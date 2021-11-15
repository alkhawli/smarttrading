from scrape_entities.connection_details import CONNECTION
from scrape_entities.common_classes_v2 import RedditConnector, RedditCrawler
from commons.env import assign_stack, Stacks

from cleanse_data.sentimentanalysis import SentimentAnalysis
from praw import Reddit
from typing import Tuple


def main():
    # Assigning a stack
    assign_stack(Stacks('dev'))

    # SCRAPING
    result_dict, json_key = crawl_reddit(reddit_conn=connect_to_reddit(), file_name="top_tickers_v3")

    # CLEANSING
    cleanse_data()  # todo seperate cleansing and analysis part, set dynamic parameters for output?
                    # todo Just json file or also a dict?


def connect_to_reddit() -> Reddit:
    reddit_conn = RedditConnector(CONNECTION).return_connector()
    return reddit_conn


def crawl_reddit(reddit_conn: Reddit, file_name: str, add_stock_values: bool = False) -> Tuple[dict, str]:
    crawler = RedditCrawler(reddit_conn=reddit_conn)
    top_tickers_week = crawler.get_top_tickers_day()
    if add_stock_values:
        top_tickers_week = crawler.add_actual_stock_value(stock_dictionary=top_tickers_week)  # Takes long time
    file_key = crawler.save_dict_as_json(top_tickers_week, file_name)
    return top_tickers_week, file_key


def cleanse_data():
    SentimentAnalysis().run()


main()
