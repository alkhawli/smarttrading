import praw
import re
import pandas as pd
import config
import discord
import time
import robin_stocks
from rich.traceback import install
import pyotp
install()
import pandas as pd
import datetime
def get_stock_list():
    ticker_dict = {}
    filelist = ["input/list1.csv", "input/list2.csv", "input/list3.csv"]
    for file in filelist:
        tl = pd.read_csv(file, skiprows=0, skip_blank_lines=True)
        tl = tl[tl.columns[0]].tolist()
        for ticker in tl:
            ticker_dict[ticker] = 1
    return ticker_dict


def get_prev_tickers():
    prev = open("output/prev.txt", "r")
    prevTickers = prev.readlines()
    prev.close()
    return prevTickers

def get_date(created):
    return datetime.datetime.fromtimestamp(created)

def get_tickers(stockList):
    reddit = praw.Reddit(
        client_id="DW05MNldhBiRxA",
        client_secret="crxcx6X53iMt8itg-elTv1mQ0jm7BA",
        user_agent="WSB Scraping",
        check_for_async=False
    )
    weeklyTickers = {}
    regexPattern = r'\b([A-Z]+)\b'
    tickerDict = stockList
    dfdata=pd.DataFrame([])
    subs = ["wallstreetbets", "stocks", "investing", "smallstreetbets"]
    for sub in subs:
        for submission in reddit.subreddit(sub).top("day"):
            print(submission)
            strings = submission.title
            scores= submission.score
            num_comments= submission.num_comments
            url= submission.url
            timestamp= get_date(submission.created_utc)
            print(strings)
            print(scores)
            print(num_comments)
            print(url)
            submission.comments.replace_more(limit=0)
            dfdata=dfdata.append({
                'Subs':sub,
                'Timestamp': timestamp,
                'Type': 'Post',
                'Title': strings,
                'Scores':scores,
                'Num_Comments': num_comments,
                'url': url}, ignore_index=True)
            for comment in submission.comments.list():
                dfdata=dfdata.append({
                    'Subs':sub,
                    'Timestamp': get_date(comment.created_utc),
                    'Type': 'Comment',
                    'Title': comment.body,
                    'Scores':comment.score,
                    'Num_Comments': 0,
                    'url': url}, ignore_index=True)
    return dfdata


def write_to_file(df,filename): 
    return df.to_csv(filename,index=False)



def main():
    prevTickers = get_prev_tickers()
    stockList = get_stock_list()

    weeklyTickers = get_tickers(stockList)
    write_to_file(weeklyTickers, "outcomes.csv")
    #     print(weeklyTickers)
    #     for ticker in weeklyTickers.keys():
    #         print(ticker)
    #         if ticker in topTickers:
    #             topTickers[ticker] += weeklyTickers[ticker]
    #         else:
    #             topTickers[ticker] = weeklyTickers[ticker]

    # top5 = sorted(topTickers, key=topTickers.get, reverse=True)[:5]
    # toBuy = []
    # toSell = []
    # for top in top5:
    #     if top not in prevTickers:
    #         toBuy.append(top)
    # for prev in prevTickers:
    #     prev = prev.strip()
    #     if prev not in top5:
    #         toSell.append(prev)

    # write_to_file("output/actions.txt", toBuy, toSell)
   # robinbot(toBuy, toSell)
   # prev = open("output/prev.txt", "w")
   # toBuy = [buy+'\n' for buy in toBuy]
    #prev.writelines(toBuy)
    #prev.close()
    #discordbot(stf(["actions"]))


if __name__ == '__main__':
    main()
