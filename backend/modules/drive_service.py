import os
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

class DriveService:
    def __init__(self, credentials_path, folder_id):
        self.credentials_path = credentials_path
        self.folder_id = folder_id
        self.scopes = ['https://www.googleapis.com/auth/drive.file']
        self.service = self._authenticate()

    def _authenticate(self):
        if not os.path.exists(self.credentials_path):
            logging.warning(f"Arquivo de credenciais do Google não encontrado em: {self.credentials_path}")
            return None
        
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scopes
            )
            return build('drive', 'v3', credentials=creds)
        except Exception as e:
            logging.error(f"Erro na autenticação do Google Drive: {e}")
            return None

    def upload_file(self, file_path):
        if not self.service:
            logging.error("Serviço do Google Drive não disponível.")
            return None

        if not os.path.exists(file_path):
            logging.error(f"Arquivo local não encontrado para upload: {file_path}")
            return None

        file_name = os.path.basename(file_path)
        file_metadata = {
            'name': file_name,
            'parents': [self.folder_id] if self.folder_id else []
        }
        
        media = MediaFileUpload(file_path, resumable=True)
        
        try:
            # Upload do arquivo
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
            ).execute()
            
            file_id = file.get('id')
            logging.info(f"Arquivo enviado com sucesso. ID: {file_id}")

            # Alterar permissão para "qualquer pessoa com o link pode ler"
            self.service.permissions().create(
                fileId=file_id,
                body={'type': 'anyone', 'role': 'viewer'}
            ).execute()

            # Obter o link de compartilhamento final
            file_info = self.service.files().get(
                fileId=file_id,
                fields='webViewLink'
            ).execute()

            return file_info.get('webViewLink')

        except Exception as e:
            logging.error(f"Erro ao fazer upload para o Google Drive: {e}")
            return None
    
    def test_connection(self):
        """Testa a conexão com o Google Drive"""
        if not self.service:
            return False
        
        try:
            # Tenta listar os arquivos na pasta (ou apenas verificar permissões)
            if self.folder_id:
                # Verifica se consegue acessar a pasta
                self.service.files().get(fileId=self.folder_id, fields='id').execute()
            else:
                # Se não tem pasta configurada, apenas verifica se o serviço está funcionando
                self.service.files().list(pageSize=1).execute()
            return True
        except Exception as e:
            logging.error(f"Erro ao testar conexão do Google Drive: {e}")
            return False