from typing import Sequence

import networkx

from geospatial_agent.agent.geospatial.solver.constants import NODE_TYPE_ATTRIBUTE, NODE_TYPE_OPERATION, \
    NODE_DESCRIPTION_ATTRIBUTE, NODE_TYPE_DATA, NODE_DATA_PATH_ATTRIBUTE, NODE_TYPE_OPERATION_TYPE


class OperationNode:
    def __init__(self,
                 function_definition: str,
                 return_line: str,
                 description: str,
                 node_name: str,
                 param_names: set,
                 return_names: set,
                 operation_type: str = "",
                 code_gen_response: str = "",
                 operation_code: str = "",
                 reviewed_code: str = "",
                 operation_prompt: str = ""):
        self.function_definition = function_definition
        self.return_line = return_line
        self.description = description
        self.operation_type = operation_type
        self.node_name = node_name
        self.param_names = param_names
        self.return_names = return_names
        self.code_gen_response = code_gen_response
        self.operation_code = operation_code
        self.reviewed_code = reviewed_code
        self.operation_prompt = operation_prompt


# An exception class for OperationsParser with a message
class OperationsParserException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class OperationsParser:
    def __init__(self, graph: networkx.DiGraph):
        self.graph = graph

        # Initializing the class with all operations found in the solution graph
        self.op_node_names = self._get_operation_node_names()
        self.operation_nodes = self._get_operation_nodes(self.op_node_names)
        self.output_node_names = self._get_output_node_names()
        self.input_node_names = self._get_input_node_names()

    def get_ancestors(self, node_name) -> Sequence[OperationNode]:
        ancestor_node_names = networkx.ancestors(self.graph, node_name)

        ancestor_operation_names = []
        for node_name in ancestor_node_names:
            if node_name in self.op_node_names:
                ancestor_operation_names.append(node_name)

        ancestor_operation_functions = []
        for op_node in self.operation_nodes:
            op_node_name = op_node.node_name
            if op_node_name in ancestor_operation_names:
                ancestor_operation_functions.append(op_node)

        return ancestor_operation_functions

    def get_descendants(self, node_name) -> Sequence[OperationNode]:
        descendant_operation_names = []
        descendant_node_names = networkx.descendants(self.graph, node_name)

        for descendant in descendant_node_names:
            if descendant in self.op_node_names:
                descendant_operation_names.append(descendant)

        descendant_operation_nodes = []
        for op_node in self.operation_nodes:
            op_name = op_node.node_name
            if op_name in descendant_operation_names:
                descendant_operation_nodes.append(op_node)

        return descendant_operation_nodes

    def stringify_nodes(self, nodes: Sequence[OperationNode]) -> str:
        """Returns all operation nodes attributes stringified as a new line delimited string"""
        op_def_list = []
        for op_node in nodes:
            op_node_dict = op_node.__dict__
            op_def_list.append(str(op_node_dict))

        defs = '\n'.join(op_def_list)
        return defs

    def _get_operation_nodes(self, op_node_names) -> Sequence[OperationNode]:
        op_nodes = []
        for op in op_node_names:
            node_dict = self.graph.nodes[op]

            node_type = node_dict[NODE_TYPE_ATTRIBUTE]
            if node_type != NODE_TYPE_OPERATION:
                raise OperationsParserException(f"Node {op} is not an operation node")

            function_def, param_names = self._get_func_def_str(op)

            successors = list(self.graph.successors(op))
            return_str = 'return ' + ', '.join(successors)

            op_node = OperationNode(
                function_definition=function_def,
                return_line=return_str,
                description=node_dict[NODE_DESCRIPTION_ATTRIBUTE],
                operation_type=node_dict.get(NODE_TYPE_OPERATION_TYPE, ""),
                node_name=op,
                param_names=param_names,
                return_names=set(successors)
            )

            op_nodes.append(op_node)
        return op_nodes

    def _get_operation_node_names(self):
        op_nodes = []
        for node_name in self.graph.nodes():
            node = self.graph.nodes[node_name]
            if node[NODE_TYPE_ATTRIBUTE] == NODE_TYPE_OPERATION:
                op_nodes.append(node_name)
        return op_nodes

    def _get_output_node_names(self):
        """Returns output nodes from the graph. Output nodes have 'output' attribute set to True"""
        output_nodes = []
        for node_name in self.graph.nodes():
            node = self.graph.nodes[node_name]
            if len(list(self.graph.successors(node_name))) == 0:
                if node[NODE_TYPE_ATTRIBUTE] != NODE_TYPE_DATA:
                    raise OperationsParserException(f"Node {node_name} is not an {NODE_TYPE_DATA} node")
                output_nodes.append(node_name)
        return output_nodes

    def _get_input_node_names(self):
        """Returns input nodes from the graph. Input nodes have 'input' attribute set to True"""
        input_nodes = []
        for node_name in self.graph.nodes():
            node = self.graph.nodes[node_name]
            if len(list(self.graph.predecessors(node_name))) == 0:
                if node[NODE_TYPE_ATTRIBUTE] != NODE_TYPE_DATA:
                    raise OperationsParserException(f"Node {node_name} is not an {NODE_TYPE_DATA} node")
                input_nodes.append(node_name)
        return input_nodes

    def _get_func_def_str(self, node):
        """
        Returns function definition string with function name, parameters and default values of parameters.
        """

        # INFO: To generate a function definition from the solution graph, we need to find the parameters of the
        # function, and the return value.

        # We start with looking for the predecessors of the node. Because the parameters are the predecessors.
        predecessors = self.graph.predecessors(node)

        param_default_str = ''
        param_str = ''
        param_names = set()

        for data_node in predecessors:
            param_node = self.graph.nodes[data_node]

            # Parameter node might have a data_path attribute. If it does, we need to use that.
            # For example, a URL or  file path.
            # Otherwise, we just use the node name as parameter default value.
            data_path = param_node.get(NODE_DATA_PATH_ATTRIBUTE, '')
            param_names.add(data_node)

            if data_path != "":
                param_default_str = param_default_str + f"{data_node}='{data_path}', "
            else:
                param_str = param_str + f"{data_node}, "

        all_parameters_str = param_str + param_default_str

        func_def = f'{node}({all_parameters_str})'
        func_def = func_def.replace(', )', ')')

        return func_def, param_names
