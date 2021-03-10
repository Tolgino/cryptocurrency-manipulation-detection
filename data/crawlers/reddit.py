import praw
from praw.models import MoreComments
import threading
import datetime
from database.models import Post

# bunlari sonra acariz
# coins = ["Bitcoin", "BTC", "btc", "Ethereum", "ETH", "eth", "Dogecoin", "DOGE", "doge", "Cardano", "ADA", "ada", "Chainlink", "LINK", "link", "Polkadot", "DOT", "dot", "Binance coin", "BNB", "bnb", "Ripple", "XRP", "xrp", "OMG Network", "OMG", "omg", "Litecoin", "LTC", "ltc", "Stellar", "XLM", "xlm", "Basic Attraction Token", "BAT", "bat", "Avalanche", "AVAX", "avax", "Ravencoin", "RVN", "rvn", "Maker", "MKR", "mkr", "Chiliz", "CHZ", "chz"]

coins = ["Bitcoin", "Doge"]
client_id = '7PKSFWfDqgf_lA'
client_secret = '5BLHdTaIJQT680-ZwXo1jo3xIbLOJw'
user_agent = 'Crawler for Cryptocurrency Analysis'


def calculate_interaction_score(num_comments, score):
    return num_comments + score


def get_reddit_posts_as_models(limit):
    # timer ayarla
    # threading.Timer(10.0, get_reddit).start()
    reddit = praw.Reddit(client_id=client_id, client_secret=client_secret,
                         user_agent=user_agent)
    print("RedditCrawler: Collecting from Reddit with limit " + str(limit))
    posts = []
    for coin in coins:
        coin_subreddit = reddit.subreddit(coin)
        # limit degistir
        for submission in coin_subreddit.hot(limit=limit):
            print("RedditCrawler: Browsing submission:", submission.title)
            interaction_score = calculate_interaction_score(submission.num_comments, submission.score)
            subreddit_source = "reddit/" + submission.subreddit.display_name
            submission_model = Post(submission.author.name, submission.selftext, interaction_score, subreddit_source,
                                    int(submission.created_utc))
            posts.append(submission_model)
            submission = reddit.submission(id=submission.id)
            # Only consider top level comments and do not expand the "more comments" links.
            for top_comment in list(submission.comments.replace_more(limit=0)):
                if isinstance(top_comment, MoreComments):
                    continue
                # Discard the comments with no content.
                if top_comment.body is None or top_comment.body.trim() == '':
                    continue
                comment_interaction_score = calculate_interaction_score(len(top_comment.replies), top_comment.score)
                comment_model = Post(top_comment.author.name, top_comment.body, comment_interaction_score,
                                     subreddit_source, top_comment.created_utc)
                posts.append(comment_model)
    print("RedditCrawler: Done!")
    return posts


def get_date(submission):
    time = submission.created
    return datetime.datetime.fromtimestamp(time)