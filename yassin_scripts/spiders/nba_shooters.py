from pymongo import MongoClient
import scrapy

class NBALeaderSpider2(scrapy.Spider):
    name = "nba_shooters"
    start_urls = ["https://www.basketball-reference.com/leagues/NBA_2025_totals.html"]

    def __init__(self):
        self.client = MongoClient("mongodb://mongo:27017")
        self.db = self.client["nba_stats"]
        self.collection = self.db["shooters"]

    def parse(self, response):
        # Select the top 10 rows from the table
        rows = response.xpath("//table[contains(@class, 'stats_table')]/tbody/tr[position() <= 10]")

        for row in rows:
            item = {
                "rank": row.xpath("th[@data-stat='ranker']/text()").get(default="N/A"),
                "name": row.xpath("td[@data-stat='name_display']/a/text()").get(default="N/A"),
                "age": row.xpath("td[@data-stat='age']/text()").get(default="N/A"),
                "position": row.xpath("td[@data-stat='pos']/text()").get(default="N/A"),
                "team": row.xpath("td[@data-stat='team_name_abbr']/a/text()").get(default="N/A"),
                "points": row.xpath("td[@data-stat='pts']//text()").get(default="N/A")
            }
            self.collection.insert_one(item)
            yield item

    def closed(self, reason):
        self.client.close()
