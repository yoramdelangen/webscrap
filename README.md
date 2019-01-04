# A configurable Webscarper
The aim of this package is to easly and quickly setup a webscraper based on configuration thats provider.
In early stages of certain projects and learning curve for datascience/machinelearning stuff I needed a simple webscraper. Because my backgroud is mainly webdevelopement I exacly knew what kind of confiugration and accessability the scraper should have.

Ultimately it should be less then 20 lines of configuration to scarper thousands of records pages etc.

> I'am not responsible in any way of usage.

## TODOS
There is still alot todo and everytime I'm using this package I'll try to improve it or create more accurate documentation.
- Improve inline docblocks
- Configuration examples
- Example code
- ....

## Common scenario's
There are different scenario's for scraping data and each of these scenario's the package tend to cover:
1. Single page with recurring records (overview)
2. Overview page (with pagination) with detail pages and scrape only data from the detail pages.
3. Pages with `<table />` data.
4. JSON api/payload.

## Configs/Configuration
Within the `mapping` object we define the properties.

These properties are defined by default:
```
"mapping": {
    "name": "td.naam",
    "street": "td.straat",
    "zipcode": "td.postcode",
    "city": "td.plaats"
}
```

> By default it will always get the `text` from the inner HTML of an element. Whenever you want a property of an attribute it can be specified after a `|`.

Example of getting a property as value:
```
    // if you want the `href` property of the attribute
    "site": "a.socialmedia.social-facebook|href",
```

Sometimes its necessary to skip when certain elements are within the rows
```
    // When `.find()` does not return `None` it will conitnue
    "skip_row": ".selector",
```

### Enabling javascript
Very easily to enable javascript waiting:
```
    "javascript": true,
```

### Using selectors
First we need to get a list of rows with single data:
```
    "selectors": {
        "container": ".bedrijventabel",
        "rows": "tbody > tr"
    },

```

### table style
Using pandas `pd.read_html()` method.


### Use mapping for the detail page
Sometimes the proper data isnt showing on the "index" page, but on the detail page. In that case it is possible to follow the "link" to the detail page.

```
    // the `a[href="*"]` to follow and so the "link" should be an <a> attribute
    "link": ".sabai-entity-permalink",
```

> The script will first retrieve all links and afterwards following it to the detail page.

#### Using GEO (TODO)
```
"geo": {
    // is geo enabled or not
    "enabled": false,
    // what fields do we need to
    "search": ["street", "zipcode", "city"],
    // response to store the output in:
    "field": "geo"
}
```
