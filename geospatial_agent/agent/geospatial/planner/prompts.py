_graph_generation_instructions = """
Generate a graph, the data structure only, whose nodes are 
1. A series of consecutive steps and 
2. Framework to achieve the following goal:
"""

_graph_reply_example = r"""
```python
import networkx as nx
G = nx.DiGraph()
# Add nodes and edges for the graph
# Load covid 19 shapefile from remote source
G.add_node("covid_19_shp_url", node_type="data", data_path="https://genai-chatbotstack.s3.amazonaws.com/data/covid_19_shapefile.zip", description="Covid 19 shapefile URL")
G.add_node("load_covid_19_shp", node_type="operation", description="Load Covid 19 shapefile")
G.add_edge("covid_19_shp_url", "load_covid_19_shp")
G.add_node("covid_19_gdf", node_type="data", description="Covid 19 shapefile GeoDataFrame")
G.add_edge("load_covid_19_shp", "covid_19_gdf")
...
```
"""

_graph_requirement_list = [
    "Create a single NetworkX graph instance. Graph in NetworkX will represent steps and data.",
    "No disconnected components are allowed.",
    "There are two types of nodes: operation node and data node.",
    "A data node is always followed by an operation node. An operation node is always followed by a data node."
    "Operation node accepts data nodes as parameters and writes data nodes as outputs to next operation",
    "Input of an Operation node is the data node output of previous operations, except for data loading or collection.",
    "First operations are data loading or collection, and the last operation output is the final answer.",
    "Use goepandas for spatial data if the goal is to make a map or visualization.",
    "Succinctly name all nodes.",
    "Produce the most concise graph possible.",
    "Nodes should have these attributes: node_type (data or operation), data_path (only for data node), operation_type (only for operation node), and description.",
    "operation_type is a single word tag to categorize the operations. For example, visualization, map, plot, load, transform, and spatial_join.",
    "Do not generate code to implement the steps.",
    "Only use the provided data. Use external, only from Github if needed.",
    "Only use columns or attributes noted in Data locations section. Do NOT assume attributes or columns."
    "Put your reply into a Python code block enclosed by ```python and ```."
]

_planning_graph_task_prompt_template = r"""
{human_role}:
Your Role: {planner_role_intro}
Your task: 
{graph_generation_instructions} {task_definition}


Your reply needs to meet these requirements:
{graph_requirements}


Your reply example:
{graph_reply_example}


Data locations (each data is a node):
{data_locations_instructions}

{assistant_role}:
"""

_task_name_generation_prompt = r"""
{human_role}: Create an appropriate unix folder name from the following task definition below:

1. Do not use spaces.
2. Do not use slashes or any escape characters.
3. Use underscore (_) to connect multiple worlds if necessary.
4. Produce a all lowercase, concise and meaningful name.
5. Only return the folder name.

The task definition is:
{task_definition}

{assistant_role}:
"""
