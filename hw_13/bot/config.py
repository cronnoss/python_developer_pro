import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file in the root directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Telegram bot token (from @BotFather)
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")

# Path to LoRA adapters
MODEL_PATH = Path(__file__).parent.parent / "model" / "lora_adapters"

# Model configuration
MAX_NEW_TOKENS = 150
TEMPERATURE = 0.7
TOP_P = 0.9
REPETITION_PENALTY = 1.1

# System prompt template (matching the training format)
SYSTEM_PROMPT = """<|user|>
Answer in English. Be concise and technical.
User question: {question}
<|assistant|>"""
