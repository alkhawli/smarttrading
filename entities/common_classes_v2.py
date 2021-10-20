import praw
from praw.models.listing.generator import ListingGenerator
import pandas as pd
import re
import json
from entities.object_entities import Comment, MainStock, AllStocks


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
        self.subs = ["wallstreetbets", "stocks"]#, "investing", "smallstreetbets"]  # toDo add to CONSTANT file
        self.data = []

    def get_top_tickers_day(self) -> dict:
        """
        Function to get a dictionary of top tickers per sub, filtered by top "week"  #toDo Set week dynamic?
        :return: top_tickers (dict): Dictionary of tickers with their quantity in comments
        """
        main_dict = AllStocks(
            stock_list=[]
        )

        for sub in self.subs:
            main_dict = self.crawl_posts(sub=sub, main_dict=main_dict)
            #print(next((item for item in main_dict.get("stock_list") if item["name"] == "TSLA"), None))

        return main_dict

    def crawl_posts(self, sub: str, main_dict: dict):
        daily_tickers = {}
        regex_pattern = r'\b([A-Z]+)\b'  # toDo add to CONSTANT file
        ticker_dict = self.stock_list
        blacklist = ["A", "I", "DD", "WSB", "YOLO", "RH", "EV", "PE", "ETH", "BTC", "E"]  # toDo add to CONSTANT file

        post_generator = self.reddit_conn.subreddit(sub).top("day",
                                                             limit=10)  # toDo Set Limit dynamically? Higher? For testing it needs to be lower

        for post in post_generator:
            post.comments.replace_more(limit=0)

            # Kommentare iterieren
            for comment in post.comments.list():
                comment_obj = Comment(
                    body=comment.body,
                    score=comment.score
                )
                found_list = []
                for phrase in re.findall(regex_pattern, comment.body):
                    if phrase not in blacklist:
                        if phrase in ticker_dict:
                            if next((item for item in main_dict.get("stock_list") if item["name"] == phrase),
                                    None) is None:
                                main_dict['stock_list'].append(MainStock(
                                    name=phrase,
                                    mentions=1,
                                    comments=[comment_obj]
                                ))
                                found_list.append(phrase)
                            else:
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
        file_list = ["input/list1.csv", "input/list2.csv", "input/list3.csv"]  # toDo add to CONSTANT file
        for file in file_list:
            tl = pd.read_csv(file, skiprows=0, skip_blank_lines=True)
            tl = tl[tl.columns[0]].tolist()
            for ticker in tl:
                ticker_dict[ticker] = 1
        return ticker_dict

    @staticmethod
    def save_dict_as_json(dictionary: dict, file_name: str) -> None:
        """
        Save dictionary as json file in /output
        :param dictionary: dictionary to be saved
        :param file_name: file name without file extension (.json)
        :return None:
        """
        ordered_dictionary = {"stock_list": sorted(dictionary.get("stock_list"), key=lambda item: item['mentions'], reverse=True)}
        with open(f'output/{file_name}.json', 'w') as fp:
            json.dump(ordered_dictionary, fp, indent=4)
        print("File saved.")
