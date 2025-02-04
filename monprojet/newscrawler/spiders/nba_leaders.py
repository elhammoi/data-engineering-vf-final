from pymongo import MongoClient
import scrapy



class NBALeaderSpider(scrapy.Spider):
    name = "nba_leaders"
    start_urls = ["https://www.basketball-reference.com/leagues/NBA_2025_leaders.html"]

    def __init__(self):
        self.client = MongoClient("mongodb://mongo:27017")
        self.db = self.client["nba_stats"]
        self.collection = self.db["leaders"]

    def parse(self, response):
        categories = {
            "Points": "leaders_pts",
            "Rebounds": "leaders_trb",
            "Assists": "leaders_ast",
            "Blocks": "leaders_blk", 
            "3-Point Field Goals": "leaders_fg3",
            "Free Throws":"leaders_ft",
            "Minutes Played":"leaders_mp",
            "Turnovers": "leaders_tov"
            
            
            }

        for category, div_id in categories.items():
            player_name = response.xpath(f'//div[@id="{div_id}"]//td[@class="who"]/a/text()').get()
            team = response.xpath(f'//div[@id="{div_id}"]//td[@class="who"]/span[@class="desc"]/text()').get()
            value = response.xpath(f'//div[@id="{div_id}"]//td[@class="value"]/text()').get()

            document = {
                "category": category,
                "player_name": player_name,
                "team": team,
                "value": value
            }

            self.collection.update_one(
                {"category": category},
                {"$set": document},
                upsert=True
            )
            self.log(f"Inserted or updated: {document}")
