from scrape_entities.connection_details import CONNECTION
from archive.attempt3_toufik_nick.common_classes import RedditConnector, RedditCrawler


def main():
    reddit_conn = RedditConnector(CONNECTION).return_connector()
    crawler = RedditCrawler(reddit_conn=reddit_conn)
    top_tickers_week = crawler.get_top_tickers_day()
    #crawler.save_all_dailyscraped_as_json()
    #crawler.save_dict_as_json(top_tickers_week, "top_tickers2")


main()
