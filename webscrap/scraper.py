from .scraper_config import ScraperConfig as Config
import pandas as pd
from requests_html import HTMLSession
from dpath.util import get as dget
from sqlalchemy.engine import Engine


class Scraper():
    collections = []
    fields = []
    session = HTMLSession()
    attribute_selector = '@'
    collectionsPath = 'collection'

    def __init__(self, fields=[], collections=[]):
        self.fields = fields
        self.df = pd.DataFrame(columns=fields)
        self.collections = collections

    def fields(self, fields: list):
        """
        Manually set the fields/output values to holdon
        for the output values.
        """
        self.fields = fields
        self.df = pd.DataFrame(columns=fields)

    def collections(self, collections: list):
        """
        Set a list of colllections to use the
        configuration from while scraping.
        """
        self.collections = collections

    def setConfig(self, config: Config):
        self.config = config

    def destructCollection(self):
        self.config = None

    def getCollections(self) -> list:
        return [self.collectionsPath+'/'+c for c in self.collections]

    def scrapeTables(self, config: Config) -> bool:
        self.checkCollector_()

        print('Start reading: '+config.get('url'))

        rsp = pd.read_html(config.get('url'))
        tbl = rsp[config.get('table_index')]

        mapping = config.getMapping()

        # filter out the only values we need
        grp = tbl.filter(mapping.values(), axis=1)
        # fix column names
        grp.columns = mapping.keys()
        grp['type'] = config.getType()
        grp['source'] = config.get('url')

        # Add to final
        self.df = pd.concat([self.df, grp], sort=False)

        return True

    def scrapeJSON(self, config: Config) -> bool:
        self.checkCollector_()

        if not config.hasRows():
            raise Exception('Cannot scrape single page because `rows` was not set.')

        # print('Start reading JSON: '+ config.get('url'))
        # print('')

        url = config.get('url')
        range_ = range(1, 2)
        separator_ = '.'
        if config.hasPagination():
            range_ = range(1, config.getPagination()+1)

        for i in range_:
            if config.hasPagination():
                url = url.format(i)
                # print('Scraping page: ', i)

            # call the url and get HTMLSession
            r = self.call_(url)
            if r.status_code != 200:
                print('ERROR: ', r.status_code)
                print('HTML: ', r.html.raw_html)
                print('HEADERS RESPONSE: ', r.headers)
                print('HEADERS REQUEST: ', r.request.headers)
                return False

            r = r.json()
            mppng = config.getMapping()
            rows = dget(r, config.get('rows'), separator=separator_)
            out = map(lambda x: ({k: dget(x, path, separator=separator_) for k, path in mppng.items()}), rows)
            grp = pd.DataFrame(list(out), columns=mppng.keys())
            grp['source'] = url

            if config.hasTranslate():
                for f in config.get('translate'):
                    symbols = self.getTranslateSymbols_()
                    grp[f] = grp[f].apply(lambda x: x.translate(symbols))

            self.df = pd.concat([self.df, grp], sort=False)

        return True

    def scrapePage(self, url: str):
        """
        Start scraping the page from the given URL.
        Whenever within the config the javascript is
        enabled wait till the javacsript is finished.
        """
        self.checkCollector_()

        if not self.config.hasRows():
            raise Exception('Cannot scrape single page because `rows` was not set.')

        # print('Start reading: '+ url)
        # print('')

        # call the url and get HTMLSession
        r = self.call_(url)

        if r is None:
            return False

        # do we need to enable javascript?
        if self.config.isJavascriptEnabled():
            r.html.render()

        rows = r.html.find(self.config.get('rows'))
        # print('Total rows:', len(rows))
        for row in rows:
            # do we need to skip this row
            if self.skipThisRow_(row):
                continue

            # whennot a link, get from the current HTML
            self.scrapeFromHtml_(self.config, row)

    def scrapePageWithDetails(self, url: str):
        self.checkCollector_()
        if not self.config.hasRows():
            raise Exception('Cannot scrape single page because `rows` was not set.')

        # print('Start reading: '+ url)
        # print('')

        # call the url and get HTMLSession
        r = self.call_(url)

        if r.status_code != 200:
            return False

        # do we need to enable javascript?
        if self.config.isJavascriptEnabled():
            r.html.render()

        links = []
        rows = r.html.find(self.config.get('rows'))
        print('Total rows:', len(rows))
        for row in rows:
            # do we need to skip this row
            if self.skipThisRow_(row):
                continue

            # When 'link' is set, there is.
            link = row.find(self.config.getLink(), first=True)
            links.append(link.attrs['href'])
            print('added link', link.attrs['href'])

        # When we have details, loop through all links
        # and fetch those HTML
        print('Total links: ', len(links))
        print('Fetch data from the following links')
        print('')

        for link in links:
            r = self.call_(link)
            print('URL: ', link)

            # do we need to enable javascript?
            if self.config.isJavascriptEnabled():
                r.html.render()

            item = self.scrapeFromHtml_(self.config, r.html, link)
            self.df = self.df.append(item, ignore_index=True)

            print('---------------------------')

    def getDataset(self):
        return self.df

    def save(self, file: str):
        self.df.to_csv(file, encoding='utf-8-sig')
        return self.df

    def saveDB(self, tname: str, engine: Engine):
        self.checkCollector_()

        self.df.to_sql(tname, con=engine, if_exists='replace', index_label='id')

        return self.df

    def checkCollector_(self):
        if not hasattr(self, 'df'):
            raise Exception('Fields are not set yet.')

    def skipThisRow_(self, row) -> bool:
        return self.config.skipRow() and row.find(self.config.skipRow(), first=True) is not None

    def call_(self, url: str):
        if self.config.has('prerequest') and self.config.get('prerequest') is True:
            self.session.get(url)

        r = self.session.get(url)

        if r.status_code != 200:
            print('ERROR: ', r.status_code)
            print('HTML: ', r.html.raw_html)
            print('HEADERS RESPONSE: ', r.headers)
            print('HEADERS REQUEST: ', r.request.headers)
            return

        return r

    def scrapeFromHtml_(self, config: Config, r, source=None) -> dict:
        mapping = self.config.getMapping()
        item = mapping.copy()

        if source is None:
            source = self.config.get('url')

        if self.config.has('type'):
            item['type'] = self.config.getType()
        item['source'] = source

        for key, selector in mapping.items():
            if selector is None:
                item[key] = None
                continue

            # default its getting the 'text'
            attr = None
            if self.attribute_selector in selector:
                selector, attr = selector.split(self.attribute_selector)
                attr = attr.strip()

            elm = r.find(selector, first=True)

            # print('SELECTOR:', selector, 'FOUND: ', elm)
            if elm is None:
                print(key, 'was not found in HTML')
                item[key] = None
            elif attr is None:
                item[key] = elm.text
            else:
                item[key] = elm.attrs[attr]

        self.df = self.df.append(item, ignore_index=True)
        return item

    def getTranslateSymbols_(self):
        symbols = (
            u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
            u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA"
        )

        return {ord(a): ord(b) for a, b in zip(*symbols)}
