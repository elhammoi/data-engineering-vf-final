import scrapy
import re

class NBATotalsSpider(scrapy.Spider):
    name = "nba_totals"
    allowed_domains = ["basketball-reference.com"]
    start_urls = [
        "https://www.basketball-reference.com/leagues/NBA_2025_totals.html"
    ]

    def parse(self, response):
        # Compiler la regex avec le flag DOTALL pour capturer le tableau sur plusieurs lignes
        pattern = re.compile(r'(<table[^>]*id="totals_stats"[^>]*>.*?</table>)', re.DOTALL)
        
        # Extraire le contenu du tableau depuis les commentaires HTML
        table_html = response.xpath('//comment()').re_first(pattern)
        
        if table_html:
            # Créer un nouveau sélecteur à partir du contenu HTML extrait
            table = scrapy.Selector(text=table_html)
        else:
            # Si le tableau n'est pas dans un commentaire, utiliser directement la réponse
            table = response

        # Récupérer les entêtes du tableau (<th>) pour constituer la liste des colonnes
        headers = table.xpath('.//thead/tr/th/text()').getall()
        headers = [h.strip() for h in headers if h.strip()]
        if not headers:
            headers = [
                "Rk", "Player", "Age", "Team", "Pos", "G", "GS", "MP",
                "FG", "FGA", "FG%", "3P", "3PA", "3P%", "2P", "2PA",
                "2P%", "eFG%", "FT", "FTA", "FT%", "ORB", "DRB", "TRB",
                "AST", "STL", "BLK", "TOV", "PF", "PTS", "Trp-Dbl", "Awards"
            ]

        # Récupérer les lignes du corps du tableau (<tr>) qui contiennent des cellules <td>
        rows = table.xpath('.//tbody/tr')
        for row in rows:
            # Extraire le texte de toutes les cellules <td>
            values = row.xpath('.//td//text()').getall()
            values = [v.strip() for v in values if v.strip()]
            if values:
                # Créer un dictionnaire en associant chaque valeur à son entête
                item = {header: (values[i] if i < len(values) else None)
                        for i, header in enumerate(headers)}
                yield item
