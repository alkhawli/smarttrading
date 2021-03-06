import praw
from praw.models.listing.generator import ListingGenerator
import pandas as pd
import re
import json
from scrape_entities.object_entities import Comment, MainStock, AllStocks


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
        self.subs = ["wallstreetbets", "stocks", "investing", "smallstreetbets"]  # toDo add to CONSTANT file
        self.data = []

    def get_top_tickers_day(self) -> dict:
        """
        Function to get a dictionary of top tickers per sub, filtered by top "week"  #toDo Set week dynamic?
        :return: top_tickers (dict): Dictionary of tickers with their quantity in comments
        """
        top_tickers = {}
        for sub in self.subs:
            daily_tickers = self._get_daily_tickers(sub)
            for ticker in daily_tickers.keys():
                if ticker in top_tickers:
                    top_tickers[ticker] += daily_tickers[ticker]
                else:
                    top_tickers[ticker] = daily_tickers[ticker]
        return top_tickers

    def _get_daily_tickers(self, sub: str) -> dict:
        """
        Internal function to get list_generator and create daily_tickers by sub
        :param sub (str): sub that defines where to search
        :return weekly_tickers (dict): returns the weekly dict per sub
        """
        list_generator = self.reddit_conn.subreddit(sub).top("day",
                                                             limit=2)  # toDo Set Limit dynamically? Higher? For testing it needs to be lower
        return self._iterate_subreddit(list_generator=list_generator)

    def _iterate_subreddit(self, list_generator: ListingGenerator) -> dict:
        """
        Function to iterate over subreddits and filter commands for phrases
        :param list_generator: List generator for comments
        :return: dictionary of daily tickers
        """
        daily_tickers = {}
        regex_pattern = r'\b([A-Z]+)\b'  # toDo add to CONSTANT file
        ticker_dict = self.stock_list
        blacklist = ["A", "I", "DD", "WSB", "YOLO", "RH", "EV", "PE", "ETH", "BTC", "E"]  # toDo add to CONSTANT file

        for post in list_generator:
            # print(submission.score)  # Shows Score of a post
            strings = [post.title]
            post.comments.replace_more(limit=0)
            comments = []
            for comment in post.comments.list():
                strings.append(comment.body)
                comments.append({"score": comment.score,
                                 "body": comment.body})

            item = {"title": post.title,
                    "score": post.score,
                    "url": post.url,
                    "comments": comments}
            for s in strings:
                for phrase in re.findall(regex_pattern, s):
                    if phrase not in blacklist:
                        if phrase in ticker_dict:
                            if phrase not in daily_tickers:
                                daily_tickers[phrase] = 1
                            else:
                                daily_tickers[phrase] += 1

            self.data.append(item)

        # all_stocks_obj = AllStocks(
        #     stock_list=[main_stock_obj]
        # )
        # print(all_stocks_obj)
        # print(daily_tickers)
        return daily_tickers

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
        ordered_dictionary = {k: v for k, v in sorted(dictionary.items(), key=lambda item: item[1], reverse=True)}
        with open(f'output/{file_name}.json', 'w') as fp:
            json.dump(ordered_dictionary, fp, indent=4)
        print("File saved.")

    def save_all_dailyscraped_as_json(self):
        with open('output/dailydata.json', 'w') as outfile:
            json.dump(self.data, outfile, indent=4)
