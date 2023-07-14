from enum import Enum, auto
from typing import TypeVar
from datetime import datetime

from pydantic import BaseModel, Field

from uuid import uuid4

SENDER_ACTION_SUMMARIZER = "action_summarizer"
SENDER_GEOSPATIAL_AGENT = "geospatial_agent"
SENDER_GEO_CHAT_AGENT = "geo_chat_agent"

SIGNAL_ASSEMBLED_CODE_EXECUTING = "assembled_code_executing"
SIGNAL_ASSEMBLED_CODE_EXECUTED = "assembled_code_executed"
SIGNAL_GRAPH_CODE_GENERATED = "plan_graph_code_generated"
SIGNAL_TASK_NAME_GENERATED = "task_name_generated"
SIGNAL_OPERATION_CODE_GENERATED = "operation_code_generated"
SIGNAL_CODE_REVIEW_GENERATED = "operation_code_review_generated"
SIGNAL_ACTION_CONTEXT_GENERATED = "action_context_generated"
SIGNAL_FILE_READ_CODE_GENERATED = "file_read_code_generated"
SIGNAL_FILE_READ_CODE_EXECUTED = "file_read_code_executed"
SIGNAL_TAIL_CODE_GENERATED = "tail_code_generated"

SIGNAL_GEO_CHAT_INITIATED = "geo_chat_initiated"
SIGNAL_GEO_CHAT_RESPONSE_COMPLETE = "geo_chat_response_complete"

ALL_SIGNALS = [
    SIGNAL_ASSEMBLED_CODE_EXECUTING,
    SIGNAL_ASSEMBLED_CODE_EXECUTED,
    SIGNAL_GRAPH_CODE_GENERATED,
    SIGNAL_TASK_NAME_GENERATED,
    SIGNAL_OPERATION_CODE_GENERATED,
    SIGNAL_CODE_REVIEW_GENERATED,
    SIGNAL_ACTION_CONTEXT_GENERATED,
    SIGNAL_FILE_READ_CODE_GENERATED,
    SIGNAL_FILE_READ_CODE_EXECUTED,
    SIGNAL_TAIL_CODE_GENERATED,
    SIGNAL_GEO_CHAT_INITIATED,
    SIGNAL_GEO_CHAT_RESPONSE_COMPLETE
]


# enum for event types - CodePython, Message, Error
class EventType(Enum):
    PythonCode = auto()
    Message = auto()
    Error = auto()


T = TypeVar('T')


class AgentSignal(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().__str__())
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    event_source: str = Field()
    event_message: str = Field()
    event_data: T = Field(default=None)
    event_type: EventType = Field(default=EventType.Message)
    is_final: bool = Field(default=False)
