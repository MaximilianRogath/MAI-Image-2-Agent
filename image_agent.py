"""
image_agent.py
--------------
Image generation agent built on the Microsoft Agent Framework.
Uses MAI-Image-2 (Microsoft Foundry) to generate images from natural language.
The agent automatically enhances simple prompts into detailed image descriptions
before calling the MAI-Image-2 API.

Usage:
    python image_agent.py
"""

import asyncio
import base64
import os
from datetime import datetime
from typing import Annotated

import requests
from agent_framework import Agent, InMemoryHistoryProvider, tool
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from dotenv import load_dotenv

load_dotenv()

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FOUNDRY_ENDPOINT = os.environ["AZURE_FOUNDRY_ENDPOINT"]
FOUNDRY_MODEL = os.environ.get("AZURE_FOUNDRY_MODEL", "gpt-4o")

MAI_ENDPOINT = os.environ["AZURE_MAI_ENDPOINT"]
MAI_DEPLOYMENT = os.environ["AZURE_MAI_IMAGE_DEPLOYMENT"]

OUTPUT_DIR = os.environ.get("IMAGE_OUTPUT_DIR", "output")

# ---------------------------------------------------------------------------
# Azure credential (shared across all Azure resources)
# DefaultAzureCredential automatically uses Azure CLI credentials when
# running locally after 'az login'. No API keys required.
# ---------------------------------------------------------------------------
_credential = DefaultAzureCredential()

_token_provider = get_bearer_token_provider(
    _credential,
    "https://cognitiveservices.azure.com/.default",
)


# ---------------------------------------------------------------------------
# Tool: generate an image using MAI-Image-2
# ---------------------------------------------------------------------------
# NOTE: approval_mode="never_require" is for development brevity.
# Use "always_require" in production for user confirmation before tool execution.
@tool(approval_mode="never_require")
def generate_image(
    prompt: Annotated[str, "A detailed description of the image to generate."],
    width: Annotated[int, "Width in pixels. Minimum 768. width × height must not exceed 1,048,576."] = 1024,
    height: Annotated[int, "Height in pixels. Minimum 768. width × height must not exceed 1,048,576."] = 1024,
) -> str:
    """
    Generate an image using MAI-Image-2 and save it to disk.
    Returns the file path of the saved image.
    Always use a rich, detailed prompt for best results.
    Width × height must not exceed 1,048,576 pixels.
    """
    url = f"{MAI_ENDPOINT}/mai/v1/images/generations"

    token = _token_provider()
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}",
    }

    payload = {
        "model": MAI_DEPLOYMENT,
        "prompt": prompt,
        "width": width,
        "height": height,
    }

    response = requests.post(url, headers=headers, json=payload, timeout=120)
    response.raise_for_status()

    result = response.json()
    image_data = [item for item in result.get("data", []) if "b64_json" in item]

    if not image_data:
        return f"Error: unexpected response format: {result}"

    # Save the image to disk
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = os.path.join(OUTPUT_DIR, f"image_{timestamp}.png")

    with open(output_path, "wb") as f:
        f.write(base64.b64decode(image_data[0]["b64_json"]))

    return f"Image saved to {output_path}"


# ---------------------------------------------------------------------------
# Agent definition
# ---------------------------------------------------------------------------
SYSTEM_INSTRUCTIONS = """
You are a professional visual content creator specializing in premium hair care
and styling product photography for a high-end beauty brand.

Your job is to generate stunning, on-brand product visuals and lifestyle imagery.

Style guidelines:
- Aesthetic: clean, sophisticated, and aspirational — think high-end editorial
- Color palette: warm neutrals, soft golds, creamy whites, and deep browns
- Lighting: soft, diffused studio lighting or warm natural light
- Composition: minimalist backgrounds, generous negative space, premium feel
- Always photorealistic, never illustrated or cartoon-like

When a user describes a visual they want:
1. Identify whether it is a product shot, lifestyle shot, or campaign visual.
2. Enhance their description into a rich, detailed prompt following the style
   guidelines above — include lighting, composition, mood, colors, and textures.
3. Call generate_image with the enhanced prompt.
4. Always show the user the enhanced prompt you used, then state the exact file path as plain text.

If the user asks to refine or adjust, incorporate their feedback and generate
a new version.

Never mention specific brand names in the prompt sent to generate_image.
Never use markdown links in your responses. Always state the file path as plain text.
Keep your responses concise and focused on the creative direction.
""".strip()


def create_agent() -> Agent:
    client = FoundryChatClient(
        project_endpoint=FOUNDRY_ENDPOINT,
        model=FOUNDRY_MODEL,
        credential=_credential,
    )

    return Agent(
        client=client,
        name="ImageAgent",
        instructions=SYSTEM_INSTRUCTIONS,
        tools=[generate_image],
        context_providers=[
            InMemoryHistoryProvider(load_messages=True),
        ],
    )


# ---------------------------------------------------------------------------
# Interactive console loop
# ---------------------------------------------------------------------------
async def run_interactive() -> None:
    print("=" * 60)
    print("  Image Agent (Microsoft Agent Framework + MAI-Image-2)")
    print("  Describe an image and I'll generate it for you.")
    print("  Type 'exit' or press Ctrl+C to quit")
    print("=" * 60)

    agent = create_agent()
    session = agent.create_session()

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Goodbye!")
            break

        result = await agent.run(user_input, session=session)
        print(f"\nAgent: {result}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(run_interactive())