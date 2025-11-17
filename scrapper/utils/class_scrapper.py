import requests
import uuid
from datetime import datetime
from bs4 import BeautifulSoup
from urllib3.util.retry import Retry
from requests.adapters import HTTPAdapter


class Scrapper:
    def __init__(self):
        self.scrape_date = datetime.now().strftime("%H:%M:%S")
        self.execution_id = str(uuid.uuid4())
        self.session = requests.Session()
        self.locator = None
        self.feed = None

    def configure_retry(self, retries):
        retries = Retry(
            total=retries,
            backoff_factor=1,
            status_forcelist=[500, 502, 503, 504],
            allowed_methods=["POST"],
        )

        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount("https://", adapter)

    def get_request(self, url):
        response = self.session.get(url)

        return self.session.cookies.get("__RequestVerificationToken"), response.text

    def post_requests(self, url, **kwargs):
        response = self.session.post(url, data=kwargs["data"])

        return response.json()

    def fetch_token(self, html):
        html_soup = BeautifulSoup(html, "html.parser")

        token_input = html_soup.find(
            "input", {"name": "__RequestVerificationToken"}
        ).get("value")

        return token_input
