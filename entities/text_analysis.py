import nltk
nltk.download('vader_lexicon')
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json

with open("C:/Users/muell/Projekte/smarttrading/output/top_tickers_v2.json", "r") as f:
    x = json.load(f)

print(x['stock_list'][0].get("comments")[0])


sid = SentimentIntensityAnalyzer()
y=sid.polarity_scores(x['stock_list'][0].get("comments")[0]['body'])
print(y)
y=sid.polarity_scores("THIS IS AWESOME!")
print(y)
y=sid.polarity_scores("THIS WAS SO BAD!")
print(y)