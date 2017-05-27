from flask import Flask, render_template, request
from google.cloud import datastore
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import time
import os
import twitter
from twitter_config import api  #The configaration api to access twitter

app = Flask(__name__)




def store(text_list,id_list,search_str):
    # Instantiates a client
    datastore_client = datastore.Client('twitter-search-168617')
    # The kind for the new entity
    kind = 'Tweet'
    # The name/ID for the new entity
    name = search_str.lower()
    # The Cloud Datastore key for the new entity
    task_key = datastore_client.key(kind, name)
    # Prepares the new entity
    task = datastore.Entity(key=task_key)
    task.update({
        'text_list' : text_list,
        'id_list' : id_list,
        'count' : 1
    })
    # Saves the entity
    datastore_client.put(task)
    print('Saved {}: '.format(task.key.name))




#get the tweets for the search string
def get_tweets(search_str):

    search_str = "\""+search_str+"\""
    result = api.GetSearch(term=search_str,result_type="mixed",count = 30,lang ="en")

    text_list = []  #store the list of tweets here
    id_list = []

    for i in result:
        if i.retweeted_status:
            text_list.append(i.retweeted_status.full_text)
            id_list.append(i.retweeted_status.id)
        else:
            text_list.append(i.full_text)
            id_list.append(i.id)
    store(text_list,id_list,search_str[1:-1])
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
    return searched_list

def increment_count(search_str):
    client = datastore.Client('twitter-search-168617')
    search_str = search_str
    task_key = client.key('Tweet', search_str)
    task = client.get(task_key)
    task['count'] += 1
    client.put(task)


def get_from_db(search_str):
    client = datastore.Client('twitter-search-168617')
    search_str = search_str
    task_key = client.key('Tweet', search_str)
    task = client.get(task_key)
    return zip(task['text_list'],task['id_list'])




@app.route('/',methods=['GET','POST'])
def send():

    searched_list = get_searched_items()

    if request.method == "POST":
        search_str = request.form['tweet']

        if len(search_str) <= 140:   #search only if the search str is less than 140 characters

            if search_str.lower() in [x.lower() for x in searched_list]:
                increment_count(search_str.lower())
                return render_template('tweets.html', search_str=search_str, tweets_list=get_from_db(search_str.lower()))

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
    app.run(debug = True)