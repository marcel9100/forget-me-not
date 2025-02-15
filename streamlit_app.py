import streamlit as st
import pandas as pd
import json

from openai import OpenAI
from pydantic import BaseModel

# Optional: Set page config for a nicer look and a custom page title/icon
st.set_page_config(
    page_title="forget me not",
    page_icon="🌸",
    layout="centered"
)

# -----------------------------------------------------------------------------
# 1. Basic Styling with CSS (optional)
# -----------------------------------------------------------------------------
st.markdown(
    """
    <style>
    /* Make sidebar have a subtle gradient background */
    [data-testid="stSidebar"] {
        background: linear-gradient(#fdf9ff, #e6f7f7);
    }
    
    /* Style main title */
    .main .block-container {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 8px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }
    
    /* Optional: Tweak fonts */
    h1, h2, h3 {
        font-family: "Segoe UI", sans-serif;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------------------------------------------------------
# 2. Create Sidebar with Radio Buttons as "Tabs"
# -----------------------------------------------------------------------------
tab = st.sidebar.radio("Navigation", ["Capture", "Retrieve"])

if "people_df" not in st.session_state:
    st.session_state.people_df = pd.DataFrame(
        columns=["Name", "last_recommendation", "other_interesting_items", "analysis_json"]
    )

if "audio_file" not in st.session_state:
    st.session_state.audio_file = None

# -----------------------------------------------------------------------------
# 3. If user chooses the first tab: show the existing content
# -----------------------------------------------------------------------------
if tab == "Capture":
    
    # -- Title (moved inside the "Main" tab)
    st.title("Forget Me Not")
    st.write(
        "Tired of forgetting names as you meet new people?\n"
        "Never remember the last interactions?\n"
        "Time to remember... **Forget me not!**"
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
        client = OpenAI(api_key =st.session_state["openai_api_key"])
        

    # -------------------------------------------------------------------------
    # 3.2 Session State for DataFrame
    # -------------------------------------------------------------------------
    # if "people_df" not in st.session_state:
    #     st.session_state.people_df = pd.DataFrame(
    #         columns=["Name", "last_recommendation", "other_interesting_items", "analysis_json"]
    #     )

    # -------------------------------------------------------------------------
    # 3.3 Model for content formatting (not strictly needed, but nice for structure)
    # -------------------------------------------------------------------------
    class ContentFormat(BaseModel):
        name: str
        last_recommendation: str
        other_interesting_items: str

    # -------------------------------------------------------------------------
    # 3.4 People class for processing
    # -------------------------------------------------------------------------
    class People:
        @staticmethod
        def process_audio_and_add_row(audio_bytes: bytes):
            if not client:
                st.error("Please enter a valid OpenAI API Key first.")
                return

            # 1) Transcribe the audio
            with st.spinner("Transcribing audio..."):
                transcript_response = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_bytes  # file-like object
                )
                transcript_text = transcript_response.text
            
            st.write("**Transcript raw response:**", transcript_response)
            
            # 2) Analyze text and extract relevant fields
            with st.spinner("Analyzing text..."):
                analysis_response = client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that extracts information from text."},
                        {
                            "role": "user",
                            "content": f"""Please extract the following fields as JSON:
                            - Name
                            - last_recommendation
                            - other_interesting_items

                            Text: {transcript_text}
                            """
                        }
                    ]
                )
                analysis_json_str = analysis_response.choices[0].message.content
                st.write("**Analysis raw JSON string:**", analysis_json_str)
                
                try:
                    analysis_json = json.loads(analysis_json_str)
                except json.JSONDecodeError:
                    st.error("Could not parse JSON from the analysis. Check the response format.")
                    analysis_json = {
                        "Name": "",
                        "last_recommendation": "",
                        "other_interesting_items": ""
                    }

            # 3) Add to DataFrame
            new_row = {
                "Name": analysis_json.get("Name", ""),
                "last_recommendation": analysis_json.get("last_recommendation", ""),
                "other_interesting_items": analysis_json.get("other_interesting_items", ""),
                "analysis_json": analysis_json,
            }
            st.session_state.people_df = st.session_state.people_df._append(new_row, ignore_index=True)

    # -------------------------------------------------------------------------
    # 3.5 UI for uploading/recording audio
    # -------------------------------------------------------------------------
    #audio_value = st.file_uploader("Upload or record a voice message", type=["wav", "mp3", "m4a"])
    
    audio_value = st.audio_input("Upload or record a voice message")


    # If we have an audio file, display it
    if audio_value is not None:
        audio_file = st.audio(audio_value.read())

        if st.button("Process Audio"):
            People.process_audio_and_add_row(audio_value)
            st.success("Audio processed and added to DataFrame!")

    # -------------------------------------------------------------------------
    # 3.6 Display the DataFrame
    # -------------------------------------------------------------------------
    st.write("### Current DataFrame")
    st.dataframe(st.session_state.people_df)

    if st.button("Clear All"):
        audio_value = None
        
# -----------------------------------------------------------------------------
# 4. The second tab content (placeholder)
# -----------------------------------------------------------------------------
elif tab == "Retrieve":
    st.title("Forget Me Not")
    # st.write(
    #     """
    #     **forget me not** helps you remember important details about the people you meet,
    #     powered by OpenAI's Whisper (for transcription) and GPT (for text analysis).
        
    #     \n\n
    #     - **Tab 1 (Main):** Record or upload audio, process it, and see extracted info.
    #     - **Tab 2 (About):** Learn more about this project or add more details here.
    #     """
    # )
    
    st.write("Below is a table of all your interactions so far. You can **create, read, update, or delete** rows.")

    # -- Display an editable data editor (Streamlit >= 1.22)
    edited_df = st.data_editor(
        st.session_state.people_df,
        num_rows="dynamic",         # Allow adding new rows
        use_container_width=True,   # Expand to width of container
        key="crm_editor"
    )

    # Save changes (Update)
    if st.button("Save Changes"):
        st.session_state.people_df = edited_df
        st.success("Changes saved to DataFrame!")

    # -- Delete row(s): let user select by index
    if not st.session_state.people_df.empty:
        selected_indices = st.multiselect(
            "Select row indices to delete:",
            st.session_state.people_df.index
        )
        if st.button("Delete Selected Rows"):
            st.session_state.people_df.drop(index=selected_indices, inplace=True)
            st.session_state.people_df.reset_index(drop=True, inplace=True)
            st.success("Selected rows deleted!")

    st.write("### Current Data")
    st.dataframe(st.session_state.people_df, use_container_width=True)
