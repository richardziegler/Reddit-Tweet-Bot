import tweepy
import praw
import time
import os
from prawcore import ResponseException

# Initiating global variables for use later
POSTED_CACHE = 'post_log.txt'
post_id = ''

# Twitter API Keys
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

#Reddit API Keys
REDDIT_CLIENT_ID = ''
REDDIT_CLIENT_SECRET = ''
REDDIT_PASSWORD = ''
REDDIT_USER_AGENT = ''
REDDIT_USERNAME = ''

# Twitter OAuth Process
auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth)
public_tweets = api.home_timeline()

# Reddit OAuth Process
reddit = praw.Reddit(client_id = REDDIT_CLIENT_ID,
                     client_secret = REDDIT_CLIENT_SECRET,
                     password = REDDIT_PASSWORD,
                     user_agent = REDDIT_USER_AGENT,
                     username = REDDIT_USERNAME)

# Function to check for the post in the log. This will help prevent duplicate tweets.
def already_tweeted(post_id):
    found = False
    with open(POSTED_CACHE, 'r') as in_file:
        for line in in_file:
            if post_id in line:
                found = True
                break
    return found

# Function to write the Post ID to the log, so it can be checked later.
def log_tweet(post_id):
    if not os.path.exists(POSTED_CACHE):
        with open(POSTED_CACHE, 'w'):
            pass
    with open(POSTED_CACHE, 'a') as out_file:
        out_file.write(str(post_id) + '\n')

# Checking the new submissions in the Subreddit and then tweeting them out + running the log functions above.
# If the tweet is a duplicate, it will print out an error to the console.
def main():
    while True:
        try:
            subreddit = reddit.subreddit('SUBREDDIT_TO_CHECK').new(limit=1)
            for submission in subreddit:
                    post_id = submission.id
                    if not already_tweeted(post_id):
                        api.update_status(submission.title + " // " + 'redd.it/' + post_id + ' \n' + submission.url + " #PlayArtifact")
                        print(submission.title + " \n" + submission.url)
                        print(post_id)
                        log_tweet(post_id)
                    else:
                        print('error: Tweet is a duplicate { ID: ' + post_id + ' }')
                    break
            time.sleep(45)
        except ResponseException:
        # PRAW returns ResponseException on 503 HTTP response
            print("Reddit is too busy right now. Reconnecting in 3m.")
            time.sleep(180)
            main()

if __name__ == '__main__':
    main()