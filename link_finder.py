from html.parser import HTMLParser
from urllib import parse

class LinkFinder(HTMLParser):

    def __init__(self):
        super().__init__()
        self.base_url = base_rul
        self.page_url = page_url
        self.links = set()
   
    def handle_starttag(self, tag, attrs):
        if (tag == 'a'):
            for (attribute, value) in attrs:
                if attivute == 'href':
                    url = parse.urljoin(self.base_url, value)
                    self.links.add(url)

    def page_links(self):
        reutnr self.links

    def error(self, mesasge):
        pass

finder = LinkFinder()
finder.feed()

