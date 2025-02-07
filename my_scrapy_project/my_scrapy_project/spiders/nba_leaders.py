import scrapy

class NBALeaderSpider(scrapy.Spider):
    name = "nba_leaders"
    start_urls = ["https://www.basketball-reference.com/leagues/NBA_2025_leaders.html"]

    def parse(self, response):
        categories = {
            "Points": "leaders_pts",
            "Rebounds": "leaders_trb",
            "Assists": "leaders_ast",
            "Blocks": "leaders_blk", 
            "3-Point Field Goals": "leaders_fg3",
            "Free Throws": "leaders_ft",
            "Minutes Played": "leaders_mp",
            "Turnovers": "leaders_tov"
        }

        for category, div_id in categories.items():
            player_name = response.xpath(f'//div[@id="{div_id}"]//td[@class="who"]/a/text()').get()
            team = response.xpath(f'//div[@id="{div_id}"]//td[@class="who"]/span[@class="desc"]/text()').get()
            value = response.xpath(f'//div[@id="{div_id}"]//td[@class="value"]/text()').get()

            item = {
                "category": category,
                "player_name": player_name,
                "team": team,
                "value": value
            }
            self.log(f"Yielding item: {item}")
            yield item
