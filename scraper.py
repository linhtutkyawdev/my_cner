import os
import re
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from rich.logging import RichHandler
import logging

# Configure logging with RichHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")


def sanitize_filename(filename):
    """
    Removes invalid characters from a filename.
    """
    return re.sub(r'[<>:"/\\|?*]', "_", filename)


def scrape_page(driver, url):
    """
    Scrapes a single web page using an existing Selenium driver instance
    and saves its text content to a file if it's an article page.
    """
    try:
        soup = BeautifulSoup(driver.page_source, "lxml")

        # Find the title to determine if it's an article page
        title_tag = soup.find("h1", class_=lambda x: x and "article" in x)

        # If there's no title tag, it's not an article, so we skip it
        if not title_tag:
            log.info(f"Skipping non-article page: {url}")
            return

        title = title_tag.get_text().strip()
        
        # Truncate title to a safe length for the filename
        truncated_title = title[:50]
        sanitized_title = sanitize_filename(truncated_title)
        
        # Check if a file with a similar name already exists
        raw_dir = "data/raw"
        os.makedirs(raw_dir, exist_ok=True)
        
        # Check for existing files starting with the sanitized title
        if any(f.startswith(sanitized_title) for f in os.listdir(raw_dir)):
            log.info(f"Skipping already scraped article: {title}")
            return

        # Find the content container based on the provided structure
        content = soup.select_one('div > div[style*="background-color"]')

        if content and title:
            text = content.get_text(separator=os.linesep, strip=True)
            # Create a filename from the title
            filename = f"{sanitized_title}.txt"
            # Ensure the directory exists
            with open(
                os.path.join(raw_dir, filename), "w", encoding="utf-8"
            ) as f:
                f.write(text)
            log.info(f"Successfully scraped {url} and saved to {filename}")
        else:
            log.warning(f"Could not find content for article: {url}")
    except Exception as e:
        log.error(f"An error occurred while scraping {url}: {e}")

if __name__ == "__main__":
    # Example usage:
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()), options=options
    )
    scrape_page(driver, "https://www.duwun.com.mm/")
    driver.quit()
