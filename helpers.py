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
