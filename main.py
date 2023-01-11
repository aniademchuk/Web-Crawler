import os
import requests
import re
from bs4 import BeautifulSoup

visited_urls = set()

# Proxy
proxies = {
    "http": "http://10.10.1.10:3128",
    "https": "http://10.10.1.10:1080",
}


# Memento
class Memento:
    def __init__(self, state):
        self.state = state


class Originator:
    def __init__(self):
        self.state = set()

    def create_memento(self):
        return Memento(self.state)

    def restore_memento(self, memento):
        self.state = memento.state


class CareTaker:
    def __init__(self):
        self.mementos = []

    def add_memento(self, memento):
        self.mementos.append(memento)

    def get_memento(self, index):
        return self.mementos[index]


# Chain of Responsibility
class LinkHandler:
    def __init__(self, crawler):
        self.crawler = crawler

    def handle(self, link):
        """
        Скануємо вказане посилання та зберігаємо HTML-сторінку в окремому пакеті.
        """
        # Скануємо посилання
        crawl(link)


class HttpLinkHandler(LinkHandler):
    def handle(self, link):
        if link.startswith("http"):
            # Скануємо посилання
            super().handle(link)
        else:
            # Передаємо посилання наступному обробнику в ланцюжку
            self.next_handler.handle(link)


class HttpsLinkHandler(LinkHandler):
    def handle(self, link):
        if link.startswith("https"):
            # Скануємо посилання
            super().handle(link)
        else:
            # Передаємо посилання наступному обробнику в ланцюжку
            self.next_handler.handle(link)


# Template Method
class CrawlTemplate:
    def crawl(self, url, depth=0, max_depth=3):
        self.pre_crawl(url, depth, max_depth)
        self.crawl_page(url)
        self.post_crawl(url, depth, max_depth)

    def pre_crawl(self, url, depth, max_depth):
        # Виконуємо завдання перед скануванням
        pass

    def crawl_page(self, url):
        # Реалізуємо завдання сканування сторінок
        pass

    def post_crawl(self, url, depth, max_depth):
        # завдання після сканування
        pass


class WebsiteCrawler(CrawlTemplate):
    def __init__(self):
        # Створюємо об’єкти originator і caretaker
        self.originator = Originator()
        self.caretaker = CareTaker()

    def sanitize_url(url):
        """
        Видаляємо спеціальні символи з URL-адреси, щоб створити валідну назву каталогу.
        """
        return re.sub(r'[^a-zA-Z0-9_.-]', '_', url)

    def pre_crawl(self, url, depth, max_depth):
        # Перевіряємо, чи досягнуто максимальної глибини
        if depth > max_depth:
            return

        # Перевіряємо, чи URL-адреса вже була відвідана
        if url in self.originator.state:
            return
        self.originator.state.add(url)

        # Зберігаємо поточнй стан у memento
        memento = self.originator.create_memento()
        self.caretaker.add_memento(memento)

    def crawl(self, url, depth=0, max_depth=3, link_handler=None):
        """
        Скануємо вказану URL-адресу та зберігаємл HTML у файлі. Потім проскануємо всі посилання
        на сторінці та збережемо свій HTML у файлах у підкаталозі.
        """
        # Перевіряємо, чи досягнуто максимальної глибини
        if depth > max_depth:
            return

        # Перевіряємо, чи URL-адреса вже була відвідана
        if url in self.originator.state:
            return
        self.originator.state.add(url)

        # Зберігаємо поточнй стан у memento
        memento = self.originator.create_memento()
        self.caretaker.add_memento(memento)

        # Надсилаємо запит GET на URL
        response = requests.get(url, proxies=proxies)

        # Аналізуємо вміст HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Створюємо новий каталог для файлів HTML
        directory = self.sanitize_url(url)
        if not os.path.exists(directory):
            os.makedirs(directory)

        # Збережемо HTML у файл
        filename = os.path.join(directory, 'index.html')
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())

        # Знайдемо усі посилання на сторінці
        links = soup.find_all('a')
        # Передаємо посилання обробнику посилань
        for link in links:
            href = link.get('href')
            if href:
                link_handler.handle(href, depth + 1, max_depth)

    def post_crawl(self, url, depth, max_depth):

        response = requests.get(url, proxies=proxies)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Знайдемо усі посилання на сторінці
        links = soup.find_all('a')

        # Передаємо посилання першому обробнику в ланцюжку
        for link in links:
            href = link.get('href')
            if href:
                self.https_handler.handle(href)


def crawl(url, depth=0, max_depth=3):
    """
    Скануємо вказану URL-адресу та зберігаємо HTML у файлі. Потім проскануємо всі посилання
    на сторінці та збережемо свій HTML у файлах у підкаталозі.
    """
    # Перевіряємо, чи досягнуто максимальної глибини
    if depth > max_depth:
        return

    # Перевіряємо, чи URL-адреса вже була відвідана
    if url in visited_urls:
        return
    visited_urls.add(url)

    # Надсилаємо запит GET на URL
    response = requests.get(url)

    # Аналізуємо вміст HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Створюємо новий каталог для файлів HTML
    directory = re.sub(r'[^a-zA-Z0-9_.-]', '_', url)
    if not os.path.exists(directory):
        os.makedirs(directory)

    # Збережемо HTML у файл
    filename = os.path.join(directory, 'index.html')
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(soup.prettify())

    # Знайдемо усі посилання на сторінці
    links = soup.find_all('a')

    # Рекурсивно скануємо посилання
    for link in links:
        href = link.get('href')
        if href and href.startswith('http'):
            crawl(href, depth + 1)


# Composite
class HtmlPage:
    def __init__(self, url, content):
        self.url = url
        self.content = content


class HtmlPackage:
    def __init__(self):
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)

    def remove_page(self, page):
        self.pages.remove(page)

    def get_size(self):
        size = 0
        for page in self.pages:
            size += len(page.content)
        return size


# Створюємо об’єкт crawler
crawler = WebsiteCrawler()

# Створюємо об’єкти обробки посилань
http_handler = HttpLinkHandler(crawler)
https_handler = HttpsLinkHandler(http_handler)

# Скануємо веб-сайт
url = input("Plese enter the link for crawling: ")
http_handler.handle(url)