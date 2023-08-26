import logging
import asyncio
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from bs4 import BeautifulSoup
from config import Config
import processing.text as summary
from processing.html import extract_hyperlinks, format_hyperlinks
import time
import threading

logging.basicConfig(filename='/tmp/logfile.log', level=logging.DEBUG, format='%(asctime)s [%(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

CFG = Config()
executor = ThreadPoolExecutor()


class LogMonitor:
    @staticmethod
    def tail(log_file_path="/tmp/logfile.log"):
        while not Path(log_file_path).exists():
            logger.info("Waiting for the log file to be created...")
            time.sleep(5)
        with open(log_file_path, 'r') as file:
            file.seek(0, 2)
            while True:
                line = file.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                logger.info(line.strip())


class WebBrowser:
    def __init__(self):
        self.driver = self._setup_webdriver()

    def _setup_webdriver(self):
        try:
            options = {
                "chrome": CFG.chrome_options,
                "safari": CFG.safari_options,
                "firefox": CFG.firefox_options
            }[CFG.selenium_web_browser]

            drivers = {
                "chrome": CFG.chrome_driver,
                "safari": CFG.safari_driver,
                "firefox": CFG.firefox_driver
            }
        except AttributeError as e:
            logger.error(f"Configuration Error: {e}")
            raise

        return drivers[CFG.selenium_web_browser](options)

    def scrape_website_content(self, url):
        self.driver.get(url)
        WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        soup = BeautifulSoup(self.driver.execute_script("return document.body.outerHTML;"), "html.parser")
        for script in soup(["script", "style"]):
            script.extract()
        return soup.get_text()

    def inject_website_headers(self):
        headers = [f"<h1>{CFG.website_header_title}</h1>", f"<h2>{CFG.website_header_subtitle}</h2>"]
        for header in headers:
            self.driver.execute_script(f"document.body.insertAdjacentHTML('afterbegin', '{header}');")

    def close(self):
        self.driver.quit()


async def async_browse(url, question, websocket):
    browser = WebBrowser()
    loop = asyncio.get_event_loop()

    try:
        await websocket.send_json({"type": "logs", "output": f"🔎 Estudiando {url} para información relevante sobre: {question}..."})

        text = await loop.run_in_executor(executor, browser.scrape_website_content, url)
        await loop.run_in_executor(executor, browser.inject_website_headers)

        summary_text = await loop.run_in_executor(executor, summary.summarize_text, url, text, question)
        await websocket.send_json({"type": "logs", "output": f"📝 Información obtenida de {url}: {summary_text}"})
        
        return f"Information gathered from url {url}: {summary_text}"
    finally:
        browser.close()


def browse_website(url, question):
    browser = WebBrowser()
    text = browser.scrape_website_content(url)
    browser.inject_website_headers()
    summary_text = summary.summarize_text(url, text, question)
    links = extract_hyperlinks(BeautifulSoup(browser.driver.page_source, "html.parser"), url)
    formatted_links = format_hyperlinks(links, CFG)[:5]
    browser.close()
    return f"Answer gathered from website: {summary_text} \n \n Links: {formatted_links}"


if __name__ == "__main__":
    threading.Thread(target=LogMonitor.tail).start()
    logger.info("Reading logs...")
    time.sleep(10)
    logger.info("Finished reading logs!")


