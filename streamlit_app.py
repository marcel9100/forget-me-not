import streamlit as st
import pandas as pd

from openai import OpenAI
import openai



# Set your OpenAI API key (or use another method to load securely)
openai.api_key = "YOUR_OPENAI_API_KEY"

# Initialize Streamlit
st.title("🎈 Forget Me Not")
st.write(
    "Tired of forgetting names as you meet new people?\n"
    "Never remember the last interactions?\n"
    "Time to remember... Forget me not!"
)

# -----------------------------------------------------------------------------
# 1. OpenAI Key Handling
# -----------------------------------------------------------------------------
# We store the OpenAI key in session_state to remember it throughout app usage
if "openai_api_key" not in st.session_state:
    st.session_state["openai_api_key"] = ""

st.session_state["openai_api_key"] = st.text_input(
    "Enter your OpenAI API Key:", 
    type="password", 
    value=st.session_state["openai_api_key"]
)

# Set the openai.api_key if available
if st.session_state["openai_api_key"]:
    openai.api_key = st.session_state["openai_api_key"]
    #client = OpenAI()

# -----------------------------------------------------------------------------
# SESSION STATE HELPER:
# -----------------------------------------------------------------------------
# We store the DataFrame in st.session_state to persist it across runs
# (Streamlit re-runs your script every time a widget changes).
if "people_df" not in st.session_state:
    # Create an empty DataFrame with desired columns
    st.session_state.people_df = pd.DataFrame(
        columns=["Name", "last_recommendation", "other_interesting_items", "analysis_json"]
    )

# -----------------------------------------------------------------------------
# CLASS FOR MANAGING PEOPLE DATAFRAME
# -----------------------------------------------------------------------------
class People:
    @staticmethod
    def process_audio_and_add_row(audio_bytes: bytes):
        """
        1) Transcribes the audio using OpenAI (placeholder).
        2) Calls another OpenAI endpoint (or ChatCompletion) to analyze text and extract relevant fields in JSON form.
        3) Adds a new row to the DataFrame stored in session_state.
        """
        # 1) Transcribe the audio (placeholder)
        #    For example, using the Whisper API endpoint (pseudo-code):
        #
        # with st.spinner("Transcribing audio..."):
        #     transcript_response = openai.Audio.transcribe(
        #         model="whisper-1",
        #         file=audio_bytes  # This might need a file-like object
        #     )
        #     transcript_text = transcript_response["text"]
        #
        # For demonstration, let's pretend we got this transcript:
        transcript_text = "Hi, this is Alice. I recommend reading 'The Great Gatsby'."

        # 2) Analyze text and extract relevant data (placeholder)
        #    For example, using ChatCompletion with a system/prompt that instructs the model
        #    to return JSON with the fields: Name, last_recommendation, other_interesting_items
        #
        # with st.spinner("Analyzing text..."):
        #     analysis_response = openai.ChatCompletion.create(
        #         model="gpt-3.5-turbo",
        #         messages=[
        #             {"role": "system", "content": "You are a helpful assistant."},
        #             {
        #                 "role": "user",
        #                 "content": f"Extract the following fields as JSON:\n"
        #                            f"Name, last_recommendation, other_interesting_items\n"
        #                            f"Text: {transcript_text}"
        #             }
        #         ]
        #     )
        #     # Suppose it returns something like:
        #     #  {
        #     #    "Name": "Alice",
        #     #    "last_recommendation": "Reading 'The Great Gatsby'",
        #     #    "other_interesting_items": "Loves painting, hiking"
        #     #  }
        #     analysis_json = analysis_response["choices"][0]["message"]["content"]
        #
        # For demonstration, let's just create a dummy JSON result:
        analysis_json = {
            "Name": "Alice",
            "last_recommendation": "Reading 'The Great Gatsby'",
            "other_interesting_items": "Enjoys painting, hiking",
        }

        # 3) Convert the analysis into a dictionary for DataFrame
        #    We'll store the entire JSON in a column for reference
        new_row = {
            "Name": analysis_json.get("Name", ""),
            "last_recommendation": analysis_json.get("last_recommendation", ""),
            "other_interesting_items": analysis_json.get("other_interesting_items", ""),
            "analysis_json": analysis_json,
        }

        # Append to the DataFrame in session_state
        st.session_state.people_df = st.session_state.people_df._append(new_row, ignore_index=True)

# -----------------------------------------------------------------------------
# STREAMLIT UI FOR AUDIO INPUT
# -----------------------------------------------------------------------------

audio_value = st.audio_input("Upload or record a voice message")


# If we have an audio file, let's "process" it
if audio_value is not None:
    audio_file = st.audio(audio_value)
    
    if st.session_state["openai_api_key"]:
      transcription = openai.audio.transcriptions.create(
      model="whisper-1", 
      file=audio_file
      )
      st.write(transcription)

    if st.button("Process Audio"):
        People.process_audio_and_add_row(audio_value.read())
        st.success("Audio processed and added to DataFrame!")

# Display the DataFrame
st.write("### Current DataFrame")
st.dataframe(st.session_state.people_df)