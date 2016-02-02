import tweepy
from config import config

# Test connection to twitter api
def connect_to_api():
	auth = tweepy.OAuthHandler(consumer_key=config['consumer_key'], consumer_secret=config['consumer_secret'])
	auth.set_access_token(config['access_token_key'], config['access_token_secret'])

	api = tweepy.API(auth)
	
	return api

def test_api():
	api = connect_to_api()
	
	print api.verify_credentials()

class ReplyListener(tweepy.StreamListener):

	def on_status(self, status):
		mentions = status.entities.get('user_mentions')

		if mentions is not None:
			if any(user.get('screen_name', None) == 'permitbot' for user in mentions):
				if status.coordinates is not None:
					print status.coordinates['coordinates']
				else:
					print "No coordinates"
					

def listen_for_replies():
	api = connect_to_api()

	reply_listener = ReplyListener()
	reply_stream = tweepy.Stream(auth = api.auth, listener=reply_listener)

	reply_stream.filter(track=['permitbot'])


if __name__ == "__main__":
	test_api()
	listen_for_replies()