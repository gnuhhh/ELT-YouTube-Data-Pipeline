import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('./.env')
API_KEY = os.getenv('API_KEY')

CHANNEL_HANDLE = 'MrBeast'

def get_channel_id():
    try:
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'
        response = requests.get(url)
        data = response.json()
        response.raise_for_status()
        print(json.dumps(data, indent = 4))
        channel_items = data['items'][0]
        channel_playlist_id = channel_items['contentDetails']['relatedPlaylists']['uploads']
        return channel_playlist_id
    except requests.exceptions.RequestException as e:
        raise e

if __name__ == "__main__":
    print(get_channel_id())