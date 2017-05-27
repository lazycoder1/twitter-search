from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, render_template, request

from modules import twitter_modules, datastore_modules

app = Flask(__name__)

@app.route('/',methods=['GET','POST'])
def send():

    searched_list = datastore_modules.get_searched_items()

    if request.method == "POST":
        search_str = request.form['tweet']
        if len(search_str) == 0:
            return render_template('index.html', error="Search something",searched_list=searched_list)
        else:
            if len(search_str) <= 140:   #search only if the search str is less than 140 characters

                if search_str.lower() in [x.lower() for x in searched_list]:
                    datastore_modules.increment_count(search_str.lower())
                    return render_template('tweets.html', search_str=search_str, tweets_list=datastore_modules.get_from_db(search_str.lower()))

                tweets_list,id_list = twitter_modules.get_tweets(search_str)
                if len(tweets_list) != 0:
                    return render_template('tweets.html',search_str = search_str,tweets_list = zip(tweets_list,id_list))
                else:
                    return render_template('index.html',error=" No tweets exists for the given search query",searched_list = searched_list)  # error message
            else :
                return render_template('index.html',error = "Error:Enter search term must be smaller than 140 characters",searched_list = searched_list)  #error message

    return render_template('index.html',error = "",searched_list = searched_list)



if __name__ == "__main__":
    scheduler = BackgroundScheduler()
    scheduler.add_job(datastore_modules.update, 'interval', hours=1)
    scheduler.start()
    app.run(debug = True)