from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define the group or channel details
CHANNEL_NAME = "ElitesFilmy"  # Replace with your channel name
CHANNEL_POST_ID = 18  # Replace with the actual post ID

# Function to handle the /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Hello {update.effective_user.first_name}. Send me any file, and I will provide you with a link to the attachment.')

# Function to handle file uploads and share the embed link
async def handle_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.document:
        file = update.message.document
    elif update.message.photo:
        file = update.message.photo[-1]  # Get the highest quality photo
    else:
        await update.message.reply_text('Please send a document or image.')
        return

    file_name = file.file_name if hasattr(file, 'file_name') else 'image.jpg'  # Default name for photos
    print(f"Received file: {file_name}")

    try:
        # Forward the file to the public channel
        message = await update.message.forward(chat_id=f"@{CHANNEL_NAME}")

        # Construct the embed code
        post_id = message.message_id
        embed_code = f'<script async src="https://telegram.org/js/telegram-widget.js?22" data-telegram-post="{CHANNEL_NAME}/{post_id}" data-width="100%"></script>'

        # Send the embed code to the user
        await update.message.reply_text(f'Thanks for sending the file "{file_name}"! Here is the link to the attachment: {embed_code}')
    except Exception as e:
        # Handle exceptions and send error message
        print(f"Error forwarding file and generating link: {e}")
        await update.message.reply_text(f'Failed to forward file and provide link.')

# Get the bot token
TOKEN = os.getenv("teleToken")

# Create the Application
app = ApplicationBuilder().token(TOKEN).build()

# Add handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_file))

# Start the bot
app.run_polling()
