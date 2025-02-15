import streamlit as st

st.title("🎈 Forget Me Not")
st.write(
    "Tired of forgetting names as you meet new people? \
      Never remember the last interactions? Time to remember... Forget me not"
)

audio_value = st.audio_input("Record a voice message")

if audio_value:
    st.audio(audio_value)