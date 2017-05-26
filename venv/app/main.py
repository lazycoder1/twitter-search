from flask import Flask, render_template, request
from google.cloud import datastore
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import time
import os
import twitter


app = Flask(__name__)




def store(text_list,id_list,search_str):
    # [START datastore_quickstart]
    # Imports the Google Cloud client library

    # Instantiates a client
    datastore_client = datastore.Client('twitter-search-168617')

    # The kind for the new entity
    kind = 'Tweet'
    # The name/ID for the new entity
    name = search_str
    # The Cloud Datastore key for the new entity
    task_key = datastore_client.key(kind, name)

    # Prepares the new entity
    task = datastore.Entity(key=task_key)
    task.update({
        'text_list' : text_list,
        'id_list' : id_list
    })

    # Saves the entity
    datastore_client.put(task)

    print('Saved {}: '.format(task.key.name))
    # [END datastore_quickstart]



#get the tweets for the search string
def get_tweets(search_str):

    #The api values
    api = twitter.Api(
        consumer_key='2aDiAbnRd49Vo7BHhrvniWjrG',
        consumer_secret='zJFiCFCHDE8JBBGrHpmFTKCnmnoDkxk1lhTYRGDuobaN46TiAX',
        access_token_key='82617811-hmaOvxhA1Idji8MrnL7r9FEjSBfagoAWUEOjDtnfo',
        access_token_secret='x4YGNDuQiB1hj1p5F3979KWvsKAbsn67KXAY4CqIds7mk',
        tweet_mode='extended'
    )
    search_str = "\""+search_str+"\""
    result = api.GetSearch(term=search_str,result_type="recent",count = 30,lang ="en")

    text_list = []  #store the list of tweets here
    id_list = []

    for i in result:
        if i.retweeted_status:
            text_list.append(i.retweeted_status.full_text)
            id_list.append(i.retweeted_status.id)
        else:
            text_list.append(i.full_text)
            id_list.append(i.id)
    store(text_list,id_list,search_str)
    return text_list,id_list

def update():
    searched_list = get_searched_items()
    for i in searched_list:
        get_tweets(i)

def get_searched_items():
    client = datastore.Client('twitter-search-168617')
    query = client.query(kind='Tweet')
    query.keys_only()
    results = list(query.fetch())
    searched_list = []
    for i in results:
        searched_list.append(i.key.name)
        searched_list[-1] = searched_list[-1][1:-1]   #REMOVES first and last doubles quotes from the strings
    return searched_list

def get_from_db(search_str):
    client = datastore.Client('twitter-search-168617')
    query = client.query(kind='Tweet')

    results = list(query.fetch())
    for i in results:
        if search_str == i.key.name[1:-1]:
            return zip(i['text_list'],i['id_list'])




@app.route('/',methods=['GET','POST'])
def send():

    searched_list = get_searched_items()
    if request.method == "POST":
        search_str = request.form['tweet']
        if len(search_str) <= 140:

            #search the list
            if search_str in searched_list:
                return render_template('tweets.html', search_str=search_str, tweets_list=get_from_db(search_str))

            tweets_list,id_list = get_tweets(search_str)
            if len(tweets_list) != 0:
                return render_template('tweets.html',search_str = search_str,tweets_list = zip(tweets_list,id_list))
            else:
                return render_template('index.html',error=" No tweets exists for the given search query",searched_list = searched_list)  # error message
        else :
            return render_template('index.html',error = "Error:Enter search term must be smaller than 140 characters",searched_list = searched_list)  #error message

    return render_template('index.html',error = "",searched_list = searched_list)



if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(update, 'interval', hours=1)
    scheduler.start()
    app.run()