import asyncio
import logging
import os
from .config import (
    TELEGRAM_TOKEN, FREEPIK_EMAIL, FREEPIK_PASSWORD,
    ENVATO_EMAIL, ENVATO_PASSWORD, DRIVE_FOLDER_ID, DOWNLOAD_PATH
)
from .modules.bot import TelegramBot
from .modules.downloader import Downloader
from .modules.drive_service import DriveService

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

    async def process_download_and_upload(self, url, telegram_message=None):
        """
        Esta função é o callback que o bot chama quando recebe um link.
        Se telegram_message for fornecido, envia o arquivo diretamente pelo Telegram.
        Caso contrário, faz upload para o Google Drive e retorna o link.
        """
        try:
            # 1. Faz o download do arquivo
            file_path = await self.downloader.download_file(url)
            
            if not file_path:
                logging.error(f"Falha ao baixar o arquivo da URL: {url}")
                return None
            
            # 2. Se temos acesso à mensagem do Telegram, envia o arquivo diretamente
            if telegram_message:
                try:
                    # Envia o arquivo diretamente pelo Telegram
                    with open(file_path, 'rb') as file:
                        await telegram_message.reply_document(document=file)
                    logging.info(f"Arquivo enviado pelo Telegram: {file_path}")
                    
                    # Remove o arquivo local após enviar
                    if os.path.exists(file_path):
                        os.remove(file_path)
                        logging.info(f"Arquivo local removido após envio: {file_path}")
                    
                    return file_path  # Retorna o caminho para indicar sucesso
                except Exception as e:
                    logging.error(f"Erro ao enviar arquivo pelo Telegram: {e}")
                    # Se falhar, tenta fazer upload para o Drive como fallback
            
            # 3. Faz o upload para o Google Drive (se configurado e não enviou pelo Telegram)
            if self.drive_service and self.drive_service.service and DRIVE_FOLDER_ID:
                drive_link = self.drive_service.upload_file(file_path)
                
                # Remove o arquivo local após upload
                if drive_link and os.path.exists(file_path):
                    os.remove(file_path)
                    logging.info(f"Arquivo local removido após upload: {file_path}")
                
                return drive_link
            else:
                # Se não tem Google Drive configurado e não enviou pelo Telegram, retorna o caminho
                logging.warning("Google Drive não configurado e mensagem do Telegram não fornecida. Arquivo salvo localmente.")
                return file_path
            
        except Exception as e:
            logging.error(f"Erro no fluxo de processamento: {e}")
            return None

    async def test_logins(self):
        """Testa os logins do Freepik, Envato e Google Drive"""
        results = {
            'freepik': None,
            'envato': None,
            'google_drive': None
        }
        
        # Testar Freepik
        if FREEPIK_EMAIL and FREEPIK_PASSWORD:
            try:
                results['freepik'] = await self.downloader.test_freepik_login()
            except Exception as e:
                logging.error(f"Erro ao testar login do Freepik: {e}")
                results['freepik'] = False
        else:
            results['freepik'] = None  # Não configurado
        
        # Testar Envato
        if ENVATO_EMAIL and ENVATO_PASSWORD:
            try:
                results['envato'] = await self.downloader.test_envato_login()
            except Exception as e:
                logging.error(f"Erro ao testar login do Envato: {e}")
                results['envato'] = False
        else:
            results['envato'] = None  # Não configurado
        
        # Testar Google Drive
        if self.drive_service:
            try:
                results['google_drive'] = self.drive_service.test_connection()
            except Exception as e:
                logging.error(f"Erro ao testar conexão do Google Drive: {e}")
                results['google_drive'] = False
        else:
            results['google_drive'] = None  # Não configurado
        
        return results
    
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
