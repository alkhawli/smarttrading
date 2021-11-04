import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
import re
import string
import contractions
import pandas as pd
from textblob import TextBlob

import en_core_web_sm
nlp = en_core_web_sm.load()
import spacy



#nltk.download('vader_lexicon')


def remove_linebreak(text):
    linebreak_pattern = r'(\r\n)+|(\r)+|(\n)+|(\t)+'
    without_linebreak_pattern = re.sub(pattern=linebreak_pattern, repl=" ", string=text)
    return without_linebreak_pattern


def remove_extra_spaces(text):
    space_pattern = r"\s+"
    text = re.sub(pattern=space_pattern, repl=" ", string=text)
    space_pattern_left_right = r"(^\s|\s$)"
    text = re.sub(pattern=space_pattern_left_right, repl="", string=text)
    return text


def lower_case_convertion(text):
    lower_text = text.lower()
    return lower_text


def expand_contraction(text):
    text = contractions.fix(text)
    return text


def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)

    without_emoji = emoji_pattern.sub(r'', text)
    return without_emoji



def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def text_preprocessing(
        df,
        column_name,
        remove_linebreak_pattern=True,
        to_lower_case=False,
        expand_contraction_pattern=True,
        remove_emoji_pattern=True,
        remove_punctuation_pattern=False
):
    column_name_cleaned = f"{column_name}_cleaned".upper()
    if remove_linebreak_pattern:
        df[column_name_cleaned] = df[column_name].apply(remove_linebreak)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)

    if to_lower_case:
        df[column_name_cleaned] = df[column_name_cleaned].apply(lower_case_convertion)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)

    if expand_contraction_pattern:
        df[column_name_cleaned] = df[column_name_cleaned].apply(expand_contraction)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)

    if remove_emoji_pattern:
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_emojis)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)

    if remove_punctuation_pattern:
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_punctuation)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)
    return df




def extract_content_words(df, part_of_speech):
	print("Step 01 (Tokenization, lemmatisation, parsing): Started.")
	df_features = pd.DataFrame(columns = ["id","text","lemma","pos","tag","dep","shape","is_alpha","is_stop","has_vector","vector_norm","is_oov"])
	for i in list(range(len(df))):
		doc = nlp(df["BODY_CLEANED"][i])
		for token in doc:
			df_features = df_features.append(
				{
					"id" : int(i + 1),
					"text" : token.text,
					"lemma": token.lemma_,
					"pos" : token.pos_,
					"tag": token.tag_,
					"dep" : token.dep_,
					"shape": token.shape_,
					"is_alpha": token.is_alpha,
					"is_stop": token.is_stop,
					"has_vector" : token.has_vector,
					"vector_norm" : token.vector_norm,
					"is_oov" : token.is_oov
				},
				ignore_index = True
			)
	print(df_features)
	print("Step 01 (Tokenization, lemmatisation, parsing): Complete.")
	print("Step 02 (Extracting content words): Started.")

	for pos in part_of_speech:
		df_temp = df_features[(df_features.pos == pos) & (df_features.is_alpha == True)]
		df_temp = df_temp[["id","lemma"]].sort_values(by = ["id"], ascending = [True])
		df_temp.reset_index(drop = True, inplace = True)
		print(df_temp)
		df_temp_lemmata = pd.DataFrame(columns = ["id",f"lemmata_{pos.lower()}"])
		print(df_temp_lemmata)

		for i in list(range(1, df_temp.id.max() + 1)):
			df_temp_pos = df_temp[df_temp.id == i]
			list_temp = df_temp_pos.lemma.to_list()
			df_temp_lemmata = df_temp_lemmata.append(
				{
					"id" : int(i),
					f"lemmata_{pos.lower()}" : list_temp
				},
				ignore_index = True
			)
		df = df.merge(right = df_temp_lemmata,  how = "left", on = "id")

	print("Step 02 (Extracting content words): Complete.")
	df.columns = df.columns.str.upper()
	return df



with open("./output/top_tickers_v2.json", "r") as f:
    x = json.load(f)

# This is only for the first array of comments
comments = x['stock_list'][0].get("comments")
df = pd.DataFrame(comments)

df['id']=df.index+1
df = text_preprocessing(
    df=df,
    column_name="body",
    remove_linebreak_pattern=True,
    to_lower_case=True,
    expand_contraction_pattern=True,
    remove_emoji_pattern=True,
    remove_punctuation_pattern=True
)



df = extract_content_words(
    df = df,
    part_of_speech = ["NOUN","VERB","ADJ","AUX","ADV"])
