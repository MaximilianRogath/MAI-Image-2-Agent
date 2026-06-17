# MAI-Image-2 Agent 

A minimal example showing how to build an interactive image generation agent using the **Microsoft Agent Framework** and **MAI-Image-2** — a Microsoft text-to-image model available in Microsoft Foundry.

The agent automatically enhances your simple descriptions into detailed prompts before generating images, and maintains conversation context so you can iteratively refine results. A Gradio web interface lets you interact with the agent directly in the browser.

## What this project demonstrates

- **Creating an agent** with `FoundryChatClient` and `Agent(client=..., instructions=...)`
- **Registering a tool** with the `@tool` decorator — imported directly from `agent_framework`
- **MAI-Image-2 integration** — calling a Microsoft text-to-image model as an agent tool
- **Prompt enhancement** — the agent improves your simple input into a detailed image prompt
- **Multi-turn conversation** with `agent.create_session()` and `InMemoryHistoryProvider`
- **Gradio web interface** — chat UI with inline image display via `app.py`
- **Keyless authentication** via `DefaultAzureCredential` — no API keys required, works seamlessly after `az login`

## Project structure

```
├── image_agent.py      # Agent with generate_image tool (also runs as CLI)
├── app.py              # Gradio web interface
├── output/             # Generated images are saved here (auto-created)
├── requirements.txt    # Python dependencies
├── .env.example        # Environment variable template
├── .gitignore
└── LICENSE
```

## Prerequisites

- Python 3.11+
- [Azure CLI](https://aka.ms/installazurecli) — used for keyless authentication
- An [Azure subscription](https://azure.microsoft.com/free/)
- The following Azure resources:
  - **Azure AI Foundry** — project with a deployed `gpt-4o` model
  - **MAI-Image-2** — deployed in your Foundry resource ([deployment guide](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai))

## Setup

**1. Clone the repository and install dependencies**

```bash
git clone https://github.com/MaximilianRogath/MAI-Image-2-Agent
cd MAI-Image-2-Agent
python -m pip install -r requirements.txt
```

**2. Log in to Azure**

```bash
az login
```

**3. Configure environment variables**

```bash
cp .env.example .env
```

Open `.env` and fill in your endpoints. No API keys needed — authentication runs via Azure CLI.

**4. Start the agent**

Launch the Gradio web interface:

```bash
python app.py
```

Then open `http://localhost:7860` in your browser.

Alternatively, run the agent directly in the terminal:

```bash
python image_agent.py
```

Generated images are saved to the `output/` directory.

## Example interaction

```
You: a shampoo bottle on a marble surface
Agent: Enhanced prompt: "A photorealistic image of a sleek shampoo bottle
       placed on a luxurious white marble surface. Soft, diffused studio
       lighting creates subtle highlights on the bottle. Minimalist background
       in warm neutrals, generous negative space, premium editorial aesthetic."

       Image saved to output/image_20260409_095125.png
```

## Image constraints

As defined in the MAI-Image-2 documentation:
- Minimum: 768 × 768 pixels
- Maximum total pixels: 1,048,576 (e.g. 1024 × 1024)
- Output format: PNG

## Further reading

- [MAI-Image-2 Documentation](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/how-to/use-foundry-models-mai)
- [Microsoft Agent Framework Documentation](https://learn.microsoft.com/en-us/agent-framework/overview/)
- [Microsoft Foundry](https://ai.azure.com/)

## License

This project is licensed under the [MIT License](LICENSE).
