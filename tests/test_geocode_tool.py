import os

import boto3
from assertpy import assert_that
from botocore.stub import Stubber

from geospatial_agent.agent.geo_chat.tools.geocode_tool import geocode_tool
from geospatial_agent.shared.location import ENV_PLACE_INDEX_NAME

test_place_index = 'test_place_index'
test_query = 'test query'


def test_initializing_geocode_tool_does_not_throw_error():
    # Set env PLACE_INDEX_NAME to 'test_place_index'
    os.environ[ENV_PLACE_INDEX_NAME] = test_place_index

    tool = geocode_tool()
    assert_that(tool).is_not_none()


def test_initializing_geocode_tool_throws_error_if_place_index_env_not_set():
    # Set env PLACE_INDEX_NAME to None
    os.environ[ENV_PLACE_INDEX_NAME] = ""

    assert_that(geocode_tool).raises(Exception).when_called_with()


def test_invoking_geocode_tool_throws_no_error_if_results_returned():
    # Set env PLACE_INDEX_NAME to 'test_place_index'
    os.environ[ENV_PLACE_INDEX_NAME] = test_place_index

    # Mock boto3 client for location
    location = boto3.client('location')
    stubber = Stubber(location)
    search_place_index_for_text_response = {
        'Results': [
            {
                'Distance': 123.0,
                'Place': {
                    'Label': 'test-address-label',
                    'Geometry': {
                        'Point': [-37.71133, 144.86304]
                    },
                },
                'PlaceId': 'test-id',
                'Relevance': 123.0
            },
        ],
        'Summary': {
            'Text': 'test-summary',
            'DataSource': 'test-datasource',
        }
    }
    expected_params = {'IndexName': test_place_index, 'MaxResults': 10, 'Text': test_query}
    stubber.add_response('search_place_index_for_text', search_place_index_for_text_response, expected_params)
    stubber.activate()

    tool = geocode_tool(location_client=location, place_index_name=test_place_index)
    response = tool(test_query).strip()

    place = search_place_index_for_text_response['Results'][0]
    response_string = f"{place['Place']['Label']}: {place['Place']['Geometry']['Point']}"

    stubber.deactivate()
    assert_that(response).is_equal_to(response_string)


def test_invoking_geocode_tool_returns_no_results_observation_if_location_client_errors():
    # Set env PLACE_INDEX_NAME to 'test_place_index'
    os.environ[ENV_PLACE_INDEX_NAME] = test_place_index

    # Mock boto3 client for location
    location = boto3.client('location')
    stubber = Stubber(location)
    expected_params = {'IndexName': test_place_index, 'MaxResults': 10, 'Text': test_query}
    stubber.add_client_error(
        'search_place_index_for_text',
        service_error_code='TestServiceErrorCode',
        service_message='Test error message',
        http_status_code=500
    )
    stubber.activate()

    tool = geocode_tool(location_client=location, place_index_name=test_place_index)
    response = tool(test_query).strip()

    stubber.deactivate()
    assert_that(response).is_equal_to("Observation: The tool did not find any results.")
