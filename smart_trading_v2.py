from entities.secret_string import CONNECTION
from entities.common_classes_v2 import RedditConnector, RedditCrawler
from commons.env import assign_stack, Stacks


def main():
    assign_stack(Stacks('dev'))
    reddit_conn = RedditConnector(CONNECTION).return_connector()
    crawler = RedditCrawler(reddit_conn=reddit_conn)
    top_tickers_week = crawler.get_top_tickers_day()
    #top_tickers_week_with_actual_stock_value = crawler.add_actual_stock_value(stock_dictionary=top_tickers_week) #Takes long time
    crawler.save_dict_as_json(top_tickers_week, "top_tickers_v2")


main()
