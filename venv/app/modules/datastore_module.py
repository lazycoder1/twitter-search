from google.cloud import datastore
from modules import twitter_module
from datetime import datetime

#To get the appengine library to work ..
import dev_appserver
dev_appserver.fix_sys_path()
from google.appengine.api import taskqueue

def strip_repeats(a,b,c):
    zipped =zip(a,b,c)
    zipped = list(zipped)
    zipped = set(zipped)
    zipped = list(zipped)
    a,b,c = zip(*zipped)
    a,b,c = convert_to_list(a,b,c)
    return a,b,c

def convert_to_list(a,b,c):
    a=list(a)
    b=list(b)
    c=list(c)
    return a,b,c



def store(tweets_list,search_str):
    text_list, id_list, created_at = zip(*tweets_list)
    text,tweet_id,created_at = convert_to_list(text_list,id_list,created_at)
    text,tweet_id,created_at=strip_repeats(text,tweet_id,created_at)

    client = datastore.Client('twitter-search-168617')    # Instantiates a client
         # Saves the entity
    table_values = []
    size = 0
    for i in range(len(text)):
        kind = '_'+search_str.lower()
        name = tweet_id[i]
        task_key = client.key(kind,name)
        task = client.get(task_key)
        if task is None:
            task = datastore.Entity(key=task_key)
        else:
            continue
        size = size+1
        task.update({
            'created_at' : datetime.strptime(created_at[i], '%a %b %d %X %z %Y'),
            'text_list': text[i],
        })
        table_values.append(task)
    client.put_multi(table_values)

    kind = 'Tweet'
    name = search_str.lower()
    task_key = client.key(kind, name)
    task = datastore.Entity(key=task_key)
    task.update({
        'size': size,
        'count': 1
    })
    client.put(task)

    print('Saved {}: '.format(task.key.name))



def update():
    searched_list = get_searched_items()
    client = datastore.Client('twitter-search-168617')
    for i in searched_list:
        print(i,' update started')

        new_text_id_time = twitter_module.get_tweets(i,2)
        text_list,id_list,created_at = zip(*new_text_id_time)
        text_list,id_list,created_at = convert_to_list(text_list,id_list,created_at)
        text_list,id_list,created_at = strip_repeats(text_list,id_list,created_at)
        size = 0

        for j in range(len(text_list)):
            task_list = []
            task_key = client.key('_'+i,id_list[j])
            task = client.get(task_key)
            if task is None:
                task = datastore.Entity(key=task_key)
            else:
                continue
            size +=1
            task.update({
                'created_at': datetime.strptime(created_at[j], '%a %b %d %X %z %Y'),
                'text_list': text_list[j],
            })
            task_list.append(task)
        client.put_multi(task_list)

        kind = 'Tweet'
        name = i
        task_key = client.key(kind, name)
        task = client.get(task_key)
        task.update({
            'size': task['size']+size,
            'count': task['count'] + 1
        })
        client.put(task)

        print(i, ' ended')





def get_searched_items(n=0):
    client = datastore.Client('twitter-search-168617')
    query = client.query(kind='Tweet')
    query.keys_only()
    query.order = ['-count']
    if n!=0:
        results = list(query.fetch(n))
    else:
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

def to_tuple(text_list,id_list,created_at):
    zip_item = zip(text_list,id_list,created_at)
    return list(zip_item)

def check_if_present(search_str):
    client = datastore.Client('twitter-search-168617')
    search_str = search_str.lower()
    task_key = client.key('Tweet', search_str)
    task = client.get(task_key)
    if task is None:
        return False
    else :
        return True


def get_one_page_of_tasks(cursor=None,search_str=''):
    client = datastore.Client('twitter-search-168617')
    query = client.query(kind='_'+search_str)
    query.order = ['-created_at']
    query_iter = query.fetch(start_cursor=cursor, limit=20)
    page = next(query_iter.pages)
    tasks = list(page)
    next_cursor = query_iter.next_page_token
    return tasks, next_cursor

def create_task_queue():
    task = taskqueue.add(
        url='/update_counter',
        target='worker',
        params={'app_name': 'app_1'},
        countdown = 300
    )
    print('task_started')

def task_full(use):
    client = datastore.Client('twitter-search-16817')
    name = 'twitter-rate'
    kind = 'Tweet-api'
    task_key = client.key(kind, name)
    task = client.get(task_key)
    if task is None:
        task = datastore.Entity(key=task_key)
        task.update({
            task['app_1'] : 1
        })
    else:
        if task['app_1'] >= 400 & use == 2:
            return True
        elif task['app_1'] >= 440 & use == 1:
            return True

        task.update({
            task['app_1'] : task['app_1']+1
        })

        create_task_queue()
        return False

def reduce_api_rate_count():
    client = datastore.Client('twitter-search-16817')
    name = 'twitter-rate'
    kind = 'Tweet-api'
    task_key = client.key(kind, name)
    task = client.get(task_key)
    if task['app_1'] == 0:
        return
    task.update({
        task['app_1']: task['app_1'] - 1
    })

