import click
import langchain
from pydispatch import dispatcher
from pygments import highlight
from pygments.formatters.terminal import TerminalFormatter
from pygments.lexers.python import PythonLexer

from geospatial_agent.agent.geo_chat.chat_agent import GeoChatAgent
from geospatial_agent.agent.shared import ALL_SIGNALS, AgentSignal, EventType
from geospatial_agent.shared.shim import LOCAL_STORAGE_MODE, LocalStorage

import uuid

from geospatial_agent.shared.utils import get_exception_messages

from dotenv import load_dotenv

langchain.verbose = False

load_dotenv()


def set_langchain_verbose(is_verbose: bool):
    langchain.verbose = is_verbose


def get_chatbot_response(user_input: str, session_id: str, verbose: bool, storage_mode: str):
    try:
        set_langchain_verbose(verbose)

        geo_chat_agent = GeoChatAgent()
        response = geo_chat_agent.invoke(agent_input=user_input, storage_mode=storage_mode, session_id=session_id)
        return response

    except Exception as e:
        click.echo(click.style(f"An unhandled error occurred during chatbot conversation: {str(e)}", fg="red"))


@click.command()
@click.option('--verbose', is_flag=True, help='Enable verbose mode')
@click.option('--session-id', help='Session id of the conversation')
def chat(session_id: str, verbose: bool):
    """
    Simple conversational chatbot running in the terminal.
    Type your message, press Enter, and the chatbot will respond.
    Type 'exit' to quit the chatbot.
    """

    click.echo("Agent: Hi! I'm Agent Smith! Your conversational geospatial agent. How can I help you today?")

    if session_id == "" or session_id is None:
        session_id = uuid.uuid4().hex

        click.echo(f"Agent: Creating a new session {session_id}")
        storage = LocalStorage()
        storage.create_session_storage(session_id=session_id)

    def print_signal(sender, event_data):
        # Check if event_data is instance of Exception
        if isinstance(event_data, Exception):
            exception_message = get_exception_messages(event_data)
            click.echo(
                click.style(
                    f"\nAn error occurred during chatbot conversation: {str(exception_message)}\n===============\n",
                    fg="red"))

        elif isinstance(event_data, AgentSignal):
            click.echo(click.style(f"\n{sender}: \n{event_data.event_message}", fg="cyan"))
            if event_data.event_type == EventType.PythonCode:
                highlighted_code = highlight(event_data.event_data, PythonLexer(), TerminalFormatter())
                print(highlighted_code)
            click.echo(click.style("\n===============\n", fg="cyan"))

    for signal in ALL_SIGNALS:
        dispatcher.connect(receiver=print_signal, signal=signal)

    while True:
        user_input = click.prompt("You", type=str)
        if user_input.lower() == 'exit':
            click.echo("Agent: Goodbye! Have a great day!")
            break

        response = get_chatbot_response(
            user_input=user_input, session_id=session_id, verbose=verbose, storage_mode=LOCAL_STORAGE_MODE)
        if response:
            click.echo(f"Agent: {response}")


def main():
    chat()


if __name__ == "__main__":
    main()
