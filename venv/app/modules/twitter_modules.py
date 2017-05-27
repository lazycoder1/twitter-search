from modules import datastore_modules
from modules import twitter_config

#get the tweets for the search string
def get_tweets(search_str):
    search_str = "\""+search_str+"\""
    result = twitter_config.api.GetSearch(term=search_str, result_type="mixed", count = 30, lang ="en")

    text_list = []  #store the list of tweets here
    id_list = []

    for i in result:
        if i.retweeted_status:
            text_list.append(i.retweeted_status.full_text)
            id_list.append(i.retweeted_status.id)
        else:
            text_list.append(i.full_text)
            id_list.append(i.id)

    #store if not empty
    if len(text_list) != 0:
        datastore_modules.store(text_list, id_list, search_str[1:-1])

    return text_list,id_list