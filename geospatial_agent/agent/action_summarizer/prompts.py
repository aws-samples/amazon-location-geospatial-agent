_ROLE_INTRO = "You are a geospatial data analyzer designed to analyze data schema from arbitrary geospatial data sets."

# Action Summary #

_ACTION_SUMMARY_REQUIREMENTS = [
    "Return a JSON object with keys: action, file_paths. The action is the intended user action. The file_paths are the file paths that are extracted from the message.",
    "Rephrase user action as a complete sentence with desired user action and include it in the action key.",
    "Only return the JSON object as output. Do not add any extra text.",
    "If no file paths are found file_paths will be an empty string list.",
    "If the file path is a HTTP(S) link, use the full link as output.",
    "If the file path is not a URI, add agent:// to the beginning of the filepath.",
    "If there are multiple file paths, add all file paths in the output. Follow the rules above for each filepath.",
    "File paths are case sensitive. It can have spaces, hyphens, underscores, and periods."
]

_ACTION_SUMMARY_PROMPT = """\
{role_intro}
{human_role}: A message is provided below.
Your task is to extract the intended user action and all file paths from the message. Meet the requirements written below:

Requirements:
{requirements}


Message: {message}

{assistant_role}:
"""

# Read File #

DATA_FRAMES_VARIABLE_NAME = "dataframes"

_READ_FILE_REQUIREMENTS = [
    "Read each file using geopandas. Each file could be csv, shapefile, or GeoJSON. Otherwise, throw a ValueError.",
    "Return a list of python dictionaries with keys: file_url, resolved_file_url, data_frame, column_names.",
    "Use built-in function resolved_file_url = get_data_file_url(file_url, session_id) to get downloadable URLs. Do not add import statement for this function.",
    "Take 3 random rows with no missing values to each data_frame.",
    f"After writing the function, call the function in the end and store the list of data_frame in a global variable named {DATA_FRAMES_VARIABLE_NAME}.",
    "Do not use any try except block.",
    "Put your reply into a Python code block(enclosed by ```python and ```) without any extra surrounding text.",
    "Use pandas, geopandas, numpy, and builtins to solve the problem. Do not use any external data sources or libraries."
]

_READ_FILE_PROMPT = """\
{role_intro}
{human_role}: You are provided a set of file URLs. You need to generate a Python function that meets the following requirements:

Requirements:
{requirements}

Session Id: {session_id}
Storage Mode: {storage_mode}

File Urls:
{file_urls}

As
{assistant_role}:
"""

# Generate Data Summary #

_DATA_SUMMARY_REQUIREMENTS = [
    "The summary should be at maximum two sentences.",
    "The first sentence should be summary of the data in the table from the aspect of the user action.",
    "If there is no geometry column in the table, the second sentence should note column names that can be used to generate a geometry column in geopandas.",
    "Write summary without any extra surrounding text."
]

_DATA_SUMMARY_PROMPT = """\
{role_intro}
{human_role}: You are provided with a table with some rows data. Your task is to generate a summary that describes the data in the table following the requirements below:

Requirements:
{requirements}

Intended user action: {action}

The table has following columns:
{columns}

Table:
{table}


{assistant_role}:
"""
