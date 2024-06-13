import requests

from munch import Munch


class BasePage:
    """
    Selenium base class to initialize the base page that will be called from all pages
    """

    def __init__(self, driver):
        self.driver = driver
        self.set_window_size(1920, 1080)
        self.driver.implicitly_wait(5)

    def open_page(self, url):
        self.driver.get(url)

    def set_window_size(self, width, height):
        self.driver.set_window_size(width, height)


class HttpClient:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()

    def make_request(self, method: str, url: str, headers: dict = None, data: str = None, **kwargs) -> Munch:
        response = self.session.request(method, url, headers=headers, data=data, **kwargs)
        data = response.json() if 'application/json' in response.headers.get('content-type') else response.text

        return Munch(
            url=url,
            status_code=response.status_code,
            reason=response.reason,
            data=data,
        )

    def update_headers(self, headers: dict) -> None:
        self.session.headers.update(headers)

    def remove_headers(self, *headers) -> None:
        """
        Example usage:
            self.remove_headers('Authorization', 'website')
        """
        for header in headers:
            self.session.headers.pop(header, None)

    def remove_all_headers(self):
        self.session.headers.clear()

    def build_url(self, path: str, protocol: str = "https", host: str = None) -> str:
        """Build the full URL, handling trailing/leading slashes and allowing specification of the protocol.

        Args:
            path: The path to resource. Example: /path/1/version/2
            protocol: Data transfer protocols HTTPS, HTTP, FTP, TCP, etc.
            host: Host name. Example: test.com

        Returns:
            Full URL.
        """
        host = host if host else self.base_url

        if host.endswith("/"):
            host = host[:-1]  # Remove trailing slash.

        if not path.startswith("/"):
            path = "/" + path  # Add leading slash.

        if host.startswith("http://") or host.startswith("https://"):
            return f"{host}{path}"

        return f"{protocol}://{host}{path}"

