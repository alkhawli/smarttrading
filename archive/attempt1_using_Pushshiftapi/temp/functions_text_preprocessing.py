# https://dataaspirant.com/nlp-text-preprocessing-techniques-implementation-python/

import re
import string
import contractions
import pandas as pd
import spacy
from spacy import displacy
nlp = spacy.load("en_core_web_lg")

def remove_linebreak(text):
	linebreak_pattern = r'(\r\n)+|(\r)+|(\n)+|(\t)+'
	without_linebreak_pattern = re.sub(pattern = linebreak_pattern, repl = " ", string = text)
	return without_linebreak_pattern

def lower_case_convertion(text):
	lower_text = text.lower()
	return lower_text

def expand_contraction(text):
	text = contractions.fix(text)
	return text

def remove_punctuation(text):
	return text.translate(str.maketrans("", "", string.punctuation))

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
	without_emoji = emoji_pattern.sub(r'',text)
	return without_emoji

def remove_extra_spaces(text):
	space_pattern = r"\s+"
	text = re.sub(pattern = space_pattern, repl = " ", string = text)
	space_pattern_left_right = r"(^\s|\s$)"
	text = re.sub(pattern = space_pattern_left_right, repl = "", string = text)
	return text

def text_preprocessing(
	
	df,
	
	column_name, 
	
	remove_linebreak_pattern = True,
	
	to_lower_case = False,

	expand_contraction_pattern = True,

	remove_emoji_pattern = True,

	remove_punctuation_pattern = False
	
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


def clean_tweet_for_sentiment_analysis(text):
    # Remove mentions
	text = re.sub(pattern = r"@\w+", repl = "", string = text)
    # Remove hashtags
	text = re.sub(pattern = r"#\w+", repl = "", string = text)
    # Remove retweets:
	text = re.sub(pattern = r"RT : ", repl = "", string = text)
    # Remove urls
	text = re.sub(pattern = r"https?:\/\/\S+|www\.\S+", repl = "", string = text)
	return text


def remove_numbers(text):
	text = re.sub(pattern = r"\d+", repl = "", string = text)
	return text

def num_to_words(text):
	# splitting text into words with space
	after_spliting = text.split()
	for index in range(len(after_spliting)):
		if after_spliting[index].isdigit():
			after_spliting[index] = num2words(after_spliting[index])
    # joining list into string with space
	text = ' '.join(after_spliting)
	return text

def remove_single_char(text):
	single_char_pattern = r"\s+[a-zA-Z]\s+"
	without_sc = re.sub(pattern = single_char_pattern, repl = " ", string = text)
	return without_sc

def extract_content_words(df, part_of_speech, csv_name, save_to_csv = True):

	print("Step 01 (Tokenization, lemmatisation, parsing): Started.")

	df_features = pd.DataFrame(columns = ["id","text","lemma","pos","tag","dep","shape","is_alpha","is_stop","has_vector","vector_norm","is_oov"])

    # text: The original word text.
    # lemma: The base form of the word.
    # pos: The simple UPOS part-of-speech tag.
    # tag: The detailed part-of-speech tag.
    # dep: Syntactic dependency, i.e. the relation between tokens.
    # shape: The word shape – capitalization, punctuation, digits.
    # is_alpha: Is the token an alpha character?
    # is_stop: Is the token part of a stop list, i.e. the most common words of the language?
    # has_vector: Does the token have a vector representation?
    # vector_norm: The L2 norm of the token’s vector (the square root of the sum of the values squared)
    # is_oov = is a word out-of-vocabulary?

	for i in list(range(len(df))):

		doc = nlp(df["TITLE_CLEANED"][i])

		# print(doc.text)

		# print("="*100)

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

	print("Step 01 (Tokenization, lemmatisation, parsing): Complete.")

	print("Step 02 (Extracting content words): Started.")

	for pos in part_of_speech:

		df_temp = df_features[(df_features.pos == pos) & (df_features.is_alpha == True)]

		df_temp = df_temp[["id","lemma"]].sort_values(by = ["id"], ascending = [True])

		df_temp.reset_index(drop = True, inplace = True)

		df_temp_lemmata = pd.DataFrame(columns = ["id",f"lemmata_{pos.lower()}"])

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

	if save_to_csv:

		print("Step 03 (Saving data): Started.")

		df.to_csv("./data/" + csv_name, index = False, sep = "\t")

		print("Step 03 (Saving data): Complete.")
		
	return df
