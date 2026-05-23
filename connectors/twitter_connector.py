import tweepy
from config import (
    TWITTER_BEARER_TOKEN, TWITTER_API_KEY, TWITTER_API_SECRET,
    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_SECRET
)


def _client():
    return tweepy.Client(
        bearer_token=TWITTER_BEARER_TOKEN,
        consumer_key=TWITTER_API_KEY,
        consumer_secret=TWITTER_API_SECRET,
        access_token=TWITTER_ACCESS_TOKEN,
        access_token_secret=TWITTER_ACCESS_SECRET,
        wait_on_rate_limit=True,
    )


def get_home_timeline(max_results: int = 20) -> str:
    """Fetch the latest tweets from your home timeline."""
    try:
        client = _client()
        me = client.get_me()
        tweets = client.get_home_timeline(
            max_results=max_results,
            tweet_fields=["created_at", "author_id", "text"],
            expansions=["author_id"],
            user_fields=["name", "username"],
        )
        if not tweets.data:
            return "No tweets found in the last period."

        users = {u.id: u for u in (tweets.includes.get("users") or [])}
        lines = []
        for t in tweets.data:
            author = users.get(t.author_id)
            name = f"@{author.username}" if author else "unknown"
            lines.append(f"• {name}: {t.text[:120]}")
        return "\n".join(lines)
    except Exception as e:
        return f"Twitter error: {e}"


def post_tweet(text: str) -> dict:
    """Post a tweet on your behalf."""
    try:
        client = _client()
        response = client.create_tweet(text=text)
        return {"success": True, "tweet_id": response.data["id"]}
    except Exception as e:
        return {"success": False, "error": str(e)}
