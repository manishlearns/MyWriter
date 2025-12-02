import requests
import secrets
import string
import urllib.parse
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
import time
import sys

# Configuration
REDIRECT_URI = "http://localhost:8080/callback"
SCOPE = "openid profile w_member_social email" 

class LinkedInAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        if parsed_path.path == "/callback":
            query_params = urllib.parse.parse_qs(parsed_path.query)
            if "code" in query_params:
                self.server.auth_code = query_params["code"][0]
                self.send_response(200)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"<h1>Authentication Successful!</h1><p>You can close this window and return to the terminal.</p>")
            else:
                self.send_response(400)
                self.wfile.write(b"Authentication failed.")
        else:
            self.send_response(404)

def get_access_token(client_id, client_secret, auth_code):
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": REDIRECT_URI,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()

def get_user_profile(access_token):
    url = "https://api.linkedin.com/v2/userinfo"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    return response.json()

def main():
    print("--- LinkedIn Access Token Generator ---")
    print("To use this script, ensure you have added 'http://localhost:8080/callback' to your Redirect URLs in the LinkedIn Developer Portal.")
    
    client_id = input("Enter your Client ID: ").strip()
    client_secret = input("Enter your Client Secret: ").strip()
    
    if not client_id or not client_secret:
        print("Client ID and Secret are required.")
        return

    # 1. Generate Auth URL
    state = "".join(secrets.choice(string.ascii_letters + string.digits) for _ in range(16))
    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": REDIRECT_URI,
        "state": state,
        "scope": SCOPE,
    }
    auth_url = f"https://www.linkedin.com/oauth/v2/authorization?{urllib.parse.urlencode(params)}"
    
    print(f"\nOpening browser to: {auth_url}")
    webbrowser.open(auth_url)
    
    # 2. Start Local Server to catch callback
    server_address = ("", 8080)
    httpd = HTTPServer(server_address, LinkedInAuthHandler)
    print("Waiting for callback on port 8080...")
    
    while not hasattr(httpd, "auth_code"):
        httpd.handle_request()
    
    auth_code = httpd.auth_code
    print("Authorization Code received!")
    
    # 3. Exchange Code for Token
    print("Exchanging code for access token...")
    token_data = get_access_token(client_id, client_secret, auth_code)
    
    if "access_token" not in token_data:
        print("Error getting access token:", token_data)
        return
    
    access_token = token_data["access_token"]
    print("Access Token obtained!")
    
    # 4. Get User URN
    print("Fetching user profile...")
    profile = get_user_profile(access_token)
    # The 'sub' field in userinfo is usually the ID, but for posting we might need the URN format
    # userinfo returns 'sub' like '7823482'
    # The URN is urn:li:person:{sub}
    
    user_id = profile.get("sub")
    if not user_id:
        print("Could not fetch user ID from profile:", profile)
        return

    person_urn = f"urn:li:person:{user_id}"
    
    print("\n" + "="*50)
    print("SUCCESS! Add these to your .env file:")
    print("="*50)
    print(f"LINKEDIN_ACCESS_TOKEN=\"{access_token}\"")
    print(f"LINKEDIN_PERSON_URN=\"{person_urn}\"")
    print("="*50)

if __name__ == "__main__":
    main()
