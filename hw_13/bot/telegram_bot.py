"""
Telegram Bot for Linux Command Explanations
Uses fine-tuned TinyLlama with LoRA adapters on CPU
"""

import logging
import torch
import os
import gc
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
from bot.config import TELEGRAM_TOKEN, MODEL_PATH, MAX_NEW_TOKENS, TEMPERATURE, TOP_P, REPETITION_PENALTY, SYSTEM_PROMPT

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class LinuxCommandBot:
    """Telegram bot for explaining Linux commands"""

    def __init__(self):
        """Initialize the bot"""
        self.token = TELEGRAM_TOKEN
        self.model_path = str(MODEL_PATH)
        self.model = None
        self.tokenizer = None
        self.device = "cpu"
        # Optimization for Mac CPU
        os.environ["PYTORCH_ENABLE_MPS_FALLBACK"] = "1"

    def load_model(self):
        """Load base model and LoRA adapters on CPU with memory optimizations"""
        logger.info("Loading base model on CPU (bfloat16)...")
        
        try:
            # Use bfloat16 for Apple Silicon CPU - it's 2x smaller than float32
            # and better supported than float16 on CPU
            base_model = AutoModelForCausalLM.from_pretrained(
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                torch_dtype=torch.bfloat16,
                low_cpu_mem_usage=True
            ).to(self.device)

            # Load LoRA adapters
            logger.info(f"Loading LoRA adapters from {self.model_path}...")
            self.model = PeftModel.from_pretrained(base_model, self.model_path).to(self.device)

            # Load tokenizer
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_path)
            if self.tokenizer.pad_token is None:
                self.tokenizer.pad_token = self.tokenizer.eos_token

            # Set to evaluation mode
            self.model.eval()

            logger.info("Model loaded successfully in bfloat16!")

        except Exception as e:
            logger.error(f"Error loading model: {e}")
            # Fallback to float32 if bfloat16 fails
            logger.info("Attempting fallback to float32...")
            base_model = AutoModelForCausalLM.from_pretrained(
                "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
                torch_dtype=torch.float32,
                low_cpu_mem_usage=True
            ).to(self.device)
            self.model = PeftModel.from_pretrained(base_model, self.model_path).to(self.device)
            self.model.eval()

    def generate_response(self, question: str) -> str:
        """Generate answer to user question with memory cleanup"""
        try:
            # Create prompt
            prompt = SYSTEM_PROMPT.format(question=question)

            # Tokenize
            inputs = self.tokenizer(
                prompt,
                return_tensors="pt",
                truncation=True,
                max_length=512
            ).to(self.device)

            # Generate with inference_mode for better performance
            with torch.inference_mode():
                outputs = self.model.generate(
                    **inputs,
                    max_new_tokens=MAX_NEW_TOKENS,
                    temperature=TEMPERATURE,
                    do_sample=True,
                    top_p=TOP_P,
                    repetition_penalty=REPETITION_PENALTY,
                    pad_token_id=self.tokenizer.eos_token_id
                )

            # Decode
            response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)

            # Extract assistant's response
            if "<|assistant|>" in response:
                response = response.split("<|assistant|>")[-1].strip()

            # Explicit cleanup
            del inputs
            del outputs
            gc.collect()

            return response

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error processing your question. Please try again."

        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "Sorry, I encountered an error processing your question. Please try again."

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "Welcome to Linux Command Helper Bot!\n\n"
            "I can explain Linux commands in simple terms.\n\n"
            "Examples:\n"
            "• 'Explain ls'\n"
            "• 'What does grep do?'\n"
            "• 'How to use chmod?'\n\n"
            "You can ask in English or Russian, but I'll always respond in English.\n\n"
            "Just send me your question!"
        )
        await update.message.reply_text(welcome_message)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_message = (
            "Commands:\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n\n"
            "Usage:\n"
            "Simply type your question about any Linux command.\n\n"
            "Examples:\n"
            "• 'Explain the ls command'\n"
            "• 'What does cd do?'\n"
            "• 'Что делает grep?' (Russian OK!)"
        )
        await update.message.reply_text(help_message)

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user messages"""
        user_message = update.message.text
        if not user_message:
            return

        logger.info(f"Question: {user_message}")

        # Send "typing..." indicator
        await update.message.chat.send_action("typing")

        # Generate response
        response = self.generate_response(user_message)

        logger.info(f"Response: {response[:100]}...")

        # Send response
        await update.message.reply_text(response)

    async def error_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")

    def run(self):
        """Start the bot"""
        if not self.token:
            logger.error("TELEGRAM_TOKEN not found in environment variables!")
            return

        # Load model first
        self.load_model()

        # Create application
        app = Application.builder().token(self.token).build()

        # Add handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))

        # Add error handler
        app.add_error_handler(self.error_handler)

        # Start bot
        logger.info("Bot is running...")
        app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    bot = LinuxCommandBot()
    bot.run()
