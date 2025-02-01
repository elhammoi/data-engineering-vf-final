# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from pymongo import MongoClient

class MongoPipeline:
    def __init__(self):
        # Connexion à MongoDB
        self.client = MongoClient("mongodb://mongodb:27017/")
        self.db = self.client["nba_database"]
        self.collection = self.db["nba_stats"]

    def process_item(self, item, spider):
        # Insertion des données dans MongoDB
        self.collection.insert_one(dict(item))
        return item

    def close_spider(self, spider):
        self.client.close()  # Fermer la connexion MongoDB


class MonprojetPipeline:
    def process_item(self, item, spider):
        return item

