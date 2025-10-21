import os
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Your base API URL
API_BASE = "https://odd-meadow-68ee.batvalour-13d.workers.dev"

# ---- Helper functions ----
def get_records(page=1, per_page=10, carrier=None):
    url = f"{API_BASE}/records?page={page}&per_page={per_page}"
    if carrier:
        url += f"&carrier={carrier}"
    res = requests.get(url)
    return res.json()

def get_record(number):
    url = f"{API_BASE}/record/{number}"
    res = requests.get(url)
    return res.json()

def search_records(query):
    url = f"{API_BASE}/search?q={query}"
    res = requests.get(url)
    return res.json()

def format_record(record):
    # Make JSON user-friendly
    formatted = "\n".join([f"👉 {k.capitalize()}: {v}" for k, v in record.items()])
    return formatted

# ---- Telegram Bot Handlers ----
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome!\n\nYou can:\n"
        "/record <number> - Get a record by number\n"
        "/search <query> - Search records\n"
        "/carrier <name> - View carrier data\n"
    )

async def record_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠ Please provide a record number.")
        return
    number = context.args[0]
    data = get_record(number)
    if data.get("ok"):
        formatted = format_record(data["record"])
        await update.message.reply_markdown(formatted)
    else:
        await update.message.reply_text("❌ Record not found.")

async def search_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠ Please provide a search query.")
        return
    query = " ".join(context.args)
    data = search_records(query)
    if data.get("ok") and data.get("results"):
        results = data["results"][:5]  # Limit to first 5
        text = "\n\n".join(format_record(r) for r in results)
        await update.message.reply_markdown(text)
    else:
        await update.message.reply_text("❌ No matching records found.")

async def carrier_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠ Please provide a carrier name.")
        return
    carrier = context.args[0]
    data = get_records(carrier=carrier)
    if data.get("ok") and data.get("records"):
        records = data["records"][:5]
        text = "\n\n".join(format_record(r) for r in records)
        await update.message.reply_markdown(text)
    else:
        await update.message.reply_text("❌ No records found for that carrier.")

# ---- Main ----
def main():
    token = os.getenv("BOT_TOKEN")  # Set this in Render environment
    app = ApplicationBuilder().token(token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("record", record_cmd))
    app.add_handler(CommandHandler("search", search_cmd))
    app.add_handler(CommandHandler("carrier", carrier_cmd))

    app.run_polling()

if __name__ == "__main__":
    main()
