from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request
from datetime import datetime
from google.cloud import datastore
from modules import twitter_module, datastore_module
import logging
import time


app = Flask(__name__)




def sort_and_zip(a,b,c):
    '''This function , sorts the input based on the timestamp '''
    return sorted(zip(a, b, c), key=lambda x: datetime.strptime(x[2], '%a %b %d %X %z %Y'),reverse=True)





@app.route('/',methods=['GET','POST'])
def send():

    searched_list = datastore_module.get_searched_items()

    if request.method == "POST":
        search_str = request.form['tweet']
        if len(search_str) == 0:
            return render_template('index.html', error="Search something",searched_list=searched_list)
        else:
            if len(search_str) <= 140:   #search only if the search str is less than 140 characters

                if search_str.lower() in [x.lower() for x in searched_list]:
                    datastore_module.increment_count(search_str.lower())    #track how many times a given search result is searched
                    tweets_list, id_list, created_at = datastore_module.get_from_db(search_str.lower())
                    no = [x for x in range(1,len(id_list)+1)]
                    return render_template('tweets.html', search_str=search_str, tweets_list=sort_and_zip(tweets_list,id_list,created_at))

                tweets_list,id_list,created_at = twitter_module.get_tweets(search_str)

                if len(tweets_list) != 0:
                    datastore_module.store(tweets_list, id_list, created_at, search_str)
                    no = [x for x in range(1,len(id_list)+1)]
                    return render_template('tweets.html',search_str = search_str,tweets_list = sort_and_zip(tweets_list,id_list,created_at))
                else:
                    return render_template('index.html',error=" No tweets exists for the given search query",searched_list = searched_list)  # error message

            else :
                return render_template('index.html',error = "Error:Enter search term must be smaller than 140 characters",searched_list = searched_list)  #error message

    return render_template('index.html',error = "",searched_list = searched_list)




if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(datastore_module.update, 'interval', hours=0.02)
    scheduler.start()
    app.run()