
import datetime
import pandas as pd
import matplotlib.pyplot as plt
from psaw import PushshiftAPI
import time
import re

def collect_data(day_,month_,year_, verbose=True,writefile=True):

    print("="*100)

    print("Data request started")

    print("="*100)

    api=PushshiftAPI()

    start_epoch=int(datetime.datetime(year_, month_,day_).timestamp())

    cols = ["timestamp","stock","title","url"]

    df = pd.DataFrame([], columns = cols)

    iteration = 1

    keeptryAPICalls = True

    while keeptryAPICalls:

        submissions=api.search_submissions(
            
            after=start_epoch,
            
            subreddit='wallstreetbets',
            
            filter=['url','author', 'title', 'subreddit','score','num_comments']
            
            )

        for submission in submissions:

            words=submission.title.split()

            cashtags=list(set(filter(lambda word:word.lower().startswith("$"),words)))

            if len(cashtags)>0:

                for cashtag in cashtags:

                    cashtag=cashtag.replace('.','').replace(',','').replace('!','').replace('?','').replace('-','').replace('$','').replace('\'s'','').replace(''/','')

                    match=re.search(r'[0-9]', cashtag)

                    if not match and len(cashtag)>2:

                        cashtag=re.sub(r'[^\w]', ' ', cashtag).strip().upper()

                        splitcash=cashtag.split()

                        if len(splitcash)>0:

                            df = df.append(
                                {
                                    cols[0]:submission.created,
                                    cols[1]:'$'+splitcash[0],
                                    cols[2]:submission.title,
                                    cols[3]:submission.url
                                }, 
                                ignore_index=True
                                )

            if (iteration%100==0 and verbose):

                print (iteration)  

            iteration=iteration+1

        if(len(df)>0):

                keeptryAPICalls=False

                if verbose:

                    print("Data Acquisition is ready")

        else:

            print("Repeating to grab data...")

            time.sleep(10)

    df.columns = df.columns.str.upper()

    if writefile:

        df.to_csv("./data/Datafrom"+"_"+str(year_)+"_"+str(month_)+"_"+str(day_)+".csv",index=False)

    print("="*100)
    
    print("Data request finished")

    print("="*100)
    
    return df