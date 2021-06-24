import tweepy
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from wordcloud import WordCloud, STOPWORDS 
import pandas as pd 
import re
import matplotlib.pyplot as plt
from datetime import datetime, timedelta


# Twitter API Credentials
consumerKey = 'enter your own consumer key'
consumerSecret = 'enter your own consumer secret'
accessToken = 'enter your own access token'
accessTokenSecret = 'enter your own token secret'


# Create authentication object
authenticate = tweepy.OAuthHandler(consumerKey, consumerSecret)

# Set the access token and access token secret
authenticate.set_access_token(accessToken, accessTokenSecret)

# Create the API object while passing in the auth information
api = tweepy.API(authenticate, wait_on_rate_limit=True)

# Check to Ensure Connection
try:
    api.verify_credentials()
    print("Authentication OK")
except:
    print("Error during authentication")


time_threshold=datetime.now()-timedelta(days=1)
search='Bitcoin'
tweets = tweepy.Cursor(api.search,q=search, lang='en', tweet_mode='extended').items(500)

text = []
user_screenname = []
all_location = []
all_time = []
retweet = []
like = []
ID = []
media = []


for tw in tweets:

	if tw.created_at >= time_threshold:
		if 'retweeted_status' in tw._json:
			text.append(tw._json['retweeted_status']['full_text'])
		else:
			text.append(tw.full_text)

		user_screenname.append(tw.user.screen_name)
		all_time.append(tw.created_at)
		all_location.append(tw.user.location)
		retweet.append(tw.retweet_count)
		like.append(tw.favorite_count)
		ID.append(tw.id)
		media.append(tw.entities)
	else:
		pass


def cleantext(txt):
	txt = re.sub(r'\n',' ', txt)
	txt = re.sub(r'@[_A-Za-z0-9]+','', txt)
	txt = re.sub(r'#', '', txt)
	txt = re.sub(r'https?:\/\/\S+', '', txt)
	txt = ' '.join(txt.split())
	return txt

tweet_clean = [cleantext(i) for i in text]

score = []
sentiment = []
vader = SentimentIntensityAnalyzer()

for i in tweet_clean:
	compound = vader.polarity_scores(i)['compound']
	score.append(compound)
	if compound	>0.05:
		sentiment.append('Positive')
	elif compound<-0.05:
		sentiment.append('Negative')
	else:
		sentiment.append('Neutral')

data = {
		'ID':ID,
		'User':user_screenname,
		'Tweets':text,
		'Tweets_clean':tweet_clean,
		'Date/time':all_time,
		'Location':all_location,
		'Retweet Count':retweet,
		'Like Count':like,
		'Score':score, 
		'Sentiment':sentiment
		}


df = pd.DataFrame(data)
pd.set_option('display.expand_frame_repr', False)
print(df.head(20))

df_pos = df[df['Sentiment']=='Positive']
df_neg = df[df['Sentiment']=='Negative']
df_neu = df[df['Sentiment']=='Neutral']

v = {'Positive':round(df_pos.shape[0]*100/df.shape[0],2),
	 'Negative':round(df_neg.shape[0]*100/df.shape[0],2),
	 'Neutral':round(df_neu.shape[0]*100/df.shape[0],2) 	
	}

print('% Positive: ',v['Positive'], '\n%Negative: ',v['Negative'], '\n%Neutral: ',v['Neutral'] )
print('Overall Twitter sentiment of {} for the last 24 hours is mostly {} ({}%).'.format(search, max(v, key=v.get), v[max(v, key=v.get)]))


# Plot Word Cloud

comment_words = ''
stopwords = set(STOPWORDS)
  
# iterate through the csv file
for val in tweet_clean:
 
    # split the value
    tokens = val.split()
      
    # Converts each token into lowercase
    for i in range(len(tokens)):
        tokens[i] = tokens[i].lower()

    comment_words += " ".join(tokens)+" "
    comment_words = re.sub(search.lower(),'',comment_words)
    comment_words = re.sub(r'btc','',comment_words)
  
wordcloud = WordCloud(width = 400, height = 400,
                background_color ='white',
                stopwords = stopwords,
                min_font_size = 10).generate(comment_words)
  
# plot the WordCloud image                       
plt.figure(figsize = (8, 8), facecolor = None)
plt.imshow(wordcloud)
plt.axis("off")
plt.title('Wordcloud of {}'.format(search))
plt.tight_layout(pad = 0)
plt.show()
