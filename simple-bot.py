import tweepy
import praw
import time

# Twitter OAuth Process
auth = tweepy.OAuthHandler("CONSUMER_KEY", "CONSUMER_SECRET")
auth.set_access_token("ACCESS_TOKEN", "ACCESS_TOKEN_SECRET")
api = tweepy.API(auth)
public_tweets = api.home_timeline()

# Reddit OAuth Process
reddit = praw.Reddit(client_id="CLIENT_ID",
                     client_secret="CLIENT_SECRET",
                     password="PASSWORD",
                     user_agent="DESCRIPTION",
                     username="USERNAME")

def main():
    while True:
        try:
            subreddit = reddit.subreddit("SUBREDDIT").new()
            for submission in subreddit:
                    api.update_status(submission.title + " \n" + submission.url)
                    print(submission.title + " \n" + submission.url)
                    break
        except tweepy.TweepError as e:
                print(e.reason)
        time.sleep(30)

if __name__ == '__main__':
    main()