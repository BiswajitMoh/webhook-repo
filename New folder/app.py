from flask import Flask, request, jsonify, render_template
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

app = Flask(__name__)

# Connect to MongoDB using .env variable
client = MongoClient(os.getenv("MONGO_URI"))
db = client.webhook_db
collection = db.events

@app.route('/webhook', methods=['POST'])
def github_webhook():
    event_type = request.headers.get('X-GitHub-Event')
    data = request.json

    # Handle GitHub's "ping" event
    if event_type == 'ping':
        return jsonify({'msg': 'pong'}), 200

    repo_data = {}

    if event_type == 'push':
        repo_data = {
            'action': 'push',
            'author': data['pusher']['name'],
            'to_branch': data['ref'].split('/')[-1],
            'timestamp': datetime.utcnow()
        }

    elif event_type == 'pull_request':
        pr = data['pull_request']
        # Check if this is a merged pull request
        if data['action'] == 'closed' and pr.get('merged'):
            repo_data = {
                'action': 'merge',
                'author': pr['merged_by']['login'],
                'from_branch': pr['head']['ref'],
                'to_branch': pr['base']['ref'],
                'timestamp': datetime.utcnow()
            }
        else:
            # Regular pull request opened
            repo_data = {
                'action': 'pull_request',
                'author': pr['user']['login'],
                'from_branch': pr['head']['ref'],
                'to_branch': pr['base']['ref'],
                'timestamp': datetime.utcnow()
            }

    # Insert data into MongoDB
    if repo_data:
        collection.insert_one(repo_data)

    return jsonify({"status": "success"}), 200


@app.route('/events')
def get_events():
    events = list(collection.find().sort("timestamp", -1).limit(10))
    for event in events:
        event['_id'] = str(event['_id'])
        event['timestamp'] = event['timestamp'].strftime('%d %b %Y - %I:%M %p UTC')
    return jsonify(events)




print(client.list_database_names())

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
