from google.cloud import datastore
import twitter







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

    return text_list,id_list





def run_quickstart():
    # [START datastore_quickstart]
    # Imports the Google Cloud client library


    # Instantiates a client
    client = datastore.Client('twitter-search-168617')
    query = client.query(kind='Tweet')
    query.keys_only()
    results = list(query.fetch())

    print(results[0].key.name)
    





if __name__ == '__main__':
    run_quickstart()