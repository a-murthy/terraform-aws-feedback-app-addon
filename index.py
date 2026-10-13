import os
import json
import boto3

# Initialize the AWS NLP client natively
comprehend = boto3.client('comprehend', region_name='us-east-1')

# Persistent cloud environment memory state tracking dictionary
MAINTENANCE_STATE = {"active": False}

def handler(event, context):
    global MAINTENANCE_STATE
    print("--- DUAL-TIER ADD-ON INVOCATION DETECTED ---")
    print(f"Incoming Event Payload: {json.dumps(event)}")
    
    # Extract the true payload dictionary whether passed directly or via a Function URL proxy body
    payload_data = {}
    
    # 🟢 FIXED: Handle Lambda Function URL HTTP POST proxy encapsulation
    if isinstance(event, dict) and 'body' in event and event['body']:
        try:
            payload_data = json.loads(event['body'])
        except Exception as e:
            print(f"Body parsing exception: {str(e)}")
    # Fallback to direct dictionary parameter extraction if called via backend invokes
    elif isinstance(event, dict):
        payload_data = event

    # ==============================================================================
    # 🚨 TRACK A: DAY 2 PLATFORM MAINTENANCE HOOK (Action / Invocation Parse)
    # ==============================================================================
    if "maintenance_mode" in payload_data:
        flag = payload_data.get("maintenance_mode", "false")
        MAINTENANCE_STATE["active"] = (str(flag).lower() == "true")
        print(f"Platform Action Hook: Maintenance mode toggled to {MAINTENANCE_STATE['active']}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'SUCCESS',
                'maintenance_mode': 'true' if MAINTENANCE_STATE["active"] else 'false',
                'maintenance_mode_active': MAINTENANCE_STATE["active"]
            })
        }

    # ==============================================================================
    # 🟢 TRACK B: IN-BAND OPERATIONS ROUTER (Flask Container Traffic Parsing)
    # ==============================================================================
    # Determine if the Flask app is just checking the status (GET) or sending text to analyze (POST)
    is_status_query = True
    text_to_analyze = ""
    
    if "text" in payload_data:
        text_to_analyze = payload_data["text"]
        is_status_query = False

    # 1. LIVE APP LAYOUT CHECK (Flask route queries via HTTP GET)
    if is_status_query:
        print(f"Flask App Status Query. Returning maintenance_mode: {MAINTENANCE_STATE['active']}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'maintenance_mode': 'true' if MAINTENANCE_STATE["active"] else 'false'
            })
        }

    # 2. LIVE SENTIMENT ANALYSIS ENGINE (Flask submissions via HTTP POST)
    print(f"Executing NLP Sentiment analysis for payload string: '{text_to_analyze}'")
    try:
        comprehend_response = comprehend.detect_sentiment(
            Text=text_to_analyze,
            LanguageCode='en'
        )
        detected_sentiment = comprehend_response.get('Sentiment', 'NEUTRAL')
        mapped_badge = f"🟡 {detected_sentiment}"
        
        if detected_sentiment == "POSITIVE": mapped_badge = "🟢 POSITIVE"
        if detected_sentiment == "NEGATIVE": mapped_badge = "🔴 NEGATIVE"
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'SUCCESS',
                'sentiment': mapped_badge
            })
        }
    except Exception as e:
        print(f"Amazon Comprehend API Exception: {str(e)}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'FALLBACK', 'sentiment': '🟡 NEUTRAL'})
        }
