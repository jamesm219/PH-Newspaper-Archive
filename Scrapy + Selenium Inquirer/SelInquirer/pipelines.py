# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class SelinquirerPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        article = adapter['article']
        
        # Remove specified strings from the 'article' field
        strings_to_remove = ["ADVERTISEMENT", "ADVERTISEMENT", "READ NEXT", "EDITORS' PICK", "MOST READ", "View comments"]
        for string in strings_to_remove:
            if string in article:
                article.remove(string)

        return item