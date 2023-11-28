import os

import networkx
from pydispatch import dispatcher

from geospatial_agent.agent.action_summarizer.action_summarizer import ActionSummary
from geospatial_agent.agent.geospatial.planner.planner import gen_plan_graph, gen_task_name
from geospatial_agent.agent.geospatial.solver.solver import Solver
from geospatial_agent.agent.shared import AgentSignal, EventType, SIGNAL_ASSEMBLED_CODE_EXECUTED, \
    SENDER_GEOSPATIAL_AGENT, SIGNAL_GRAPH_CODE_GENERATED, SIGNAL_TASK_NAME_GENERATED, SIGNAL_ASSEMBLED_CODE_EXECUTING, \
    execute_assembled_code
from geospatial_agent.shared.bedrock import get_claude_v2
from geospatial_agent.shared.shim import LocalStorage


class GISAgentException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class GISAgentResponse:
    def __init__(self, graph_plan_code, graph, repl_output, op_defs,
                 assembled_code, assembled_code_output, assembled_code_file_path):
        self.graph_plan_code = graph_plan_code
        self.graph = graph
        self.graph_plan_code_output = repl_output
        self.assembled_code = assembled_code
        self.op_defs = op_defs
        self.assembled_code_output = assembled_code_output
        self.assembled_code_file_path = assembled_code_file_path


class GeospatialAgent:
    """A  geospatial data scientist and a python developer agent written by Amazon Location Service."""

    _assembled_code_file_name = "assembled_code.py"

    def __init__(self, storage_mode: str):
        claude_v2 = get_claude_v2()
        self.llm = claude_v2
        self.local_storage = LocalStorage()
        self.storage_mode = storage_mode

    def invoke(self, action_summary: ActionSummary, session_id: str) -> GISAgentResponse:
        try:
            # INFO: Generating a task name from the action summary action
            task_name = gen_task_name(self.llm, action_summary.action)
            dispatcher.send(signal=SIGNAL_TASK_NAME_GENERATED,
                            sender=SENDER_GEOSPATIAL_AGENT,
                            event_data=AgentSignal(
                                event_source=SENDER_GEOSPATIAL_AGENT,
                                event_message=f"I will use task name {task_name} to gather all generated artifacts.",
                            ))

            data_locations_instructions = self._get_data_locations_instructions(action_summary)

            # INFO: Generating the graph plan to write code
            graph_plan_code = gen_plan_graph(self.llm,
                                             task_definition=action_summary.action,
                                             data_locations_instructions=data_locations_instructions)
            dispatcher.send(
                signal=SIGNAL_GRAPH_CODE_GENERATED,
                sender=SENDER_GEOSPATIAL_AGENT,
                event_data=AgentSignal(
                    event_source=SENDER_GEOSPATIAL_AGENT,
                    event_message=f'Generated plan graph code.',
                    event_type=EventType.PythonCode,
                    event_data=graph_plan_code
                ))

            # INFO: Executing the graph plan code and get the graph object and the repl output
            graph, repl_output = self._execute_plan_graph_code(graph_plan_code)
            graph_file_abs_path = self._write_local_graph_file(graph, session_id=session_id, task_name=task_name)

            solver = Solver(
                llm=self.llm,
                graph=graph,
                graph_code=graph_plan_code,
                session_id=session_id,
                storage_mode=self.storage_mode,
                task_definition=action_summary.action,
                task_name=task_name,
                data_locations_instructions=data_locations_instructions)

            op_defs = solver.solve()
            assembled_code = solver.assemble()

            dispatcher.send(signal=SIGNAL_ASSEMBLED_CODE_EXECUTING,
                            sender=SENDER_GEOSPATIAL_AGENT,
                            event_data=AgentSignal(
                                event_source=SENDER_GEOSPATIAL_AGENT,
                                event_message="Saving and executing assembled code",
                            ))

            code_file_abs_path = self._write_local_code_file(assembled_code=assembled_code, session_id=session_id,
                                                             task_name=task_name)

            code_output, _ = execute_assembled_code(assembled_code)
            if code_output is not None:
                dispatcher.send(signal=SIGNAL_ASSEMBLED_CODE_EXECUTED,
                                sender=SENDER_GEOSPATIAL_AGENT,
                                event_data=AgentSignal(
                                    event_source=SENDER_GEOSPATIAL_AGENT,
                                    event_message=code_output
                                ))

            return GISAgentResponse(
                graph_plan_code=graph_plan_code,
                graph=graph,
                repl_output=repl_output,
                op_defs=op_defs,
                assembled_code=assembled_code,
                assembled_code_output=code_output,
                assembled_code_file_path=code_file_abs_path,
            )
        except Exception as e:
            raise GISAgentException(message="Error occurred while executing the graph plan code") from e

    @staticmethod
    def _get_data_locations_instructions(action_summary):
        # Generating a string for all the data locations from action_summary
        # For each file in action_summary.file_summaries, we will generate a string of:
        # "File Location: <file_url>",
        # "Column Names: <column_names>",
        # "Summary: <file_summary>"
        # We will then join these strings with a new line character and return it.
        # We will also add a new line character at the end of the string.
        data_locations_instructions = ""
        for file_summary in action_summary.file_summaries:
            instr = ""
            instr += f"File Location: {file_summary.file_url}\n"
            instr += f"Column Names: {file_summary.column_names}\n"
            instr += f"Summary: {file_summary.file_summary}\n"
            data_locations_instructions += instr
        return data_locations_instructions

    def _write_local_graph_file(self, graph, session_id: str, task_name: str) -> str:
        graph_file_path = self.local_storage.get_generated_file_url(
            file_path="plan_graph.graphml", session_id=session_id, task_name=task_name)

        parent_dir = os.path.dirname(graph_file_path)
        if not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        networkx.write_graphml(graph, graph_file_path, named_key_ids=False)
        return os.path.abspath(graph_file_path)

    def _write_local_code_file(self, session_id: str, assembled_code: str, task_name: str):
        return self.local_storage.write_file(
            file_name=self._assembled_code_file_name,
            session_id=session_id,
            task_name=task_name,
            content=assembled_code
        )

    @staticmethod
    def _execute_plan_graph_code(graph_plan_code) -> tuple[networkx.DiGraph, str]:
        """Returns the plan graph object by executing the graph plan code."""
        output, _globals = execute_assembled_code(graph_plan_code)
        graph: networkx.DiGraph = _globals['G']
        return graph, output
