import requests
import json

# The base URL for your Django server
BASE_URL = 'http://127.0.0.1:8000'

def test_jwt_api():
    print("--- 1. Requesting JWT Token ---")
    # Replace these credentials with your actual manager or superuser account
    credentials = {
        'username': 'admin',
        'password': 'admin123'
    }
    
    # Ping the token endpoint
    token_response = requests.post(f"{BASE_URL}/api/token/", json=credentials)
    
    if token_response.status_code == 200:
        print("✅ SUCCESS: Server verified credentials and generated JWT.")
        access_token = token_response.json().get('access')
        print(f"JWT Access Token: {access_token[:50]}...\n")
        
        print("--- 2. Querying Protected Metrics API ---")
        # Attach the token to the header using the Bearer scheme
        headers = {
            'Authorization': f'Bearer {access_token}'
        }
        
        # Ping the protected metrics endpoint
        metrics_response = requests.get(f"{BASE_URL}/api/metrics/", headers=headers)
        
        if metrics_response.status_code == 200:
            print("✅ SUCCESS: Server accepted the JWT and returned the SOC metrics!")
            print("JSON Payload:")
            print(json.dumps(metrics_response.json(), indent=4))
        else:
            print("❌ FAILED: The server rejected the JWT.")
    else:
        print("❌ FAILED: Invalid credentials. Could not obtain JWT.")

if __name__ == '__main__':
    test_jwt_api()
