from flask import Flask, render_template, request ,redirect , url_for
from datetime import datetime
from modules import twitter_module, datastore_module

app = Flask(__name__)


@app.route('/tweets',methods=['POST','GET'])
def page(search_str=None):
    if request.method == "POST":
        search_str = request.form['tweet']
        task, next_cursor = datastore_module.get_one_page_of_tasks(search_str=search_str)

        text = []
        id = []
        time = []
        for i in task:
            text.append(i['text_list'])
            id.append(i.key.id)
            time.append(i['created_at'])

        return render_template('tweets.html',
                               search_str = search_str,
                               next_cursor = next_cursor,
                               text = text,
                               id = id,
                               time = time,
                               )

    if request.method == "GET":
        search_str = request.args.get("search_str")
        cursor = request.args.get("cursor")
        cursor = bytes(cursor[2:-1],'utf-8')
        task,next_cursor = datastore_module.get_one_page_of_tasks(cursor,search_str=search_str)

        text = []
        id = []
        time = []
        for i in task:
            text.append(i['text_list'])
            id.append(i.key.id)
            time.append(i['created_at'])

        if len(text) == 0:
            return render_template('END.html',error="YOU HAVE REACHED THE END")
        return render_template('tweets.html',
                               search_str=search_str,
                               next_cursor=next_cursor,
                               text=text,
                               id=id,
                               time=time,
                               )







@app.route('/',methods=['GET','POST'])
def send():

    searched_list = datastore_module.get_searched_items(n=10)
    if request.method == "POST":
        search_str = request.form['tweet']
        if len(search_str) == 0:
            return render_template('index.html', error="Search something",searched_list=searched_list) # User did not search anything
        else:
            if len(search_str) <= 140:   #search only if the search str is less than 140 characters
                if datastore_module.check_if_present(search_str): #if present in the server
                    datastore_module.increment_count(search_str.lower())    #track how many times a given search result is searched
                    return redirect(url_for('page'),code=307)
                tweets_list = twitter_module.get_tweets(search_str,1) #if not present ,ask twitter
                if tweets_list:
                    datastore_module.store(tweets_list, search_str)
                    return redirect(url_for('page'),code=307)
                else:
                    return render_template('index.html',error=" No tweets exists for the given search query",searched_list = searched_list)  # error message
            else :
                return render_template('index.html',error = "Error:Enter search term must be smaller than 140 characters",searched_list = searched_list)  #error message

    return render_template('index.html',error = "",searched_list = searched_list)

@app.route('/crontask',methods=['GET'])
def update():
    datastore_module.update()
    return render_template('index.html',error = "")

@app.route('/update_counter',methods=['GET'])
def reduce_rate_count():
    datastore_module.reduce_api_rate_count()
    return render_template('index.html', error="")


if __name__ == "__main__":
    app.run(debug = True)