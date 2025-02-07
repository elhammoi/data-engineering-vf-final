import scrapy

class NbaShootersSpider(scrapy.Spider):
    name = "nba_shooters"
    start_urls = ["https://www.basketball-reference.com/leagues/NBA_2025_totals.html"]

    def parse(self, response):
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
            # On "yield" l'item (Python dict), et c'est le pipeline qui l'insère
            yield item
