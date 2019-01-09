from webscrap import Scraper, Config

funda = {
    "url": "https://www.funda.nl/koop/oldenzaal/verkocht/",
    "javascript": True,
    "rows": ".search-content-output .search-results",
    "mapping": {
        "address": ".search-result-title",
        "price": ".search-result-price",
        "status": ".label-transactie-definitief",
        "surface": ".search-result-kenmerken span[title^=Gebruiksoppervlakte]",
        "parcel": ".search-result-kenmerken span[title=Perceeloppervlakte]",
        "link": ".search-result-header > a | href"
    }
}

# create Scraper instance
scraper = Scraper(['address', 'price', 'surface', 'status', 'parcel', 'link'])

# Set scraper Config instance
config = Config(funda)

# set config for current itteration - this case
scraper.setConfig(config)

# Start scraping the page
scraper.scrapePage(config.get('url'))

# get all data scraped from the pages in a Pandas.
df = scraper.getDataset()

print(df)
