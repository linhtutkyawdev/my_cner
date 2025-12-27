import time
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.logging import RichHandler
import logging
from scraper import scrape_page
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
from threading import Lock

# Configure logging with RichHandler
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

log = logging.getLogger("rich")


class WebDriverManager:
    def __init__(self, num_drivers=5):
        self.num_drivers = num_drivers
        self.driver_queue = queue.Queue()
        for _ in range(self.num_drivers):
            options = webdriver.ChromeOptions()
            options.add_argument("--headless")
            try:
                driver = webdriver.Chrome(
                    service=Service(ChromeDriverManager().install()), options=options
                )
            except ValueError:
                driver = webdriver.Chrome(service=Service(), options=options)
            self.driver_queue.put(driver)

    def get_driver(self):
        return self.driver_queue.get()

    def return_driver(self, driver):
        self.driver_queue.put(driver)

    def shutdown(self):
        while not self.driver_queue.empty():
            driver = self.driver_queue.get()
            driver.quit()




def crawl_page(url, driver_manager, crawled_urls, pages_to_crawl, netloc, lock):
    """
    Crawls a single page, scrapes it, and finds new links.
    """
    with lock:
        if url in crawled_urls:
            return None, []
        crawled_urls.add(url)

    driver = driver_manager.get_driver()
    try:
        driver.get(url)
        scrape_page(driver, url)
        
        soup = BeautifulSoup(driver.page_source, "lxml")
        new_links = []
        for link in soup.find_all("a", href=True):
            full_url = urljoin(url, link["href"])
            if "videos" in full_url:
                continue
            with lock:
                if (
                    urlparse(full_url).netloc == netloc
                    and full_url not in crawled_urls
                    and full_url not in pages_to_crawl
                ):
                    new_links.append(full_url)
                    pages_to_crawl.add(full_url)

        return f"Crawled {url}", new_links
    except WebDriverException as e:
        log.error(f"Could not fetch {url}: {e}")
        return None, []
    except Exception as e:
        log.error(f"An error occurred while processing {url}: {e}")
        return None, []
    finally:
        driver_manager.return_driver(driver)


def crawl_website(start_url, max_workers=5):
    """
    Crawls a website starting from a given URL, scrapes each page,
    and follows internal links using a thread pool.
    """
    netloc = urlparse(start_url).netloc
    crawled_urls = set()
    pages_to_crawl = {start_url}
    lock = Lock()

    driver_manager = WebDriverManager(num_drivers=max_workers)

    try:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("({task.completed} of {task.total})"),
            transient=False,
        ) as progress:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                task = progress.add_task("Crawling...", total=len(pages_to_crawl))
                
                while pages_to_crawl:
                    with lock:
                        urls_to_crawl = list(pages_to_crawl)
                        pages_to_crawl.clear()

                    futures = {executor.submit(crawl_page, url, driver_manager, crawled_urls, pages_to_crawl, netloc, lock) for url in urls_to_crawl}

                    for future in as_completed(futures):
                        description, new_links = future.result()
                        if description:
                            progress.update(task, description=description)
                        
                        progress.update(task, advance=1, total=len(crawled_urls) + len(pages_to_crawl))

    finally:
        driver_manager.shutdown()



if __name__ == "__main__":
    start_url = "https://www.duwun.com.mm/"
    crawl_website(start_url, max_workers=10)