df['neg'] = 0
df['neu'] = 0
df['pos'] = 0
df['compound'] = 0
df['polarity'] = 0
df['subjectivity'] = 0

sid = SentimentIntensityAnalyzer()

for index, row in df.iterrows():
    sentimentResults = sid.polarity_scores(row.BODY_CLEANED)
    print(sentimentResults)
    textblox = TextBlob(row.BODY_CLEANED)
    df.neg.iloc[index] = sentimentResults['neg']
    df.neu.iloc[index] = sentimentResults['neu']
    df.pos.iloc[index] = sentimentResults['pos']
    df.compound.iloc[index] = sentimentResults['compound']
    df.polarity.iloc[index] = textblox.sentiment.polarity
    df.subjectivity.iloc[index] = textblox.sentiment.subjectivity


df.to_csv("./output/outputsentimentanalysis_onlyfirstrow.csv")


'''
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
import re
import string
import contractions
import pandas as pd

nltk.download('vader_lexicon')


def remove_linebreak(text):
    linebreak_pattern = r'(\r\n)+|(\r)+|(\n)+|(\t)+'
    without_linebreak_pattern = re.sub(pattern=linebreak_pattern, repl=" ", string=text)
    return without_linebreak_pattern


def remove_extra_spaces(text):
    space_pattern = r"\s+"
    text = re.sub(pattern=space_pattern, repl=" ", string=text)
    space_pattern_left_right = r"(^\s|\s$)"
    text = re.sub(pattern=space_pattern_left_right, repl="", string=text)
    return text


def lower_case_convertion(text):
    lower_text = text.lower()
    return lower_text


def expand_contraction(text):
    text = contractions.fix(text)
    return text


def remove_emojis(text):
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # emoticons
                               u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                               u"\U0001F680-\U0001F6FF"  # transport & map symbols
                               u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                               u"\U00002500-\U00002BEF"  # chinese char
                               u"\U00002702-\U000027B0"
                               u"\U00002702-\U000027B0"
                               u"\U000024C2-\U0001F251"
                               u"\U0001f926-\U0001f937"
                               u"\U00010000-\U0010ffff"
                               u"\u2640-\u2642"
                               u"\u2600-\u2B55"
                               u"\u200d"
                               u"\u23cf"
                               u"\u23e9"
                               u"\u231a"
                               u"\ufe0f"  # dingbats
                               u"\u3030"
                               "]+", flags=re.UNICODE)

    without_emoji = emoji_pattern.sub(r'', text)
    return without_emoji


def remove_punctuation(text):
    return text.translate(str.maketrans("", "", string.punctuation))


def text_preprocessing(
        df,
        column_name,
        remove_linebreak_pattern=True,
        to_lower_case=False,
        expand_contraction_pattern=True,
        remove_emoji_pattern=True,
        remove_punctuation_pattern=False
):
    column_name_cleaned = f"{column_name}_cleaned".upper()
    if remove_linebreak_pattern:
        df[column_name_cleaned] = df[column_name].apply(remove_linebreak)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)

    if to_lower_case:
        df[column_name_cleaned] = df[column_name_cleaned].apply(lower_case_convertion)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)

    if expand_contraction_pattern:
        df[column_name_cleaned] = df[column_name_cleaned].apply(expand_contraction)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)

    if remove_emoji_pattern:
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_emojis)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)

    if remove_punctuation_pattern:
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_punctuation)
        df[column_name_cleaned] = df[column_name_cleaned].apply(remove_extra_spaces)
    return df


with open("./output/top_tickers_v2.json", "r") as f:
    x = json.load(f)

# This is only for the first array of comments
comments = x['stock_list'][0].get("comments")
df = pd.DataFrame(comments)

df = text_preprocessing(
    df=df,
    column_name="body",
    remove_linebreak_pattern=True,
    to_lower_case=True,
    expand_contraction_pattern=True,
    remove_emoji_pattern=True,
    remove_punctuation_pattern=True
)

df['neg'] = 0
df['neu'] = 0
df['pos'] = 0
df['compound'] = 0

sid = SentimentIntensityAnalyzer()

for index, row in df.iterrows():
    sentimentResults = sid.polarity_scores(row.BODY_CLEANED)
    print(sentimentResults)
    df.neg.iloc[index] = sentimentResults['neg']
    df.neu.iloc[index] = sentimentResults['neu']
    df.pos.iloc[index] = sentimentResults['pos']
    df.compound.iloc[index] = sentimentResults['compound']

print(df)
'''