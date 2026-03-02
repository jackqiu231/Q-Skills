import os
import tweepy
from dotenv import load_dotenv

# 加载技能根目录下的.env文件
skill_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(skill_root, '.env'))

def run(args: dict) -> dict:
    # 读取环境变量
    api_key = os.getenv("X_API_KEY")
    api_secret = os.getenv("X_API_SECRET")
    access_token = os.getenv("X_ACCESS_TOKEN")
    access_token_secret = os.getenv("X_ACCESS_TOKEN_SECRET")
    bearer_token = os.getenv("X_BEARER_TOKEN")

    # 解析参数
    text = args.get("text", "")
    media_paths = args.get("media_paths", [])

    if not text:
        return {"output": "错误：推文内容不能为空", "success": False}

    if len(text) > 280:
        return {"output": f"错误：推文内容过长，当前长度{len(text)}字符，最多支持280字符", "success": False}

    try:
        # 优先使用OAuth1.0a认证（支持媒体上传）
        if all([api_key, api_secret, access_token, access_token_secret]):
            auth = tweepy.OAuth1UserHandler(api_key, api_secret, access_token, access_token_secret)
            client = tweepy.Client(
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=access_token,
                access_token_secret=access_token_secret
            )

            # 上传媒体文件
            media_ids = []
            api_v1 = tweepy.API(auth)
            for path in media_paths:
                if not os.path.exists(path):
                    return {"output": f"错误：媒体文件不存在 {path}", "success": False}
                media = api_v1.media_upload(path)
                media_ids.append(media.media_id)

            # 发布推文
            response = client.create_tweet(text=text, media_ids=media_ids)
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
            return {
                "output": f"推文发布成功！访问地址：{tweet_url}",
                "success": True,
                "data": {
                    "tweet_id": tweet_id,
                    "tweet_url": tweet_url
                }
            }
        # 备选：使用OAuth2.0 Bearer Token认证（仅支持纯文本推文，需要用户级token带tweet.write权限）
        elif bearer_token:
            client = tweepy.Client(bearer_token=bearer_token)

            if media_paths:
                return {"output": "错误：使用Bearer Token认证暂不支持发布带媒体的推文，请使用OAuth1.0a认证方式", "success": False}

            # 发布纯文本推文
            response = client.create_tweet(text=text)
            tweet_id = response.data['id']
            tweet_url = f"https://twitter.com/i/web/status/{tweet_id}"
            return {
                "output": f"推文发布成功！访问地址：{tweet_url}",
                "success": True,
                "data": {
                    "tweet_id": tweet_id,
                    "tweet_url": tweet_url
                }
            }
        else:
            return {"output": "错误：缺少认证参数，请配置OAuth1.0a所需的X_API_KEY、X_API_SECRET、X_ACCESS_TOKEN、X_ACCESS_TOKEN_SECRET，或配置OAuth2.0所需的X_BEARER_TOKEN（用户级，需包含tweet.write权限）", "success": False}

    except Exception as e:
        return {"output": f"发布失败：{str(e)}", "success": False}