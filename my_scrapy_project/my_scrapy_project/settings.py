# my_scrapy_project/settings.py

BOT_NAME = "my_scrapy_project"

SPIDER_MODULES = ["my_scrapy_project.spiders"]
NEWSPIDER_MODULE = "my_scrapy_project.spiders"

ROBOTSTXT_OBEY = True

# -- PIPELINES --
ITEM_PIPELINES = {
    'my_scrapy_project.pipelines.MongoPipeline': 300,
}

FEED_EXPORT_ENCODING = "utf-8"
