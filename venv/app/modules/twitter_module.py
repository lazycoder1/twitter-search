from modules import datastore_module
from modules import twitter_config

def to_tuple(text_list,id_list,created_at):
    zip_item = zip(text_list,id_list,created_at)
    return list(zip_item)

#get the tweets for the search string
def get_tweets(search_str):
    search_str = "\""+search_str+"\""
    result = twitter_config.api.GetSearch(term=search_str, result_type="mixed", count = 30, lang ="en")

    if len(result) == 0:
        return False

    created_at = []
    text_list = []  #store the list of tweets here
    id_list = []

    for i in result:
        if i.retweeted_status:
            text_list.append(i.retweeted_status.full_text)
            id_list.append(i.retweeted_status.id)
            created_at.append(i.retweeted_status.created_at)
        else:
            text_list.append(i.full_text)
            id_list.append(i.id)
            created_at.append(i.created_at)
    tweets_list = to_tuple(text_list,id_list,created_at)

    return tweets_list