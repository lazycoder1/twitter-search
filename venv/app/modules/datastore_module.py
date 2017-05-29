from modules import twitter_module
from google.cloud import datastore
import logging
from modules import twitter_module
import time







def store(tweets_list,search_str):
    text_list, id_list, created_at = zip(*tweets_list)
    text = list(text_list)
    tweet_id = list(id_list)
    Timestamp = list(created_at)



    client = datastore.Client('twitter-search-168617')    # Instantiates a client
    kind = 'Tweet'
    name = search_str.lower()
    task_key = client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task.update({
        'size'  : len(text_list),
        'created_at' : Timestamp,
        'text_list' : text,
        'id_list' : tweet_id,
        'count' : 1
    })
    client.put(task)      # Saves the entity
    print('Saved {}: '.format(task.key.name))



def union(a,b):
    a = list(a)
    b = list(b)
    return list(set(a).union(b))

def update():
    searched_list = get_searched_items()
    for i in searched_list:

        print(i,' update started')

        new_text_id_time = twitter_module.get_tweets(i)
        old_text_id_time = get_from_db(i)
        union_zip = union(new_text_id_time,old_text_id_time)
        text_list,id_list,created_at = zip(*union_zip)
        text_list = list(text_list)
        id_list = list(id_list)
        created_at = list(created_at)

        client = datastore.Client('twitter-search-168617')
        task_key = client.key('Tweet', i)
        task = client.get(task_key)
        task.update({
            'size': len(text_list),
            'created_at': created_at,
            'text_list': text_list,
            'id_list': id_list,
        })
        logging.debug(i, ' ended started')
        client.put(task)  # Saves the entity





def get_searched_items():
    client = datastore.Client('twitter-search-168617')
    query = client.query(kind='Tweet')
    query.keys_only()
    query.order = ['-count']
    results = list(query.fetch(10))
    searched_list = []
    for i in results:
        searched_list.append(i.key.name)
    return searched_list

def increment_count(search_str):
    client = datastore.Client('twitter-search-168617')
    task_key = client.key('Tweet', search_str)
    task = client.get(task_key)
    task['count'] += 1
    client.put(task)

def to_tuple(text_list,id_list,created_at):
    zip_item = zip(text_list,id_list,created_at)
    return list(zip_item)

def get_from_db(search_str):
    client = datastore.Client('twitter-search-168617')
    search_str = search_str
    task_key = client.key('Tweet', search_str)
    task = client.get(task_key)
    if task is None:
        return False
    else:
        return to_tuple(task['text_list'],task['id_list'],task['created_at'])


