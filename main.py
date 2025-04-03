# Note: Replace **<YOUR_APPLICATION_TOKEN>** with your actual Application token
import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()


BASE_API_URL = "https://api.langflow.astra.datastax.com"
LANGFLOW_ID = "1688a4a2-e9a3-4f74-8dd7-1065e5bb6226"
FLOW_ID = "93eae292-fa60-4393-bbbf-c4b1aa4311f2"
APPLICATION_TOKEN = os.environ.get('APP_TOKEN')
ENDPOINT = "customer"  # The endpoint name of the flow

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []


def run_flow(message: str) -> dict:
    api_url = f"{BASE_API_URL}/lf/{LANGFLOW_ID}/api/v1/run/{ENDPOINT}"

    payload = {
        "input_value": message,
        "output_type": "chat",
        "input_type": "chat",
    }

    headers = {"Authorization": "Bearer " +
               APPLICATION_TOKEN, "Content-Type": "application/json"}
    try:
        response = requests.post(
            api_url, json=payload, headers=headers, timeout=60)
        response.raise_for_status()  # Raise exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API Error: {str(e)}")
        return {"error": str(e)}


def extract_bot_message(response: dict) -> str:
    """Extract the bot's message from the response JSON."""
    try:
        return response['outputs'][0]['outputs'][0]['results']['message']['data']['text']
    except (KeyError, IndexError) as e:
        st.error(f"Couldn't parse response: {e}")
        if "error" in response:
            return f"Error: {response['error']}"
        return "Sorry, I couldn't process your request properly."


def display_chat_history():
    """Display the chat history with proper formatting."""
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]

        if role == "user":
            st.markdown(f"**You:** {content}")
        else:
            st.markdown(f"**Bot:** {content}")


def main():
    st.title("💬 LangFlow Chatbot")
    st.subheader("Ask me anything!")

    # Display chat history
    if st.session_state.chat_history:
        display_chat_history()
    with st.form(key="message_form", clear_on_submit=True):
        user_input = st.text_area(
            "Message", placeholder="Type your message here", height=100)
        submit_button = st.form_submit_button("Send")

    if submit_button and user_input.strip():
        # Add user message to chat history
        st.session_state.chat_history.append(
            {"role": "user", "content": user_input})

        try:
            with st.spinner("Processing..."):
                response = run_flow(user_input)

            bot_message = extract_bot_message(response)

            # Add bot message to chat history
            st.session_state.chat_history.append(
                {"role": "assistant", "content": bot_message})
            st.rerun()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    if st.session_state.chat_history and st.button("Clear Chat"):
        st.session_state.chat_history = []
        st.rerun()
    # userInput = input("What do you want to ask customer care ? ")
    # try :
    #     response = run_flow(userInput)
    #     print(response['outputs'][0]['outputs'][0]['results']['message']['data']['text'])
    # except Exception as e:
    #     print(e)

if __name__ == "__main__":
    main()
