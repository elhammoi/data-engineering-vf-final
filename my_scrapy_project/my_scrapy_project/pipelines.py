import pymongo

class MongoPipeline:
    def open_spider(self, spider):
        self.client = pymongo.MongoClient("mongodb://mongo:27017/")
        self.db = self.client["nba_stats"]  # <-- base renommée en "nba_stats"

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        if spider.name == "nba_leaders":
            self.db["new_nba_leaders"].insert_one(dict(item))
        elif spider.name == "nba_shooters":
            self.db["new_nba_shooters"].insert_one(dict(item))
        else:
            self.db["others"].insert_one(dict(item))
        return item
