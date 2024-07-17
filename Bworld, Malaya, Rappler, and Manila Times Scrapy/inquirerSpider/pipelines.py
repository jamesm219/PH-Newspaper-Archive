# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class InquirerspiderPipeline:
    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        article = adapter['article']
        
        # Remove specified strings from the 'article' field
        strings_to_remove = ["ADVERTISEMENT", "ADVERTISEMENT", "READ NEXT", "EDITORS' PICK", "MOST READ", "View comments"]
        for string in strings_to_remove:
            if string in article:
                article.remove(string)

        return item


import mysql.connector

class SaveToMySQLPipeline:

    def __init__(self):
        self.conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Getgood1234",
        database="ph_newspaper"
)
        self.cur = self.conn.cursor()

    def process_item(self, item, spider):
        self.cur.execute("""INSERT INTO philstar(title, author, date, article, link) 
                         VALUES (%s, %s, %s, %s, %s)""", (item['title'], item['author'], item['date'], item['article'], item['link']))
        self.conn.commit()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()