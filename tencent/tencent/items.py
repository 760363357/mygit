# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy



class TencentItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    topic_id = scrapy.Field()
    topic_link = scrapy.Field()


class StatItem(scrapy.Item):
    topic = scrapy.Field()
    topic_follow_num = scrapy.Field()
    topic_que_num = scrapy.Field()
    topic_essence10 = scrapy.Field()


class AnserwItem(scrapy.Item):
    topic = scrapy.Field()
    title = scrapy.Field()
    follow_num = scrapy.Field()
    scan_num = scrapy.Field()
    total_answer_num = scrapy.Field()
    answer_content = scrapy.Field()
    # answer_agree = scrapy.Field()
    mode = scrapy.Field()
    topics = scrapy.Field()
