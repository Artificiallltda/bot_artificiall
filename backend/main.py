import asyncio
import logging
import os
from config import (
    TELEGRAM_TOKEN, FREEPIK_EMAIL, FREEPIK_PASSWORD,
    ENVATO_EMAIL, ENVATO_PASSWORD, DRIVE_FOLDER_ID, DOWNLOAD_PATH
)
from modules.bot import TelegramBot
from modules.downloader import Downloader
from modules.drive_service import DriveService

# Configuração de logs
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AutomationApp:
    def __init__(self):
        # Inicializa o Downloader
        self.downloader = Downloader(
            freepik_creds={'email': FREEPIK_EMAIL, 'password': FREEPIK_PASSWORD},
            envato_creds={'email': ENVATO_EMAIL, 'password': ENVATO_PASSWORD},
            download_path=DOWNLOAD_PATH
        )
        
        # Inicializa o Drive Service
        # O arquivo 'credentials.json' deve estar na raiz do projeto
        self.drive_service = DriveService(
            credentials_path='credentials.json',
            folder_id=DRIVE_FOLDER_ID
        )

    async def process_download_and_upload(self, url):
        """
        Esta função é o callback que o bot chama quando recebe um link.
        """
        try:
            # 1. Faz o download do arquivo
            file_path = await self.downloader.download_file(url)
            
            if not file_path:
                logging.error(f"Falha ao baixar o arquivo da URL: {url}")
                return None
            
            # 2. Faz o upload para o Google Drive
            drive_link = self.drive_service.upload_file(file_path)
            
            # 3. Remove o arquivo local para economizar espaço
            if drive_link and os.path.exists(file_path):
                os.remove(file_path)
                logging.info(f"Arquivo local removido após upload: {file_path}")
                
            return drive_link
            
        except Exception as e:
            logging.error(f"Erro no fluxo de processamento: {e}")
            return None

    def run(self):
        # Inicializa o Bot do Telegram com o callback de processamento
        bot = TelegramBot(
            token=TELEGRAM_TOKEN,
            download_callback=self.process_download_and_upload
        )
        bot.run()

if __name__ == "__main__":
    # Garantir que o diretório de downloads existe
    if not os.path.exists(DOWNLOAD_PATH):
        os.makedirs(DOWNLOAD_PATH)
        
    app = AutomationApp()
    app.run()
