import os

import boto3

ENV_MAP_NAME = "MAP_NAME"
ENV_PLACE_INDEX_NAME = "PLACE_INDEX_NAME"


class LocationConfigurationError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


def get_location_client():
    return boto3.client("location")


def get_place_index_name():
    """Gets Place Index name from environment variable PLACE_INDEX_NAME"""
    place_index_name = os.environ.get(ENV_PLACE_INDEX_NAME)
    if not place_index_name:
        raise LocationConfigurationError(f"{ENV_PLACE_INDEX_NAME} environment variable is not set")

    return place_index_name


def get_api_key() -> str:
    """Gets API Key referenced by API Key Name from environment variables."""

    api_key_arn = os.environ.get("API_KEY_NAME")
    if not api_key_arn:
        raise LocationConfigurationError("API_KEY_NAME environment variable is not set")

    try:
        location = get_location_client()
        api_key = location.describe_key(KeyName=api_key_arn)
    except Exception as e:
        raise LocationConfigurationError(f"Error getting API Key") from e

    return api_key["Key"]


def get_map_style_uri():
    """Returns map style URI inside the style JSON returned by GetMapStyleDescriptor API of Amazon Location Service"""
    map_name = os.environ.get(ENV_MAP_NAME)
    if not map_name:
        raise LocationConfigurationError("MAP_NAME environment variable is not set")

    try:
        client = get_location_client()
        op_path = f'/maps/v0/maps/{map_name}/style-descriptor'
        style_uri = f"https://maps.{client.meta.service_model.signing_name}.{client.meta.region_name}.amazonaws.com{op_path}?key={get_api_key()}"
        return style_uri
    except Exception as e:
        raise LocationConfigurationError(f"Error getting map style URI") from e
