import pandas
import pytest
from assertpy import assert_that
from langchain.llms import FakeListLLM
from pydantic import ValidationError

from geospatial_agent.agent.action_summarizer.action_summarizer \
    import ActionContext, ActionSummarizer, FileSummary
from geospatial_agent.agent.action_summarizer.prompts import DATA_FRAMES_VARIABLE_NAME


def test_initializing_action_summarizer_does_not_raise_exception():
    action_summarizer = ActionSummarizer()
    assert_that(action_summarizer).is_not_none()


def test_action_context_extraction_from_llm_response_does_not_raise_exception():
    user_input = "Build me a heatmap. I have uploaded data.csv"
    expected_action_context = ActionContext(action="Build me a heatmap", file_paths=["agent://data.csv"])
    responses = [expected_action_context.json()]

    # Creating a Fake LLM for mocking responses.
    fake_llm = FakeListLLM(responses=responses)
    action_summarizer = ActionSummarizer(llm=fake_llm)

    context = action_summarizer._extract_action_context(user_input=user_input)
    assert_that(context).is_equal_to(expected_action_context)


def test_action_context_extraction_from_llm_response_raise_exception_if_action_is_missing():
    user_input = "Build me a heatmap. I have uploaded data.csv"
    expected_action_context = ActionContext.construct(
        ActionContext.__fields_set__, action=None, file_paths=["agent://data.csv"])
    responses = [expected_action_context.json()]

    # Creating a Fake LLM for mocking responses.
    fake_llm = FakeListLLM(responses=responses)
    action_summarizer = ActionSummarizer(llm=fake_llm)

    with pytest.raises(ValidationError) as exec_info:
        action_summarizer._extract_action_context(user_input=user_input)

    assert_that(exec_info.value.raw_errors).is_length(1)
    assert_that(exec_info.value.raw_errors[0]._loc).is_equal_to('action')
    assert_that(exec_info.value.__str__()).contains('none is not an allowed value')


def test_action_context_extraction_from_llm_response_raise_exception_if_file_paths_is_missing():
    user_input = "Build me a heatmap. I have uploaded data.csv"
    expected_action_context = ActionContext.construct(
        ActionContext.__fields_set__, action="Build me a heatmap", file_paths=None)
    responses = [expected_action_context.json()]

    # Creating a Fake LLM for mocking responses.
    fake_llm = FakeListLLM(responses=responses)
    action_summarizer = ActionSummarizer(llm=fake_llm)

    with pytest.raises(ValidationError) as exec_info:
        action_summarizer._extract_action_context(user_input=user_input)

    assert_that(exec_info.value.raw_errors).is_length(1)
    assert_that(exec_info.value.raw_errors[0]._loc).is_equal_to('file_paths')
    assert_that(exec_info.value.__str__()).contains('none is not an allowed value')


def test_generating_file_reading_code_does_not_raise_exception():
    expected_action_context = ActionContext(action="Build me a heatmap", file_paths=["agent://data.csv"])
    responses = ["```python var something = 'something'\n```"]
    fake_llm = FakeListLLM(responses=responses)
    action_summarizer = ActionSummarizer(llm=fake_llm)

    action_summarizer._gen_file_read_code(
        action_context=expected_action_context, session_id="session_id", storage_mode='test_storage_mode')


def test_generating_file_summary_for_action_does_not_raise_exception():
    action = "Build me a heatmap"
    file_summaries = [FileSummary(
        file_url="agent://data.csv",
        data_frame=pandas.DataFrame(data=[[1, 2, 3], [4, 5, 6]]),
        column_names=["a", "b", "c"]
    )]

    test_file_summary = "test file summary"
    responses = [test_file_summary]
    fake_llm = FakeListLLM(responses=responses)

    action_summarizer = ActionSummarizer(llm=fake_llm)
    file_summaries = action_summarizer._gen_file_summaries_for_action(action=action, file_summaries=file_summaries)

    assert_that(file_summaries).is_length(1)
    assert_that(file_summaries[0].file_summary).is_equal_to(test_file_summary)


def test_generating_file_summaries_from_executing_code_does_not_raise_exception():
    expected_file_summaries = [FileSummary(
        file_url="agent://data.csv",
        data_frame=pandas.DataFrame(data=[[1, 2, 3], [4, 5, 6]]),
        column_names=["a", "b", "c"]
    )]

    code = f"""
import pandas
from geospatial_agent.agent.action_summarizer.action_summarizer import  FileSummary

def test_code():
    file_summaries = [FileSummary(
        file_url="agent://data.csv",
        data_frame=pandas.DataFrame(data=[[1, 2, 3], [4, 5, 6]]),
        column_names=["a", "b", "c"]
    ).dict()]
    return file_summaries

{DATA_FRAMES_VARIABLE_NAME} = test_code()
    """

    file_summaries = ActionSummarizer._gen_file_summaries_from_executing_code(code=code)
    assert_that(file_summaries).is_length(len(expected_file_summaries))
    assert_that(file_summaries[0].file_url).is_equal_to(expected_file_summaries[0].file_url)
    assert_that(file_summaries[0].data_frame.equals(expected_file_summaries[0].data_frame)).is_true()
    assert_that(file_summaries[0].column_names).is_equal_to(expected_file_summaries[0].column_names)


def test_invoking_action_summarizer_does_not_raise_exception():
    user_input = "Build me a heatmap. I have uploaded data.csv"
    session_id = "session_id"

    code = f"""
```python
import pandas
from geospatial_agent.agent.action_summarizer.action_summarizer import  FileSummary

def test_code():
    file_summaries = [FileSummary(
        file_url="agent://data.csv",
        data_frame=pandas.DataFrame(data=[[1, 2, 3], [4, 5, 6]]),
        column_names=["a", "b", "c"]
    ).dict()]
    return file_summaries

{DATA_FRAMES_VARIABLE_NAME} = test_code()
```"""
    test_file_summary = "test file summary"

    expected_action_context = ActionContext(action="Build me a heatmap", file_paths=["agent://data.csv"])
    responses = [expected_action_context.json(), code, test_file_summary]
    fake_llm = FakeListLLM(responses=responses)

    action_summarizer = ActionSummarizer(llm=fake_llm)
    action_summary = action_summarizer.invoke(user_input=user_input, session_id=session_id,
                                              storage_mode='test_storage_mode')
