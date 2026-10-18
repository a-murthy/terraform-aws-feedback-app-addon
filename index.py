import os
import json
import boto3

# Initialize the AWS NLP and Systems Manager clients natively
comprehend = boto3.client('comprehend', region_name='us-east-1')
ssm        = boto3.client('ssm', region_name='us-east-1')

PARAMETER_NAME = "/platform/maintenance_mode"

def get_maintenance_state():
    try:
        response = ssm.get_parameter(Name=PARAMETER_NAME)
        return response['Parameter']['Value'] == 'true'
    except Exception:
        # 🟢 Safe structural fallback: creates the parameter card string dynamically if it is missing
        try:
            ssm.put_parameter(Name=PARAMETER_NAME, Value='false', Type='String', Overwrite=True)
        except Exception:
            pass
        return False

def handler(event, context):
    print("--- DUAL-TIER DURABLE ADD-ON INVOCATION DETECTED ---")
    print(f"Incoming Event Payload: {json.dumps(event)}")
    
    # 🟢 FIX: Extract the deterministic HTTP method from the AWS proxy wrapper
    http_method = event.get('requestContext', {}).get('http', {}).get('method', 'POST')
    if 'httpMethod' in event:
        http_method = event['httpMethod']
    
    payload_data = {}
    if isinstance(event, dict) and event.get('body'):
        try:
            payload_data = json.loads(event['body'])
        except Exception:
            pass
    elif isinstance(event, dict):
        # Only unpack root dictionary if this isn't an AWS Proxy Event wrapper
        if 'requestContext' not in event:
            payload_data = event

    # ==============================================================================
    # 🚨 TRACK A: DAY 2 PLATFORM MAINTENANCE HOOK (HCP UI Button Intercepts)
    # ==============================================================================
    if "maintenance_mode" in payload_data:
        flag = str(payload_data.get("maintenance_mode", "false")).lower().strip()
        ssm.put_parameter(Name=PARAMETER_NAME, Value=flag, Type='String', Overwrite=True)
        is_active = (flag == 'true')
        
        print(f"Durable Storage Sync: Maintenance state key updated to {is_active}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'SUCCESS',
                'maintenance_mode': 'true' if is_active else 'false',
                'maintenance_mode_active': is_active
            })
        }

    # ==============================================================================
    # 🟢 TRACK B: IN-BAND OPERATIONS ROUTER (Flask Container Traffic Parsing)
    # ==============================================================================
    
    # 1. LIVE APP LAYOUT CHECK (Flask route queries via HTTP GET on page load)
    # Uses clean HTTP isolation instead of brittle string sniffing in dictionaries
    if http_method == 'GET':
        current_lockout_state = get_maintenance_state()
        print(f"Flask Dynamic Pull. Fetching persistent key: {current_lockout_state}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'maintenance_mode': 'true' if current_lockout_state else 'false'
            })
        }

    # 2. LIVE SENTIMENT ANALYSIS ENGINE (Flask submissions via HTTP POST)
    text_to_analyze = payload_data.get("text", "").strip()
    if not text_to_analyze:
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'SUCCESS', 'sentiment': '🟡 NEUTRAL'})
        }

    print(f"Executing NLP Sentiment analysis for payload string: '{text_to_analyze}'")
    try:
        comprehend_response = comprehend.detect_sentiment(Text=text_to_analyze, LanguageCode='en')
        detected_sentiment = comprehend_response.get('Sentiment', 'NEUTRAL')
        mapped_badge = f"🟡 {detected_sentiment}"
        
        if detected_sentiment == "POSITIVE": mapped_badge = "🟢 POSITIVE"
        if detected_sentiment == "NEGATIVE": mapped_badge = "🔴 NEGATIVE"
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'SUCCESS', 'sentiment': mapped_badge})
        }
    except Exception as e:
        print(f"Amazon Comprehend API Exception: {str(e)}")
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'status': 'FALLBACK', 'sentiment': '🟡 NEUTRAL'})
        }

