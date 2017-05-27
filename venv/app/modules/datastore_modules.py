from modules import twitter_modules
from google.cloud import datastore
from google.cloud import datastore

from modules import twitter_modules


def store(text_list,id_list,search_str):
    datastore_client = datastore.Client('twitter-search-168617')    # Instantiates a client
    kind = 'Tweet'
    name = search_str.lower()
    task_key = datastore_client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task.update({
        'text_list' : text_list,
        'id_list' : id_list,
        'count' : 1
    })
    datastore_client.put(task)      # Saves the entity
    print('Saved {}: '.format(task.key.name))


def update():
    searched_list = get_searched_items()
    for i in searched_list:
        twitter_modules.get_tweets(i)



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