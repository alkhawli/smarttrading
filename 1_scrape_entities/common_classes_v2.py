import praw
from praw.models.listing.generator import ListingGenerator
import pandas as pd
import re
import json
import logging
from yahoo_fin import stock_info as si

from scrape_entities.object_entities import Comment, MainStock, AllStocks
from commons.env import get_config, Vars

logging.getLogger().setLevel(logging.INFO)


class RedditConnector:
    def __init__(self, connection: dict):
        self.CONNECTION = connection

    def return_connector(self) -> praw.Reddit:
        reddit_conn = praw.Reddit(
            client_id=self.CONNECTION.get("client_id", ""),
            client_secret=self.CONNECTION.get("client_secret", ""),
            username=self.CONNECTION.get("username", ""),
            password=self.CONNECTION.get("password", ""),
            user_agent=self.CONNECTION.get("user_agent", ""),
        )
        return reddit_conn


class RedditCrawler:
    def __init__(self, reddit_conn: praw.Reddit):
        """
        Class to crawl reddit feeds, commends etc.
        :param reddit_conn: Reddit Connector to build a connection to reddit
        """
        self.reddit_conn = reddit_conn
        self.stock_list = self._get_stock_list()
        self.subs = get_config(Vars.SUBS_TO_CRAWL)
        self.data = []

    def get_top_tickers_day(self) -> AllStocks:
        """
        Function to get a dictionary of top tickers per sub, filtered by top "week"  #toDo Set week dynamic?
        :return: top_tickers (dict): Dictionary of tickers with their quantity in comments
        """
        main_dict = AllStocks(
            stock_list=[]
        )

        for sub in self.subs:
            main_dict = self._crawl_posts(sub=sub, main_dict=main_dict) #todo filter for thresholds

        return main_dict

    def _crawl_posts(self, sub: str, main_dict: dict) -> dict:
        """
        Function to crawl posts and iterate through the comments in a post
        :param sub: string of subreddit name
        :param main_dict: main_dictionary where all stocks are listed AllStocks{..}
        :return: updated main_dict with comments (crawled)
        """
        post_generator = self.reddit_conn.subreddit(sub).top("day", limit=10)  # toDo Set Limit dynamically? Higher? For testing it needs to be lower

        for post in post_generator:
            post.comments.replace_more(limit=0)

            for comment in post.comments.list():
                main_dict = self._crawl_comment(comment=comment, main_dict=main_dict)

        return main_dict

    def _crawl_comment(self, comment, main_dict: dict) -> dict:
        """
        Function to iterate over comments and search for phrases, add them to the main_dict and return it
        :param comment: comment in a post
        :param main_dict: main_dictionary where all stocks are listed AllStocks{..}
        :return: updated main_dict
        """
        regex_pattern = get_config(Vars.REGEX_PATTERN_STOCKS)
        ticker_dict = self.stock_list
        blacklist = get_config(Vars.STOCK_BLACKLIST)

        # IF CLAUSE FOR THRESHOLD
        if get_config(Vars.COMMENT_THRESHOLD_LOWER) < comment.score < get_config(Vars.COMMENT_THRESHOLD_UPPER):
            return main_dict

        comment_obj = Comment(
            body=comment.body,
            score=comment.score
        )
        found_list = []

        # Looks for phrase in comment.body
        for phrase in re.findall(regex_pattern, comment.body):
            if phrase not in blacklist:
                if phrase in ticker_dict:
                    # Adds a MainStock obj to the dictionary if the phrase not exists
                    if next((item for item in main_dict.get("stock_list") if item["name"] == phrase), None) is None:
                        new_stock = MainStock(
                            name=phrase,
                            actual_stock_value="",
                            mentions=1,
                            comments=[comment_obj]
                        )
                        main_dict['stock_list'].append(new_stock)
                        found_list.append(phrase)
                    else:
                        # Adds comment to list and count mention +1 if phrase found
                        if phrase not in found_list:
                            next((item for item in main_dict.get("stock_list") if item["name"] == phrase), None)['mentions'] += 1
                            next((item for item in main_dict.get("stock_list") if item["name"] == phrase), None)['comments'].append(comment_obj)
                            found_list.append(phrase)
        return main_dict

    @staticmethod
    def _get_stock_list() -> dict:
        """
        Internal static method to get stock_list from files (input..)
        :return ticker_dict (dict): dictionary of tickers from files
        """
        ticker_dict = {}
        file_list = get_config(Vars.INPUT_FILE_LIST)
        for file in file_list:
            tl = pd.read_csv(file, skiprows=0, skip_blank_lines=True)
            tl = tl[tl.columns[0]].tolist()
            for ticker in tl:
                ticker_dict[ticker] = 1
        return ticker_dict

    @staticmethod
    def add_actual_stock_value(stock_dictionary: AllStocks) -> AllStocks:
        """
        Function to add actual stock value to dictionary
        :param stock_dictionary: Prepared AllStock dictionary
        :return: AllStock dictionary extended with actual stock values
        """
        for key in stock_dictionary.get("stock_list", []):
            try:
                stock_value = str(si.get_live_price(key.get("name", "")))
            except:
                stock_value = "Can not be extracted."
            key['actual_stock_value'] = stock_value

        return stock_dictionary

    @staticmethod
    def save_dict_as_json(dictionary: dict, file_name: str) -> str:
        """
        Save dictionary as json file in /output
        :param dictionary: dictionary to be saved
        :param file_name: file name without file extension (.json)
        :return None:
        """
        ordered_dictionary = {
            "stock_list": sorted(dictionary.get("stock_list"), key=lambda item: item['mentions'], reverse=True)}
        file_key = f'output/{file_name}.json'
        with open(file_key, 'w') as fp:
            json.dump(ordered_dictionary, fp, indent=4)
        logging.info("File saved.")
        return file_key
