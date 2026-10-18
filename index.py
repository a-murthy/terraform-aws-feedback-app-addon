import os
import json
import boto3

# Initialize the AWS NLP and Systems Manager clients natively
comprehend = boto3.client('comprehend', region_name='us-east-1')
ssm        = boto3.client('ssm', region_name='us-east-1')

PARAMETER_NAME = "/platform/maintenance_mode"

# ==============================================================================
# 🎯 PASSIVE MEMORY DISCOVERY (No Side-Effect Cloud Writes)
# ==============================================================================
def get_maintenance_state():
    try:
        response = ssm.get_parameter(Name=PARAMETER_NAME)
        return str(response['Parameter']['Value']).strip().lower() == 'true'
    except Exception as e:
        print(f"SSM Parameter Read Block (Defaulting to Normal Operations): {str(e)}")
        return False

def handler(event, context):
    print("--- DUAL-TIER DURABLE ADD-ON INVOCATION DETECTED ---")
    print(f"Incoming Event Payload: {json.dumps(event)}")
    
    # 1. Extract the deterministic HTTP method from the AWS proxy wrapper context
    http_method = event.get('requestContext', {}).get('http', {}).get('method', '')
    if not http_method and isinstance(event, dict):
        http_method = event.get('httpMethod', event.get('requestContext', {}).get('stage', 'POST'))

    # 2. BULLETPROOF UNPACKING: Flatten event data cleanly across proxy and direct activations
    payload_data = {}
    
    # Track A: Handle standard stringified JSON bodies sent via HTTP proxy integrations
    if isinstance(event, dict) and event.get('body'):
        try:
            payload_data = json.loads(event['body'])
        except Exception:
            pass
            
    # Track B: Handle raw dictionary payloads passed directly from HCP UI invocations
    if not payload_data and isinstance(event, dict):
        payload_data = event

    # Ensure payload_data is a dictionary to prevent attribute extraction crashes
    if not isinstance(payload_data, dict):
        payload_data = {}

    # ==============================================================================
    # 🚨 LIFECYCLE ROUTE 1: DAY 2 PLATFORM MAINTENANCE TOGGLE (HCP UI Actions)
    # ==============================================================================
    if "maintenance_mode" in payload_data:
        flag = str(payload_data.get("maintenance_mode", "false")).lower().strip()
        ssm.put_parameter(Name=PARAMETER_NAME, Value=flag, Type='String', Overwrite=True)
        is_active = (flag == 'true')
        
        print(f"Durable Storage Sync: Maintenance state key updated to {is_active}")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'status': 'SUCCESS',
                'maintenance_mode': 'true' if is_active else 'false',
                'maintenance_mode_active': is_active
            })
        }

    # ==============================================================================
    # 🚨 LIFECYCLE ROUTE 2: IN-BAND RUNTIME OVERLAYS (Flask Traffic Channeling)
    # ==============================================================================
    
    # A. Page Loads (HTTP GET Check)
    if str(http_method).upper() == 'GET':
        current_lockout_state = get_maintenance_state()
        print(f"Flask Dynamic Pull. Fetching persistent key: {current_lockout_state}")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'maintenance_mode': 'true' if current_lockout_state else 'false'
            })
        }

    # B. Form Submissions (HTTP POST Check)
    text_to_analyze = str(payload_data.get("text", "")).strip()
    if not text_to_analyze:
        print("Empty text payload encountered or missing token.")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
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
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'status': 'SUCCESS', 'sentiment': mapped_badge})
        }
    except Exception as e:
        print(f"Amazon Comprehend API Exception: {str(e)}")
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'status': 'FALLBACK', 'sentiment': '🟡 NEUTRAL'})
        }
