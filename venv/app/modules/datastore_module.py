from modules import twitter_module
from google.cloud import datastore
import logging
from modules import twitter_module
import time

def store(text_list,id_list,created_at,search_str):
    client = datastore.Client('twitter-search-168617')    # Instantiates a client
    kind = 'Tweet'
    name = search_str.lower()
    task_key = client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task.update({
        'size'  : len(text_list),
        'created_at' : created_at,
        'text_list' : text_list,
        'id_list' : id_list,
        'count' : 1
    })
    client.put(task)      # Saves the entity
    print('Saved {}: '.format(task.key.name))



def union(a,b):
    return list(set(a).union(b))

def update():
    searched_list = get_searched_items()
    for i in searched_list:
        logging.debug(i,' update started')
        time.sleep(5)
        new_text,new_id,new_time = twitter_module.get_tweets(i)
        old_text,old_id,old_time = get_from_db(i)
        text_list = union(new_text,old_text)
        id_list = union(new_id,old_id)
        created_at = union(new_time,old_time)

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
    results = list(query.fetch())
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


def get_from_db(search_str):
    client = datastore.Client('twitter-search-168617')
    search_str = search_str
    task_key = client.key('Tweet', search_str)
    task = client.get(task_key)
    return task['text_list'],task['id_list'],task['created_at']