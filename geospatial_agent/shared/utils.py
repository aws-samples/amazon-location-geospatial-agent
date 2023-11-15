import re

import networkx
from pydot import Dot


class ExtractionException(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def extract_content_xml(tag: str, response: str) -> str:
    pattern = f"<{tag}>(.*?)<\/{tag}>"
    match = re.search(pattern, response, re.DOTALL)
    if match:
        return match.group(1).strip()
    else:
        raise ExtractionException(f"Failed to extract {tag} from response")


def extract_code(response):
    """Extract python code from LLM response."""

    python_code_match = re.search(r"```(?:python)?(.*?)```", response, re.DOTALL)
    if python_code_match:
        python_code = python_code_match.group(1).strip()
        return python_code
    else:
        raise ExtractionException("Failed to extract python code from response")


def get_dot_graph(graph: networkx.DiGraph) -> Dot:
    """Returns a  dot graph using pydot from a networkx graph"""
    graph_dot: Dot = networkx.drawing.nx_pydot.to_pydot(graph)
    return graph_dot


def get_exception_messages(ex: Exception) -> str:
    msg = ""
    while ex:
        msg += ex.__str__() + "\n"
        ex = ex.__cause__
    return msg
