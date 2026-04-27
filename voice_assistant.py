import os
import sys
import threading
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
AGENT_ID = os.getenv("AGENT_ID")

from elevenlabs.client import ElevenLabs
from elevenlabs.conversational_ai.conversation import Conversation
from elevenlabs.conversational_ai.default_audio_interface import DefaultAudioInterface
from elevenlabs.types import ConversationConfig

user_name = "Hussaan"
fitness_goal = "Build muscle and improve endurance"
schedule = "Push workout at 16:00; Cardio at 17:30"

prompt = (
    f"You are a personal gym assistant. "
    f"Your client is {user_name}, whose fitness goal is: {fitness_goal}. "
    f"Their schedule today is: {schedule}. "
    f"Provide workout tips, track progress, and answer gym-related questions."
)

first_message = f"Hey {user_name}, ready for your workout today?"

conversation_override = {
    "agent": {
        "prompt": {"prompt": prompt},
        "first_message": first_message,
    },
}

config = ConversationConfig(
    user_id=user_name,
    conversation_config_override=conversation_override,
    extra_body={},
    dynamic_variables={
        "goal": fitness_goal,
        "schedule": schedule,
    },
)

client = ElevenLabs(api_key=API_KEY)
stop_event = threading.Event()  # ← shared signal between threads

def print_agent_response(response):
    print(f"Agent: {response}")

def print_interrupted_response(original, corrected):
    print(f"Agent interrupted, truncated response: {corrected}")

def print_user_transcript(transcript):
    print(f"User: {transcript}")
    if any(word in transcript.lower() for word in ["exit", "quit", "stop"]):
        print("Exiting assistant...")
        stop_event.set()  # signal the main thread to stop

conversation = Conversation(
    client,
    AGENT_ID,
    config=config,
    requires_auth=True,
    audio_interface=DefaultAudioInterface(),
    callback_agent_response=print_agent_response,
    callback_agent_response_correction=print_interrupted_response,
    callback_user_transcript=print_user_transcript,
)

conversation.start_session()
stop_event.wait()          # main thread blocks here until signal
conversation.end_session()
print("Session ended. Goodbye!")