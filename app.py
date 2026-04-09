"""
app.py
------
Gradio web interface for the Beauty Brand Image Agent.
Run with: python app.py

The agent enhances your prompts and generates images using MAI-Image-2.
Generated images are displayed directly in the chat interface.
"""

import os
import re

import gradio as gr
from dotenv import load_dotenv

from image_agent import create_agent

load_dotenv()

# ---------------------------------------------------------------------------
# Create a single agent and session shared across the UI
# ---------------------------------------------------------------------------
_agent = create_agent()
_session = _agent.create_session()


# ---------------------------------------------------------------------------
# Chat function called by Gradio on each message
# ---------------------------------------------------------------------------
async def chat(message: str, history: list) -> list:
    """
    Handle a user message and return a list of assistant responses.
    Each response is either a text string or an image.
    """
    result = await _agent.run(message, session=_session)
    result_text = str(result)

    # Extract image path from the agent's response using regex
    image_path = None
    match = re.search(r"output[/\\][\w\-]+\.png", result_text)
    if match:
        image_path = match.group(0)

    responses = []
    responses.append({"role": "assistant", "content": result_text})

    if image_path and os.path.exists(image_path):
        responses.append({"role": "assistant", "content": gr.Image(value=image_path)})

    return responses


# ---------------------------------------------------------------------------
# Gradio UI
# ---------------------------------------------------------------------------
with gr.Blocks(title="Beauty Brand Image Agent") as demo:
    gr.Markdown("""
    # ✨ Beauty Brand Image Agent
    **Powered by Microsoft Agent Framework + MAI-Image-2**

    Describe a product shot, lifestyle image, or campaign visual.
    The agent will enhance your prompt and generate a professional image.
    """)

    chatbot = gr.Chatbot(
        height=600,
        placeholder="<strong>Beauty Brand Image Agent</strong><br>Describe an image and I'll generate it for you.",
    )

    gr.ChatInterface(
        fn=chat,
        chatbot=chatbot,
        examples=[
            {"text": "a shampoo bottle on a marble surface with soft studio lighting"},
            {"text": "flat lay of premium hair styling products on a white surface"},
            {"text": "close-up of a hair serum bottle with gold accents, dark background"},
        ],
    )

if __name__ == "__main__":
    demo.launch()