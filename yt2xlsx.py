from googleapiclient.discovery import build

import pandas as pd

# For API key stored as an environmentbal variable
import os
#For Timer
import time

# set api key from local environment
# if you don't have any evironmental variables set, just set your API_KEY = 'YOUR_API_KEY_HERE'
API_KEY = os.environ.get('API_KEY')
# set API service vars
API_SERVICE_NAME = 'youtube'
API_VERSION = 'v3'

def get_channel_id(username):

    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
    request = youtube.channels().list(
            part='statistics',
            forUsername=username).execute()
    
    video_count = request['items'][0]['statistics']['videoCount']
    ch_id = request['items'][0]['id']

    return ch_id

def get_channel_df(channel_id):
    time_start = time.perf_counter()
    
    # Step 1
    youtube = build(API_SERVICE_NAME, API_VERSION, developerKey=API_KEY)
    
    # Get number of videos in uploads playlist
    vid_response = youtube.channels().list(part = 'statistics',
                                      id = channel_id).execute()
    video_count = vid_response['items'][0]['statistics']['videoCount']

    print()
    print(f'Scraping {video_count} videos for channel id: {channel_id} ...')
    print()
    
    # Get upload playlist id
    response = youtube.channels().list(part = 'contentDetails',
                                      id = channel_id).execute()
    playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']

    # Step 2
    
    videos_result = []
    nextPageToken = None
    while 1:
        playlist_response = youtube.playlistItems().list(playlistId = playlist_id,
                                                        part = 'snippet',
                                                        maxResults = 50,
                                                        pageToken = nextPageToken).execute()
        
        videos_result.extend(playlist_response['items'])
        nextPageToken = playlist_response.get('nextPageToken')
        
        if nextPageToken is None:
            break
    
    time_end = time.perf_counter()
    print(f'Finished in {time_end-time_start} seconds.')
    
    results = [] 
    
    for video in videos_result:
        date = video['snippet']['publishedAt'][:10]
        vid_id = video['snippet']['resourceId']['videoId']
       # description = video['snippet']['description']
        title = video['snippet']['title']
        
        data = {'Date' : date,
                'Video ID' : vid_id,
               # 'Description' : description,
                'Title' : title}
                
        results.append(data)
    
    df = pd.DataFrame(results)
    return df

if __name__ == '__main__':
    answer = input('Do you have the channel id? (y/[n])')
    
    if answer == 'y':
        channel_id = input("Enter the channel ID: ")
        df = get_channel_df(channel_id)
        file_name = input('What would you like to name your file? Do not include the file extension ')
        df.to_excel(f'{file_name}.xlsx', index=False, header=True)
        print('File saved.')
        print()

    elif answer == 'n' :
        channel_username = input("Enter the channel username: ")
        channel_id = get_channel_id(channel_username)
        df = get_channel_df(channel_id)
        file_name = input('What would you like to name your file? Do not include the file extension ')
        df.to_excel(f'{file_name}.xlsx', index=False, header=True)
        print('File saved.')
        print()

    else: 
        print()
        print('Please enter a valid response.')
        print()