import logging
import re
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# Configuração de logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class TelegramBot:
    def __init__(self, token, download_callback):
        self.token = token
        self.download_callback = download_callback
        self.app = ApplicationBuilder().token(self.token).build()

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not update.message or not update.message.text:
            return

        text = update.message.text
        # Regex para identificar links do Freepik e Envato
        freepik_pattern = r'https?://(?:www\.)?freepik\.com/[^\s]+'
        envato_pattern = r'https?://(?:www\.)?elements\.envato\.com/[^\s]+'

        links = re.findall(f'({freepik_pattern}|{envato_pattern})', text)

        if links:
            for link in links:
                await update.message.reply_text(f"Recebi seu link: {link}\nIniciando o processo de download e upload...")
                # Chama o callback que fará o download e upload
                try:
                    result_link = await self.download_callback(link)
                    if result_link:
                        await update.message.reply_text(f"Aqui está o seu arquivo: {result_link}")
                    else:
                        await update.message.reply_text("Desculpe, ocorreu um erro ao processar seu arquivo.")
                except Exception as e:
                    logging.error(f"Erro ao processar link {link}: {e}")
                    await update.message.reply_text(f"Erro técnico ao processar o link.")

    def run(self):
        message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), self.handle_message)
        self.app.add_handler(message_handler)
        print("Bot do Telegram iniciado...")
        self.app.run_polling()
