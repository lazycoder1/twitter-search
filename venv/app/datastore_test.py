from flask import Flask, render_template, request
from google.cloud import datastore
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

import time
import os
import twitter

search_str = '"google"'
# Instantiates a client
client = datastore.Client('twitter-search-168617')
query = client.query(kind='Tweet')
task_key = client.key('Tweet',search_str)
g = client.get(task_key)

print(g['id_list'])
