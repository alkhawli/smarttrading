from A_scrape_entities.connection_details import CONNECTION
from A_scrape_entities.common_classes_v2 import RedditConnector, RedditCrawler
from commons.env import assign_stack, Stacks

from B_cleanse_data.sentimentanalysis import SentimentAnalysis
from praw import Reddit
from typing import Tuple
import json

def main():
    # Assigning a stack
    assign_stack(Stacks('dev'))

    # SCRAPING
    result_dict, json_key = crawl_reddit(reddit_conn=connect_to_reddit(), file_name="top_tickers_v3")

    #with open('./output/top_tickers_v3.json') as f:
    #    result_dict = json.load(f)
    #    print(result_dict)

    # CLEANSING
    cleanse_data(result_dict)  # todo seperate cleansing and analysis part, set dynamic parameters for output?
    # todo Just json file or also a dict?


def connect_to_reddit() -> Reddit:  # todo add Docstrings
    reddit_conn = RedditConnector(CONNECTION).return_connector()
    return reddit_conn


def crawl_reddit(reddit_conn: Reddit, file_name: str, add_stock_values: bool = False) -> Tuple[dict, str]: # todo add Docstrings
    crawler = RedditCrawler(reddit_conn=reddit_conn)
    top_tickers_week = crawler.get_top_tickers_day()
    if add_stock_values:
        top_tickers_week = crawler.add_actual_stock_value(stock_dictionary=top_tickers_week)  # Takes long time
    file_key = crawler.save_dict_as_json(top_tickers_week, file_name)
    return top_tickers_week, file_key


def cleanse_data(jsonobject): # todo add Docstrings
    SentimentAnalysis(jsonobject).run()


main()
