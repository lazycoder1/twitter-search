from flask import Flask, render_template, request
import twitter
app = Flask(__name__)

def get_tweets(search_str):
    api = twitter.Api(
        consumer_key='2aDiAbnRd49Vo7BHhrvniWjrG',
        consumer_secret='zJFiCFCHDE8JBBGrHpmFTKCnmnoDkxk1lhTYRGDuobaN46TiAX',
        access_token_key='82617811-hmaOvxhA1Idji8MrnL7r9FEjSBfagoAWUEOjDtnfo',
        access_token_secret='x4YGNDuQiB1hj1p5F3979KWvsKAbsn67KXAY4CqIds7mk'
    )
    search_str = "\""+search_str+"\""
    result = api.GetSearch(term=search_str,result_type="mixed",count = 30,lang ="en")
    text_list = []
    id_list = []
    for i in result:
        text_list.append(i.text)
        id_list.append(i.id)
    return text_list,id_list

@app.route('/',methods=['GET','POST'])
def send():

    if request.method == "POST":
        search_str = request.form['tweet']
        if len(search_str) <= 140:
            tweets_list,id_list = get_tweets(search_str)
            if len(tweets_list) != 0:
                return render_template('tweets.html',search_str = search_str,tweets_list = zip(tweets_list,id_list))
            else:
                return render_template('index.html',error=" No tweets exists for the given search query")  # error message
        else :
            return render_template('index.html',error = "Error:Enter search term must be smaller than 140 characters")  #error message

    return render_template('index.html',error = "")

if __name__ == "__main__":
    app.run()