import os
import logging
from playwright.async_api import async_playwright

class Downloader:
    def __init__(self, freepik_creds, envato_creds, download_path):
        self.freepik_creds = freepik_creds
        self.envato_creds = envato_creds
        self.download_path = download_path
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)

    async def download_file(self, url):
        async with async_playwright() as p:
            # Lançar navegador. Em produção, headless=True é recomendado.
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = await context.new_page()

            try:
                if "freepik.com" in url:
                    file_path = await self._download_freepik(page, url)
                elif "elements.envato.com" in url:
                    file_path = await self._download_envato(page, url)
                else:
                    logging.warning(f"URL não suportada: {url}")
                    file_path = None
                
                return file_path
            except Exception as e:
                logging.error(f"Erro durante o download de {url}: {e}")
                return None
            finally:
                await browser.close()

    async def _download_freepik(self, page, url):
        logging.info(f"Acessando Freepik para download: {url}")
        # Login
        await page.goto("https://www.freepik.com/login")
        # Aceitar cookies se aparecer
        try:
            await page.click("#onetrust-accept-btn-handler", timeout=5000)
        except:
            pass
            
        await page.fill('input[name="email"]', self.freepik_creds['email'])
        await page.fill('input[name="password"]', self.freepik_creds['password'])
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")

        # Ir para a URL do arquivo
        await page.goto(url)
        
        # Tentar encontrar o botão de download principal
        # O Freepik muda seletores frequentemente, então usamos uma abordagem mais flexível
        download_selectors = [
            "button.download-button",
            "button#download-file",
            "a.download-button",
            "text=Download"
        ]
        
        for selector in download_selectors:
            btn = page.locator(selector).first
            if await btn.is_visible():
                async with page.expect_download() as download_info:
                    await btn.click()
                download = await download_info.value
                path = os.path.join(self.download_path, download.suggested_filename)
                await download.save_as(path)
                logging.info(f"Download concluído: {path}")
                return path
        
        logging.error("Botão de download não encontrado no Freepik.")
        return None

    async def _download_envato(self, page, url):
        logging.info(f"Acessando Envato para download: {url}")
        # Login
        await page.goto("https://elements.envato.com/sign-in")
        await page.fill('#username', self.envato_creds['email'])
        await page.fill('#password', self.envato_creds['password'])
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")

        # Ir para a URL do arquivo
        await page.goto(url)
        
        # Botão de download inicial
        download_btn = page.locator('button:has-text("Download")').first
        if await download_btn.is_visible():
            await download_btn.click()
            
            # Envato geralmente pede para selecionar um projeto ou licença
            # Vamos tentar clicar em "Download without a project" ou similar se disponível
            # Ou simplesmente "Add & Download" se as configurações permitirem
            confirm_btn = page.locator('button:has-text("Add & Download"), button:has-text("Download")').last
            if await confirm_btn.is_visible():
                async with page.expect_download() as download_info:
                    await confirm_btn.click()
                download = await download_info.value
                path = os.path.join(self.download_path, download.suggested_filename)
                await download.save_as(path)
                logging.info(f"Download concluído: {path}")
                return path
                
        logging.error("Botão de download não encontrado no Envato.")
        return None
