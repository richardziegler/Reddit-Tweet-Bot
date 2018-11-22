import tweepy
import praw
import time
import os
import requests
import urllib.parse
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

# Function to download Reddit or Imgur photo
def tweet(url, tweet_message):
    if "i.redd.it" in url or "imgur.com" in url:
        print("We recognize the image URL.")
        file_name = os.path.basename(urllib.parse.urlsplit(url).path)
        request = requests.get(url, stream=True)
        if request.status_code == 200:
            # Request and Download Image form URL
            with open(file_name, 'wb') as image:
                for chunk in request:
                    image.write(chunk)
            print("Tweeting /w Image...")
            try:        # Handling situations where we get an imgur gallery or other non-image URL.
                api.update_with_media(file_name, status=tweet_message)
                os.remove(file_name)
            except tweepy.TweepError:   # Tweets out with URL attached if we get TweepyError.
                print("Encountered an error. Tweeting as normal with link")
                api.update_status(tweet_message)
                os.remove(file_name)
        else:   # If request status code is not 200, tweets without image.
            print("Unable to download image")
            api.update_status(tweet_message)
    else:
        print("No 'i.redd.it' or 'imgur.com' in URL")
        api.update_status(tweet_message)

# Checking the new submissions in the Subreddit and then tweeting them out + running the log functions above.
# If the tweet is a duplicate, it will print out an error to the console.
def main():
    while True:
        try:
            subreddit = reddit.subreddit('SUBREDDIT_TO_CHECK').new(limit=1)
            for submission in subreddit:
                    post_id = submission.id
                    if not already_tweeted(post_id):
                        submission_title = submission.title
                        submission_url = submission.url
                        # Check to see if Title is too long for Twitter, if so, WE SLICE IT UP!
                        if len(submission_title) > 210:
                            submission_title = submission_title[0:210] + "..."
                        # Checks for what kind of URL we have to avoid duplicate links to the same page.
                        if "reddit.com/r/SUBREDDIT_TO_CHECK/comments" in submission_url or "i.redd.it" in submission_url or "imgur.com" in submission_url:
                            tweet_message = submission_title + ' redd.it/' + post_id + " #HashTag"
                        else:
                            tweet_message = submission_title + ' redd.it/' + post_id + ' \n' + submission_url + " #HashTag"
                        tweet(submission_url, tweet_message)
                        print(submission_title + " \n" + submission_url)
                        print(post_id)
                        log_tweet(post_id)
                    else:
                        print('error: Tweet is a duplicate { ID: ' + post_id + ' }')
                    break
            time.sleep(300)
        except ResponseException:
        # PRAW returns ResponseException on 503 HTTP response
            print("Reddit is too busy right now. Reconnecting in 3m.")
            time.sleep(400)
            main()

if __name__ == '__main__':
    main()