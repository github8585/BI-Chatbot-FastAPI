import requests
import json

# Constants
AUTH_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
API_URL = "https://test.api.amadeus.com/v1/reference-data/locations/hotels/by-city?cityCode=BKK&radius=30&radiusUnit=KM&amenities=SPA,FITNESS_CENTER,AIR_CONDITIONING,RESTAURANT&hotelSource=ALL"
JSON_FILE_PATH = 'data.json'

# Function to get access token
def get_access_token(api_credentials):
    auth_data = {
        "grant_type": "client_credentials",
        "client_id": api_credentials['api_key'],
        "client_secret": api_credentials['api_secret']
    }
    response = requests.post(AUTH_URL, data=auth_data)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        raise Exception("Failed to obtain access token")

# Function to get hotel data
def get_hotel_data(access_token):
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(API_URL, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception("Failed to fetch hotel data")

# Function to save data to a file
def save_data_to_file(data, file_path):
    with open(file_path, 'w') as outfile:
        json.dump(data, outfile)

# Main execution
if __name__ == "__main__":
    # Replace these with actual credentials or environment variables
    api_credentials = {
        "api_key": "api_key",
        "api_secret": "api_secret"
    }

    try:
        access_token = get_access_token(api_credentials)
        hotel_data = get_hotel_data(access_token)
        save_data_to_file(hotel_data, JSON_FILE_PATH)
        print("Data saved successfully.")
    except Exception as e:
        print(f"Error: {e}")
