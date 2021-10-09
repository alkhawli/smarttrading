from entities.secret_string import CONNECTION
from entities.common_classes import RedditConnector, RedditCrawler


def main():
    reddit_conn = RedditConnector(CONNECTION).return_connector()
    crawler = RedditCrawler(reddit_conn=reddit_conn)
    top_tickers_week = crawler.get_top_tickers_week()
    crawler.save_dict_as_json(top_tickers_week, "top_tickers")


main()
