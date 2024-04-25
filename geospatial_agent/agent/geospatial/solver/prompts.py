from geospatial_agent.shared.prompts import GIS_AGENT_ROLE_INTRO

# =============Operation Requirement Gen Section==================
operation_requirement_gen_intro = GIS_AGENT_ROLE_INTRO

shim_instructions = [
    "Always use built-in function resolved_file_url = get_data_file_url(file_url, session_id) to get downloadable URLs. Do not add import statement for this function.",
    "For any type of task, when saving any file locally, use built-in function get_local_file_path(filepath, session_id, task_name). Do not add import statement for this function.",
    "When visualizing something with pydeck,use a built-in function named location_map_style() to return map_style. Do not add import statement for this function.",
]

predefined_operation_requirements = [
    "Do not change the given variable names and paths from the graph.",
    "Write code with necessary import statements of necessary libraries. Do not add imports for built-in functions. Follow Pep8 styling.",
    'Write code into a Python code block(enclosed by ```python and ```).',
    "For visualization that requires a map, always use pydeck library unless otherwise specified.",
    "For visualization, if pydeck is used, save the pydeck deck to a HTML file.",
    "For visualization that does not require a map, use other plotting libraries such as matplotlib, and pyplot.",
    "When using GeoPandas to load a zipped shapefile from a URL, use gpd.read_file(URL). Do not download and unzip the file.",
    "When doing spatial analysis, if necessary, and if there are multiple layers ONLY, convert all involved spatial layers into the same map projection.",
    "Conduct map projection conversion only for spatial data layers defined with geopandas GeoDataFrame. Do not do map projection with pandas DataFrame",
    "While joining DataFrame and GeoDataFrame, use common columns. Do not to convert DataFrame to GeoDataFrame.",
    "When joining tables, convert the involved columns to string type without leading zeros. Convert integers to floats if necessary.",
    "Show units for graphs or maps.",
    "When doing spatial joins, retain at least 1 geometry column",
    "While using GeoPandas for spatial joining, remind the arguements. The arguments are: geopandas.sjoin(left_df, right_df, how='inner', predicate='intersects', lsuffix='left', rsuffix='right', **kwargs)",
    "Do not to write a main function with 'if __name__ == '__main__:'",
    "Only a single python function is to be written in this task. Do not write tests or a main function.",
    "Use the built-in functions or attribute. Do not to make up fake built-in functions.",
    "Do not to use any library or package that is not necessary for the task.",
    "Do not to use try except block without re-throwing the exception.",
    "Point function requires importing shapely library."
]

operation_requirement_gen_task_prefix = r"""
{human_role}:
Your role: {operation_req_gen_intro}

The function to write requirements for: {operation_name}.

The function that we need requirements for has the following properties:
{operation_properties}

These are the pre-written requirements:
{pre_requirements}

Your task is to respond with a JSON string array of requirements.
1. Pick requirements from the pre-written requirements that are relevant for the current function.
2. Never re-phrase the requirements from the pre-written requirements.
3. Do not add your own specific requirements unless it is a corner case.
4. Maximum number of requirements is 20.
5. Write the python array into a xml block, enclosed by <json> and </json>.


{assistant_role}:
"""

# =============Operation Code Gen Section==================
operation_code_gen_intro = GIS_AGENT_ROLE_INTRO
operation_task_prefix = r'You need to generate a Python function to do: '

operation_reply_example = """
```python'
import pandas as pd

def Load_csv(csv_url="https://someurl.amazonaws.com/dd87ba06-242c-4a15-9e8d-5bfde1947077/data/data.csv"):
    # Description: Load a CSV file from a given URL
    # csv_url: CSV file URL
    # Get downloadable url from csv_url
    file_url = get_data_file_url(file_url, session_id)
    tract_population_df = pd.read_csv(tract_population_csv_url)
    return tract_population_df
```
"""

operation_pydeck_example = """
import pydeck as pdk

def generate_heatmap(airbnb_gdf):
    # Generate heatmap using pydeck
    airbnb_heatmap = pdk.Deck(
        map_style=location_map_style(),
        initial_view_state=pdk.ViewState(
            latitude=airbnb_gdf['latitude'].mean(),
            longitude=airbnb_gdf['longitude'].mean(),
            zoom=11,
            pitch=50,
        ),
        layers=[
            pdk.Layer(
                'HexagonLayer',
                data=airbnb_gdf,
                get_position=['longitude', 'latitude'],
                radius=100,
                elevation_scale=4,
                elevation_range=[0, 1000],
                pickable=True,
                extruded=True,
            ),
            pdk.Layer(
                'ScatterplotLayer',
                data=airbnb_gdf,
                get_position=['longitude', 'latitude'],
                get_color='[200, 30, 0, 160]',
                get_radius=200,
            ),
        ],
    )

    # Save heatmap HTML
    airbnb_heatmap.to_html(get_local_file_path('airbnb_heatmap.html', session_id, task_name))
    return airbnb_heatmap
"""

operation_code_gen_prompt_template = """
{human_role}:
Your role: {operation_code_gen_intro}

Operation_task: {operation_task_prefix} {operation_description}

This function is one step to solve the question/task: {task_definition}

Your reply needs to meet these requirements: {operation_requirements}

Data locations: {data_locations_instructions}
Session Id: {session_id}
Task Name: {task_name}
Storage Mode: {storage_mode}

Your reply example: {operation_reply_example}

Pydeck usage example:
{operation_pydeck_example}

This function is a operation node in a solution graph for the question/task, the Python code to build the graph is:
{graph_code}

The ancestor function code is below. Follow the generated file names and attribute names:
{ancestor_operation_code}

The descendant function (if any) definitions for the question are (node_name is function name):
{descendant_operations_definition}


{assistant_role}:
"""
