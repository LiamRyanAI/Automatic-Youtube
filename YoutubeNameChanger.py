import os
import re
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


# Define the scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.readonly', 
          'https://www.googleapis.com/auth/youtube']

TOKEN_FILE = 'token.pickle'

def load_credentials():
    creds = None
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    return creds

def authenticate_youtube():
    creds = load_credentials()
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secret.json', SCOPES)
            creds = flow.run_local_server(port=0)
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
    return build('youtube', 'v3', credentials=creds)

# Use this function to authenticate
youtube = authenticate_youtube()

# Function to get your channel ID
def get_my_channel_id(youtube):
    request = youtube.channels().list(
        part="id",
        mine=True
    )
    response = request.execute()
    return response['items'][0]['id'] if response['items'] else None

# Function to list videos from your channel using channel ID
def list_my_videos(youtube, channel_id, part='snippet', max_results=50):
    request = youtube.search().list(
        part=part,
        channelId=channel_id,
        maxResults=max_results,
        type="video"
    )
    return request.execute()

# Get your channel ID
channel_id = get_my_channel_id(youtube)
if channel_id:
    # List your videos
    videos = list_my_videos(youtube, channel_id)
    print(videos)
    # Rest of your code to find and update the video title...
else:
    print("Channel not found.")

# Function to find a video with a title ending in '.mp4'
def find_video_with_mp4(videos):
    for item in videos.get('items', []):
        title = item['snippet']['title']
        if title.endswith('.mp4'):
            return item['id'], title
    return None, None

# Function to update the video's title
# Function to update the video's title
def update_video_title(youtube, video_id, new_title):
    # First, retrieve the current snippet of the video
    video_response = youtube.videos().list(
        part='snippet',
        id=video_id
    ).execute()

    if not video_response['items']:
        return None

    current_snippet = video_response['items'][0]['snippet']

    # Update the title within the snippet
    current_snippet['title'] = new_title

    # Now, make the update request with the modified snippet
    request = youtube.videos().update(
        part="snippet",
        body={
            "id": video_id,
            "snippet": current_snippet
        }
    )
    return request.execute()


# List your videos
videos = list_my_videos(youtube, channel_id)

# Find the video and update its title
video_id, video_title = find_video_with_mp4(videos)
if video_id:
    # Ensure that video_id is a string
    video_id = video_id.get('videoId') if isinstance(video_id, dict) else video_id

    new_title = re.sub(r'\.mp4$', '', video_title)  # Removes '.mp4' from the end of the title
    update_response = update_video_title(youtube, video_id, new_title)
    print(f"Updated video: {new_title} (ID: {video_id})")
    print("Update response:", update_response)  # Print the API response
else:
    print("No video ending with '.mp4' found.")
