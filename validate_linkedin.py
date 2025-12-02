
import os
import requests
from dotenv import load_dotenv

load_dotenv()

def validate_linkedin():
    token = os.getenv("LINKEDIN_ACCESS_TOKEN")
    urn = os.getenv("LINKEDIN_PERSON_URN")
    
    print(f"Checking credentials...")
    print(f"Token present: {'Yes' if token else 'No'}")
    print(f"URN present: {'Yes' if urn else 'No'} ({urn if urn else 'None'})")
    
    if not token:
        print("ERROR: LINKEDIN_ACCESS_TOKEN is missing in .env")
        return

    # Test the token by fetching the user's profile (me endpoint)
    url = "https://api.linkedin.com/v2/me"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-Restli-Protocol-Version": "2.0.0"
    }
    
    try:
        print(f"\nTesting token against {url}...")
        response = requests.get(url, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("SUCCESS: Token is valid!")
            print(f"User: {data.get('localizedFirstName')} {data.get('localizedLastName')}")
            print(f"ID: {data.get('id')}")
            
            # Verify URN matches
            expected_urn = f"urn:li:person:{data.get('id')}"
            if urn != expected_urn:
                print(f"\nWARNING: Mismatch in URN!")
                print(f"Configured URN: {urn}")
                print(f"Actual URN from token: {expected_urn}")
                print("Please update LINKEDIN_PERSON_URN in .env to the Actual URN.")
            else:
                print("\nURN configuration matches token user.")
                
        elif response.status_code == 403:
            print("FAILURE: Access Denied (403) on /me.")
            print("Trying OIDC /userinfo endpoint...")
            
            # Fallback to OIDC userinfo
            oidc_url = "https://api.linkedin.com/v2/userinfo"
            oidc_response = requests.get(oidc_url, headers=headers)
            
            if oidc_response.status_code == 200:
                data = oidc_response.json()
                print("SUCCESS: Token is valid (OIDC)!")
                print(f"User: {data.get('given_name')} {data.get('family_name')}")
                print(f"ID: {data.get('sub')}")
                
                # Verify URN matches
                expected_urn = f"urn:li:person:{data.get('sub')}"
                if urn != expected_urn:
                    print(f"\nWARNING: Mismatch in URN!")
                    print(f"Configured URN: {urn}")
                    print(f"Actual URN from token: {expected_urn}")
                    print("Please update LINKEDIN_PERSON_URN in .env to the Actual URN.")
                else:
                    print("\nURN configuration matches token user.")
            else:
                print(f"FAILURE: OIDC check also failed: {oidc_response.status_code}")
                print(oidc_response.text)

        elif response.status_code == 401:
            print("FAILURE: Unauthorized (401). Your token is invalid or expired.")
            print("Please generate a new access token from the LinkedIn Developer Portal.")
        else:
            print(f"FAILURE: Unexpected error: {response.text}")
            
    except Exception as e:
        print(f"Error during validation: {e}")

if __name__ == "__main__":
    validate_linkedin()
