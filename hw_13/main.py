import sys
import os

# Ensure the root directory is in sys.path
root_dir = os.path.dirname(os.path.abspath(__file__))
if root_dir not in sys.path:
    sys.path.insert(0, root_dir)

from bot.telegram_bot import LinuxCommandBot

def main():
    print("Starting Linux Command Chatbot...")
    bot = LinuxCommandBot()
    bot.run()

if __name__ == "__main__":
    main()
