import json
import boto3

comprehend = boto3.client('comprehend')

def handler(event, context):
    try:
        body = json.loads(event.get('body', '{}'))
        text = body.get('text', '')
        
        if not text:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "No text provided"})
            }

        # Secure enterprise NLP inference handshake via native AWS SDK
        response = comprehend.detect_sentiment(Text=text, LanguageCode='en')
        sentiment_raw = response.get('Sentiment', 'NEUTRAL')
        
        # Map raw corporate classification responses to your visual UI emojis
        emoji_map = {
            "POSITIVE": "🟢 POSITIVE", 
            "NEGATIVE": "🔴 NEGATIVE", 
            "NEUTRAL": "🟡 NEUTRAL"
        }
        
        return {
            "statusCode": 200,
            "headers": { "Content-Type": "application/json" },
            "body": json.dumps({"sentiment": emoji_map.get(sentiment_raw, "🟡 NEUTRAL")})
        }
    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }
