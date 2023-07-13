from assertpy import assert_that

from geospatial_agent.shared.utils import extract_code, ExtractionException


def test_extract_code_works_with_python_markdown_blocks():
    # Get code of method_for_code using inspect.getsource
    method_code = """
def method_for_code():
pass
    """
    python_block_code = f'```python\n{method_code}\n```'
    extracted_code = extract_code(python_block_code)
    assert_that(extracted_code.strip()).is_equal_to(method_code.strip())


def test_extract_code_raise_exception_when_code_is_not_in_markdown_block():
    python_block_code = 'some code'
    assert_that(extract_code).raises(ExtractionException).when_called_with(python_block_code)
