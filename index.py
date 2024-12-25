import requests
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

TOKEN = "7849034938:AAF9OqW9F7n9lgWm3vR-DFSiMRsuPWftcYs"
DEFAULT_TEXT_MODEL = "openai"
DEFAULT_IMAGE_MODEL = "flux"

user_settings = {}

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_settings[chat_id] = {"text_model": DEFAULT_TEXT_MODEL, "image_model": DEFAULT_IMAGE_MODEL}
    update.message.reply_text("Hi! Let's start.\n\nUse:\n/text_model - Choose a text model\n/image_model - Choose an image model\n/eragen <prompt> - Generate an image\nFeel free to chat anytime!")

def text_model(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    response = requests.get("https://image.pollinations.ai/models").json()
    text_models = [model for model in response if "text" in model.lower()]
    
    keyboard = [[InlineKeyboardButton(model, callback_data=f"text_model:{model}")] for model in text_models]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose a text model:", reply_markup=reply_markup)

def image_model(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    response = requests.get("https://image.pollinations.ai/models").json()
    image_models = [model for model in response if "image" in model.lower()]
    
    keyboard = [[InlineKeyboardButton(model, callback_data=f"image_model:{model}")] for model in image_models]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("Choose an image model:", reply_markup=reply_markup)

def eragen(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    if len(context.args) == 0:
        update.message.reply_text("Usage: /eragen <prompt>")
        return

    prompt = " ".join(context.args)
    model = user_settings[chat_id].get("image_model", DEFAULT_IMAGE_MODEL)
    seed = random.randint(1, 10000)
    
    # Generate image
    response = requests.get(f"https://image.pollinations.ai/prompt/{prompt}", params={"model": model, "seed": seed})
    if response.status_code == 200:
        update.message.reply_photo(response.content, caption="Here is your generated image.")
        # Generate variation
        new_seed = random.randint(1, 10000)
        response_variation = requests.get(f"https://image.pollinations.ai/prompt/{prompt}", params={"model": model, "seed": new_seed})
        if response_variation.status_code == 200:
            update.message.reply_photo(response_variation.content, caption="Variation with a new seed.")
    else:
        update.message.reply_text("Error generating image. Please try again.")

def handle_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    chat_id = query.message.chat_id
    data = query.data.split(":")
    
    if data[0] == "text_model":
        user_settings[chat_id]["text_model"] = data[1]
        query.edit_message_text(f"Text model set to: {data[1]}")
    elif data[0] == "image_model":
        user_settings[chat_id]["image_model"] = data[1]
        query.edit_message_text(f"Image model set to: {data[1]}")

def chat(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    model = user_settings[chat_id].get("text_model", DEFAULT_TEXT_MODEL)
    seed = random.randint(1, 10000)
    
    messages = [{"role": "user", "content": update.message.text}]
    payload = {"messages": messages, "model": model, "seed": seed, "jsonMode": False}
    response = requests.post("https://text.pollinations.ai/", json=payload)
    
    if response.status_code == 200:
        generated_text = response.json().get("generated_text", "Error: No response")
        update.message.reply_text(generated_text)
    else:
        update.message.reply_text("Error generating text. Please try again.")

def main():
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("text_model", text_model))
    dispatcher.add_handler(CommandHandler("image_model", image_model))
    dispatcher.add_handler(CommandHandler("eragen", eragen))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, chat))
    dispatcher.add_handler(CallbackQueryHandler(handle_callback))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
