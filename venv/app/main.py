from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request ,redirect , url_for
from datetime import datetime
from google.cloud import datastore
from modules import twitter_module, datastore_module
import logging
import time
from flask_paginate import Pagination
import sys




app = Flask(__name__)

search_str = ''
tweets_list = []


def sort_and_zip(a):
    '''This function , sorts the input based on the timestamp '''
    return sorted(a, key=lambda x: datetime.strptime(x[2], '%a %b %d %X %z %Y'),reverse=True)


def get_tweets_for_page(page,items_per_page,tweets_list):
    start = (page-1)*items_per_page
    stop  = start + items_per_page
    if len(tweets_list) <= stop:
        return tweets_list[start:]
    else:
        return tweets_list[start:stop]

@app.route('/tweets/',defaults={'page': 1})
@app.route('/tweets/pages/<int:page>')
def page(page):
    global tweets_list
    tweets_list = list(tweets_list)
    items_per_page = 20
    tweets = get_tweets_for_page(page,items_per_page,tweets_list)
    search = False
    q = request.args.get('q')
    if q:
        search = True

    pagination = Pagination(page=page, total=len(tweets_list), search=search, record_name='Tweets',bs_version = 3,per_page= 20)
    return render_template('tweets.html',
                           search_str = search_str,
                           tweets_list=tweets,
                           pagination=pagination,
                           )



@app.route('/',methods=['GET','POST'])
def send():
    global tweets_list,search_str
    searched_list = datastore_module.get_searched_items()

    if request.method == "POST":
        search_str = request.form['tweet']
        if len(search_str) == 0:
            return render_template('index.html', error="Search something",searched_list=searched_list) # User did not search anything
        else:
            if len(search_str) <= 140:   #search only if the search str is less than 140 characters
                tweets_list = datastore_module.get_from_db(search_str.lower())
                if tweets_list: #if present in the server
                    datastore_module.increment_count(search_str.lower())    #track how many times a given search result is searched
                    tweets_list=sort_and_zip(tweets_list)
                    return redirect(url_for('page'))
                tweets_list = twitter_module.get_tweets(search_str) #if not present ,ask twitter
                if tweets_list:
                    datastore_module.store(tweets_list, search_str)
                    return redirect(url_for('page'))
                else:
                    return render_template('index.html',error=" No tweets exists for the given search query",searched_list = searched_list)  # error message
            else :
                return render_template('index.html',error = "Error:Enter search term must be smaller than 140 characters",searched_list = searched_list)  #error message

    return render_template('index.html',error = "",searched_list = searched_list)

@app.route('/crontask',methods=['GET'])
def update():
    datastore_module.update()
    return render_template('index.html',error = "")


if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(datastore_module.update, 'interval', hours=1)
    scheduler.start()
    app.run(debug = True)