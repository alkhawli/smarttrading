import pprint
import sys
import nltk
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import json
import re
import string
import contractions
import pandas as pd
import spacy
import en_core_web_sm
from datetime import datetime

nlp = en_core_web_sm.load()


class SentimentAnalysis:
    def __init__(self, jsonobject):
        self.sid = SentimentIntensityAnalyzer()
        self.outputdf = pd.DataFrame([])
        self.mentions = 0
        self.stockname = ''
        self.jsondata=jsonobject

    def __remove_linebreak(self, text):
        linebreak_pattern = r'(\r\n)+|(\r)+|(\n)+|(\t)+'
        without_linebreak_pattern = re.sub(pattern=linebreak_pattern, repl=" ", string=text)
        return without_linebreak_pattern

    def __remove_extra_spaces(self, text):
        space_pattern = r"\s+"
        text = re.sub(pattern=space_pattern, repl=" ", string=text)
        space_pattern_left_right = r"(^\s|\s$)"
        text = re.sub(pattern=space_pattern_left_right, repl="", string=text)
        return text

    def __lower_case_convertion(self, text):
        lower_text = text.lower()
        return lower_text

    def __expand_contraction(self, text):
        text = contractions.fix(text)
        return text

    def __remove_emojis(self, text):
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

    def __remove_punctuation(self, text):
        return text.translate(str.maketrans("", "", string.punctuation))

    def __text_preprocessing(self,
                             df,
                             column_name,
                             remove_linebreak_pattern=True,
                             to_lower_case=True,
                             expand_contraction_pattern=True,
                             remove_emoji_pattern=True,
                             remove_punctuation_pattern=True
                             ):
        column_name_cleaned = f"{column_name}_cleaned".upper()
        if remove_linebreak_pattern:
            df[column_name_cleaned] = df[column_name].apply(self.__remove_linebreak)
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__remove_extra_spaces)

        if to_lower_case:
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__lower_case_convertion)
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__remove_extra_spaces)

        if expand_contraction_pattern:
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__expand_contraction)
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__remove_extra_spaces)

        if remove_emoji_pattern:
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__remove_emojis)
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__remove_extra_spaces)

        if remove_punctuation_pattern:
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__remove_punctuation)
            df[column_name_cleaned] = df[column_name_cleaned].apply(self.__remove_extra_spaces)
        return df

    def __extract_content_words(self, df, part_of_speech):
        df_features = pd.DataFrame(
            columns=["id", "text", "lemma", "pos", "tag", "dep", "shape", "is_alpha", "is_stop", "has_vector",
                     "vector_norm", "is_oov"])
        for i in list(range(len(df))):
            doc = nlp(df["BODY_CLEANED"][i])
            for token in doc:
                df_features = df_features.append(
                    {
                        "id": int(i + 1),
                        "text": token.text,
                        "lemma": token.lemma_,
                        "pos": token.pos_,
                        "tag": token.tag_,
                        "dep": token.dep_,
                        "shape": token.shape_,
                        "is_alpha": token.is_alpha,
                        "is_stop": token.is_stop,
                        "has_vector": token.has_vector,
                        "vector_norm": token.vector_norm,
                        "is_oov": token.is_oov
                    },
                    ignore_index=True
                )
        for pos in part_of_speech:
            df_temp = df_features[(df_features.pos == pos) & (df_features.is_alpha == True)]
            df_temp = df_temp[["id", "lemma"]].sort_values(by=["id"], ascending=[True])
            df_temp.reset_index(drop=True, inplace=True)
            df_temp_lemmata = pd.DataFrame(columns=["id", f"lemmata_{pos.lower()}"])
            valuemax = df_temp.id.max()
            if np.isnan(valuemax) == True: valuemax = 0
            for i in list(range(1, int(valuemax + 1))):
                df_temp_pos = df_temp[df_temp.id == i]
                list_temp = df_temp_pos.lemma.to_list()
                df_temp_lemmata = df_temp_lemmata.append(
                    {
                        "id": int(i),
                        f"lemmata_{pos.lower()}": list_temp
                    },
                    ignore_index=True
                )
            df = df.merge(right=df_temp_lemmata, how="left", on="id")
        df.columns = df.columns.str.upper()
        return df

    def writeoutput(self):
        self.outputdf.sort_values(by='Mentions',inplace=True, ascending=False)
        filename=datetime.now().strftime("%Y%m%d-%H%M%S")
        self.outputdf.to_csv("./output/{0}_output.csv".format(filename), index=False)

    def runononeline(self, iteration):
        print(self.jsondata['stock_list'][iteration])
        self.stockname = self.jsondata['stock_list'][iteration]['name']
        self.mentions = self.jsondata['stock_list'][iteration]['mentions']
        df = pd.DataFrame(self.jsondata['stock_list'][iteration].get("comments"))
        df = self.__text_preprocessing(
            df=df,
            column_name="body",
            remove_linebreak_pattern=True,
            to_lower_case=True,
            expand_contraction_pattern=True,
            remove_emoji_pattern=True,
            remove_punctuation_pattern=True
        )
        df = df[(df.score < -2) | (df.score > 2)].sort_values(by='score', ascending=False)
        df.reset_index(inplace=True)
        df['neg'] = 0
        df['neu'] = 0
        df['pos'] = 0
        df['compound'] = 0
        df['score']=df['score'].sum()

        for index, row in df.iterrows():
            sentimentResults = self.sid.polarity_scores(row.BODY_CLEANED)
            df.neg.iloc[index] = sentimentResults['neg']
            df.neu.iloc[index] = sentimentResults['neu']
            df.pos.iloc[index] = sentimentResults['pos']
            df.compound.iloc[index] = sentimentResults['compound']

        df = df[df.compound != 0]
        df.reset_index(inplace=True)
        df['id'] = df.index + 1
        df = self.__extract_content_words(
            df=df,
            part_of_speech=["NOUN", "VERB", "ADJ", "AUX", "ADV"])
        return df

    def aggregateinformation(self, df):
        countpositive = (df.COMPOUND > 0.2).sum().sum()
        countnegative = (df.COMPOUND < -0.2).sum().sum()
        countneutral = ((df.COMPOUND > -0.2) & (df.COMPOUND < 0.2)).sum().sum()
        newdf = df.explode('LEMMATA_VERB')
        newdf.LEMMATA_VERB = newdf.LEMMATA_VERB.str.replace('be', '')
        newdf.LEMMATA_VERB = newdf.LEMMATA_VERB.str.replace('have', '')
        newdf.LEMMATA_VERB = newdf.LEMMATA_VERB.str.replace('\'', '')
        newdf.LEMMATA_VERB = newdf.LEMMATA_VERB.str.replace(' ', '')
        verbsoccurences = newdf.LEMMATA_VERB.value_counts().rename_axis('verbs').reset_index(name='counts')
        verbsoccurences = verbsoccurences[verbsoccurences.verbs != '']
        if len(df)>0:
            self.outputdf = self.outputdf.append({'Stockname': self.stockname, 'Mentions': self.mentions, 'countpositive': countpositive,
             'countnegative': countnegative, 'countneutral': countneutral, 'verbs': verbsoccurences.verbs.tolist(),'aggscoresum':df.SCORE.iloc[0]},
            ignore_index=True)
        else:
            self.outputdf = self.outputdf.append({'Stockname': self.stockname, 'Mentions': self.mentions, 'countpositive': countpositive,
             'countnegative': countnegative, 'countneutral': countneutral, 'verbs': verbsoccurences.verbs.tolist(),'aggscoresum':np.nan},
            ignore_index=True)
    def run(self):
        for jsonline in range(len(self.jsondata['stock_list'])):
            print("Json item {0} is now being processed".format(jsonline))
            df = self.runononeline(jsonline)
            self.aggregateinformation(df)
        self.writeoutput()