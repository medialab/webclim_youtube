import re
import os
import sys

import numpy as np
import pandas as pd
from googleapiclient.discovery import build
from dotenv import load_dotenv


def get_data_video(v_url, vid_id):
    data = np.array([])
    code = v_url.split('v=')[1][0:11]
    vid_suff = code
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=vid_suff
    )
    response = request.execute()
    try:

        main_info = response['items'][0]['snippet']

        channel_name = main_info['channelTitle']
        video_title = main_info['title']
        channel_ids = main_info['channelId']
        published_ats = main_info['publishedAt']
        video_ids = response['items'][0]['id']
        view_counts = response['items'][0]['statistics']['viewCount']
        try:
            likes = response['items'][0]['statistics']['likeCount']
        except:
            likes = 'non'
        try:
            dislikes = response['items'][0]['statistics']['dislikeCount']
        except:
            dislikes = 'non'
        try:
            comments = response['items'][0]['statistics']['commentCount']
        except:
            comments = 'non'
        duration = re.findall(r'\d+', response['items'][0]['contentDetails']['duration'])
        request_channel = youtube.channels().list(
            part="statistics",
            id=main_info['channelId']
        )
        data = np.append(data, np.array(
            [vid_id, video_title, view_counts, likes, dislikes, comments, video_ids, channel_name, channel_ids,
             published_ats, duration]))
        channels_info = request_channel.execute()
        if (channels_info['items'][0]['statistics']['hiddenSubscriberCount'] == False):
            subs_count = channels_info['items'][0]['statistics']['subscriberCount']
        else:
            subs_count = None
        data = np.append(data, [subs_count, v_url])
    except:
        print('Error')
    return data


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('YOUTUBE_TOKEN')
    youtube = build('youtube', 'v3', developerKey=api_key)
    file_name = sys.argv[1]
    video_ids = pd.read_csv(file_name)
    ids = list(video_ids['video_id'])
    data = pd.DataFrame([], columns=['id', 'video_title', 'view_counts', 'likes', 'dislikes', 'comments', 'video_id',
                                     'channel_name', 'channel_id', 'published_at', 'duration', 'subscriber_count',
                                     'video_url'])
    for i in ids:
        baseurl = "http://youtube.com"
        x_data = get_data_video(f'{baseurl}/watch?v={i}',i)
        a_series = pd.Series(x_data, index=data.columns)
        data = data.append(a_series, ignore_index=True)
    path = 'data/' + 'collected_youtube_data.csv'
    data.to_csv(path, index=False)


