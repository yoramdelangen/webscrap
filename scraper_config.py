import json
from os import path


class ScraperConfig():
    config = {}
    attribute_selector = '@'

    def __init__(self, file):
        self.config = self.readConfig_(file)

    def readConfig_(self, file):
        with open(path.abspath(file+'.json'), 'r') as fp:
            return json.load(fp)

    def has(self, key):
        return key in self.config and self.config[key] is not None

    def get(self, key):
        return self.config[key]

    def getType(self):
        return self.config['type']

    def getMapping(self) -> list:
        return self.config['mapping']

    def getPagination(self) -> int:
        if 'pagination' in self.config:
            return int(self.config['pagination'])
        return None

    def getLink(self) -> str:
        if 'link' in self.config:
            return self.config['link']
        return None

    def hasRows(self) -> bool:
        return 'rows' in self.config

    def isJSON(self) -> bool:
        return 'json' in self.config and self.config['json'] is True

    def isTable(self) -> bool:
        return 'table' in self.config and self.config['table'] is True

    def hasTranslate(self) -> bool:
        return 'translate' in self.config

    def withDetails(self) -> bool:
        return 'link' in self.config

    def isJavascriptEnabled(self) -> bool:
        return 'javascript' in self.config \
            and self.config['javascript'] is True

    def hasPagination(self) -> bool:
        return 'pagination' in self.config \
            and int(self.config['pagination']) > 0

    def skipRow(self):
        if 'skip_row' in self.config:
            return self.config['skip_row']
        return None
