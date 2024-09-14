import streamlit as st
import requests
import time

# Set the page configuration to include the title in the browser tab
st.set_page_config(page_title="Yoga Companion Chat", layout="centered")

# Remove the Streamlit footer but keep the hamburger menu
hide_streamlit_style = """
    <style>
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .css-18ni7ap.e8zbici2 {
        display: none;
    }
    .user-message {
        text-align: right;
        color: white;
        background-color: #1a73e8;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 10px;
        margin-left: auto;
        width: fit-content;
        max-width: 70%;
    }
    .bot-message {
        text-align: left;
        color: black;
        background-color: #f1f1f1;
        padding: 10px;
        border-radius: 15px;
        margin-bottom: 10px;
        margin-right: auto;
        width: fit-content;
        max-width: 70%;
    }
    .user-label {
        font-weight: bold;
        text-align: right;
        margin-bottom: 5px;
        margin-left: auto;
        width: fit-content;
    }
    .bot-label {
        font-weight: bold;
        text-align: left;
        margin-bottom: 5px;
        margin-right: auto;
        width: fit-content;
    }
    .feedback-container {
        text-align: center;
        margin-top: 10px;
    }
    .button-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .feedback-button {
        background-color: #ff7f50;
        color: white;
        border: none;
        padding: 10px;
        border-radius: 5px;
        cursor: pointer;
        margin-top: 20px;
    }
    .feedback-popup {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        margin-top: 10px;
    }
    .app-title {
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 20px;
    }
    </style>
    """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# Display and center the app title
st.markdown("<div class='app-title'>Yoga Companion Chat</div>", unsafe_allow_html=True)

# Initialize session state for storing chat history and feedback
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "conversation_id" not in st.session_state:
    st.session_state.conversation_id = None
if "show_feedback" not in st.session_state:
    st.session_state.show_feedback = False
if "feedback_given" not in st.session_state:
    st.session_state.feedback_given = False
if "conversation_had" not in st.session_state:
    st.session_state.conversation_had = False

# Form to handle Enter key submission
with st.form(key='message_form', clear_on_submit=True):
    user_input = st.text_input("You:", key="user_input")
    submitted = st.form_submit_button("Send")

# Check if a conversation has occurred
if submitted and user_input:
    # Store the user message in session state
    st.session_state.chat_history.append({"user": user_input})
    st.session_state.conversation_had = True

    # Send the question to the Flask API
    response = requests.post(
        "http://localhost:5000/question", 
        json={"question": user_input}
    )
    
    # Check if the request was successful
    if response.status_code == 200:
        answer_data = response.json()
        st.session_state.chat_history.append({"bot": answer_data["answer"]})
        st.session_state.conversation_id = answer_data["conversation_id"]
        st.session_state.feedback_given = False
    else:
        st.session_state.chat_history.append({"bot": "Failed to get an answer. Please try again."})

# Only show the last message from the user and the bot, with the user message above the bot message
if st.session_state.chat_history:
    last_user_message = next((msg['user'] for msg in reversed(st.session_state.chat_history) if 'user' in msg), None)
    last_bot_message = next((msg['bot'] for msg in reversed(st.session_state.chat_history) if 'bot' in msg), None)
    
    if last_user_message:
        st.markdown(f"<div class='user-label'>User:</div><div class='user-message'>{last_user_message}</div>", unsafe_allow_html=True)
    if last_bot_message:
        st.markdown(f"<div class='bot-label'>Yoga Bot:</div><div class='bot-message'>{last_bot_message}</div>", unsafe_allow_html=True)

# Reposition the feedback button below the chat and show it only if feedback hasn't been given
if st.session_state.conversation_had and not st.session_state.feedback_given:
    if st.button("Provide Feedback", key="feedback_button", help="Click to provide feedback"):
        st.session_state.show_feedback = True

# Always show the feedback options but hide the button if feedback is given
if st.session_state.show_feedback and not st.session_state.feedback_given:
    with st.container():
        st.markdown("### Provide Feedback", unsafe_allow_html=True)
        
        # Track the user selection
        feedback_option = st.radio(
            "Was the answer helpful?", 
            (1, -1), 
            index=0, 
            key="feedback_option"
        )
        
        if st.button("Submit Feedback"):
            # Use the selected value from the radio button directly
            feedback_response = requests.post(
                "http://localhost:5000/feedback", 
                json={"conversation_id": st.session_state.conversation_id, "feedback": feedback_option}
            )
            if feedback_response.status_code == 200:
                st.success("Feedback submitted successfully!")
                st.session_state.feedback_given = True
                st.session_state.show_feedback = False  # Hide the feedback button after submission
            else:
                st.error("Failed to submit feedback. Please try again.")
