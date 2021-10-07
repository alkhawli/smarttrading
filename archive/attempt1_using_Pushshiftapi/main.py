import datetime
import pandas as pd
from smartstocker import *


print("="*100)
today = datetime.date.today()
yesterday = today - datetime.timedelta(days = 1)
data_from = yesterday.strftime("%Y-%m-%d")
print(f"Getting data for: {data_from}")

df = collect_data(
    day_ = yesterday.day, 
    month_ = yesterday.month,     
    year_ = yesterday.year,     
    verbose = False,     
    writefile = False    
    )

df = text_preprocessing(
    df = df, 
    column_name = "TITLE", 
    remove_linebreak_pattern = True,
 	to_lower_case = False,
 	expand_contraction_pattern = True,
 	remove_emoji_pattern = True,
 	remove_punctuation_pattern = False
 	)
df.insert(0, "id", range(1, len(df) + 1))

df = extract_content_words(
    df = df, 
    part_of_speech = ["NOUN","VERB","ADJ","AUX","ADV"], 
    save_to_csv = True, 
    csv_name = "data" + "-" + data_from + ".csv")


