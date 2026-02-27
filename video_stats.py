import requests
import json
import os
from dotenv import load_dotenv

load_dotenv('./.env')
API_KEY = os.getenv('API_KEY')
CHANNEL_HANDLE = 'MrBeast'
max_results = 50

def get_channel_id():
    try:
        url = f'https://youtube.googleapis.com/youtube/v3/channels?part=contentDetails&forHandle={CHANNEL_HANDLE}&key={API_KEY}'
        response = requests.get(url)
        data = response.json()
        response.raise_for_status()
        channel_items = data['items'][0]
        channel_playlist_id = channel_items['contentDetails']['relatedPlaylists']['uploads']
        return channel_playlist_id
    except requests.exceptions.RequestException as e:
        raise e

def get_video_ids(playlist_id):
    video_ids = []
    page_token = None
    base_url = f'https://youtube.googleapis.com/youtube/v3/playlistItems?part=contentDetails&maxResults={max_results}&playlistId={playlist_id}&key={API_KEY}'
    
    while True:
        url = base_url
        if page_token:
            url += f'&pageToken={page_token}'
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            for item in data.get('items', []):
                video_id = item['contentDetails']['videoId']
                video_ids.append(video_id)
            page_token = data.get('nextPageToken')
            if not page_token:
                break
        except requests.exceptions.RequestException as e:
            raise e
    return video_ids

def batch_list(video_ids, batch_size):
    for video_id in range(0, len(video_ids), batch_size):
        yield video_ids[video_id: video_id + batch_size]

def extract_video_stats(video_ids):
    video_stats = []
    for batch in batch_list(video_ids, max_results):
        video_ids_str = ','.join(batch)
        url = f'https://youtube.googleapis.com/youtube/v3/videos?part=snippet&part=contentDetails&part=statistics&id={video_ids_str}&key={API_KEY}'
        response = requests.get(url)
        data = response.json()
        for item in data.get('items', []):
            video_id = item['id']
            snippet = item['snippet']
            content_details = item['contentDetails'] 
            statistics = item['statistics']

            video_stat = {
                'video_id': video_id,
                'publish_at': snippet['publishedAt'],
                'title': snippet['title'],
                'duration': content_details['duration'],
                'view_count': statistics.get('viewCount'),
                'like_count': statistics.get('likeCount'),
                'comment_count': statistics.get('commentCount')
            }
            video_stats.append(video_stat)
    return video_stats

if __name__ == "__main__":
    playlist_id = get_channel_id()
    video_ids = get_video_ids(playlist_id)
    extract_video_stats(video_ids)