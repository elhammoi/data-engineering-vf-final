# my_scrapy_project/pipelines.py

import pymongo

class MongoPipeline:
    def open_spider(self, spider):
        # À l'intérieur de Docker Compose, le service "mongo" sera accessible
        # via le hostname "mongo" (cf. docker-compose.yml).
        # Port par défaut : 27017
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["my_new_database"]       # Nom de ta base
        self.collection = self.db["new_nba_leaders"]   # Nom de ta collection

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.collection.insert_one(dict(item))
        return item
