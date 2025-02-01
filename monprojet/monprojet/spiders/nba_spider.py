import scrapy
from scrapy_splash import SplashRequest

class NBASpider(scrapy.Spider):
    name = "nba_spider"
    start_urls = ["https://www.basketball-reference.com/leagues/NBA_2023.html"]

    # Script Lua pour Splash : attend le rendu complet de la page
    lua_script = """
    function main(splash, args)
        splash:go(args.url)
        splash:wait(1)  -- Attendre 1 seconde pour permettre le rendu complet
        return {
            html = splash:html()
        }
    end
    """

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(
                url=url,
                callback=self.parse,
                endpoint="execute",
                args={"lua_source": self.lua_script},
                dont_filter=True  # Pour éviter que Scrapy ignore les URL déjà visitées
            )

    def parse(self, response):
        # Extraire les données de la table après le rendu HTML
        rows = response.css("table#per_game-team tbody tr")

        for row in rows:
            yield {
                "team": row.css("td[data-stat='team'] a::text").get(),
                "games_played": row.css("td[data-stat='g']::text").get(),
                "minutes_per_game": row.css("td[data-stat='mp']::text").get(),
                "field_goals": row.css("td[data-stat='fg']::text").get(),
                "field_goal_attempts": row.css("td[data-stat='fga']::text").get(),
                "field_goal_percentage": row.css("td[data-stat='fg_pct']::text").get(),
                "three_pointers": row.css("td[data-stat='fg3']::text").get(),
                "three_point_attempts": row.css("td[data-stat='fg3a']::text").get(),
                "three_point_percentage": row.css("td[data-stat='fg3_pct']::text").get(),
                "free_throws": row.css("td[data-stat='ft']::text").get(),
                "free_throw_attempts": row.css("td[data-stat='fta']::text").get(),
                "free_throw_percentage": row.css("td[data-stat='ft_pct']::text").get(),
                "total_rebounds": row.css("td[data-stat='trb']::text").get(),
                "assists": row.css("td[data-stat='ast']::text").get(),
                "steals": row.css("td[data-stat='stl']::text").get(),
                "blocks": row.css("td[data-stat='blk']::text").get(),
                "turnovers": row.css("td[data-stat='tov']::text").get(),
                "points": row.css("td[data-stat='pts']::text").get(),
            }
