import uuid
import time
import re
import os
import sys
import ast

import numpy as np
import pandas as pd
from selenium import webdriver
from googleapiclient.discovery import build
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv

# returns information about the video as data frame and for how much it should run
def get_data_video(v_url, curr_depth, vid_id, youtube, parent_id = 'None'):
    data = np.array([])
    code = v_url.split('v=')[1]
    vid_suff = code
    request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id=vid_suff
    )
    response = request.execute()
    main_info = response['items'][0]['snippet']
    channel_name = main_info['channelTitle']
    video_title= main_info['title']
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
    time_to_run = time_collect(duration)
    request_channel = youtube.channels().list(
        part="statistics",
        id= main_info['channelId']
    )
    data = np.append(data ,np.array
        ([vid_id ,video_title, view_counts, likes, dislikes, comments, video_ids, channel_name, channel_ids
         ,published_ats ,duration]))
    channels_info = request_channel.execute()

    if channels_info['items'][0]['statistics']['hiddenSubscriberCount' ]==False:
        subs_count = channels_info['items'][0]['statistics']['subscriberCount']
    else:
        subs_count = None
    data = np.append(data ,[subs_count ,v_url ,curr_depth ,parent_id])

    return data ,time_to_run

# returns count of seconds to run video
def time_collect(duration):
    if len(duration) > 2:
        return 5*60
    elif len(duration) == 2:
        if int(duration[1]) < 10:
            return int(duration[1])*60
        else:
            return 5*60
    elif(len(duration) == 1):
        return int(duration[0])


def collect_recommendations(depth, search_word, youtube):
    data = pd.DataFrame([], columns=['id', 'video_title', 'view_counts', 'likes', 'dislikes', 'comments', 'video_id',
                                     'channel_name', 'channel_id', 'published_at', 'duration', 'subscriber_count',
                                     'video_url', 'level', 'parent_id'])
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(ChromeDriverManager().install())
    baseurl = "http://youtube.com"
    driver.get("http://youtube.com")
    driver.get(f'{baseurl}/search?q={search_word}')
    list_youtube = []
    time.sleep(30)
    elems = driver.find_elements_by_xpath("//a[@href]")
    for elem in elems:
        if str(elem.get_attribute("href")).find('v=') != -1:
            list_youtube.append(elem.get_attribute("href"))
    list_youtube = list(dict.fromkeys(list_youtube))
    print(len(list_youtube))
    for vid in list_youtube:
        vid_id = uuid.uuid4()
        driver.get(vid)
        time.sleep(10)
        try:
            button = driver.find_element_by_class_name('ytp-ad-skip-button-container')
            button.click()
        except:
            print('no ad')
        curr = 0
        # curr is the current depth we are at it is 0 since we are at the main search page
        # you don't need to play with the the depth numbers
        x_data, duration = get_data_video(vid, curr, vid_id,youtube)
        # the duration accounts for either full of the video if it is less than 10 mins otherwise the video will run for 5 mins
        # you can replace this with less time like 20 second to make the experiment faster but then the emulating of user behaviour
        # can get effected
        #time.sleep(duration)
        time.sleep(30)
        # create dataset
        a_series = pd.Series(x_data, index=data.columns)
        data = data.append(a_series, ignore_index=True)
        depth_current = 0
        while depth_current < depth:
            depth_current = depth_current + 1
            # wait for recommendation
            wait = WebDriverWait(driver, 10)
            presence = EC.presence_of_element_located
            wait.until(presence((By.ID, "related")))
            # collect the urls for the recommendations
            list_recommendation = driver.find_elements_by_xpath('//*[@id="dismissible"]/div/div[1]/a')
            # for each recommendation get the data
            for reco in range(0, len(list_recommendation)):
                reco_id = uuid.uuid4()
                reco_data, duration = get_data_video(list_recommendation[reco].get_attribute("href"), depth_current,
                                                     reco_id, youtube, vid_id)
                r_series = pd.Series(reco_data, index=data.columns)

                data = data.append(r_series, ignore_index=True)
            # if done break
            if depth == 1:
                break
            else:

                driver.get(list_recommendation[0].get_attribute("href"))
                time.sleep(10)
                try:
                    button = driver.find_element_by_class_name('ytp-ad-skip-button-container')
                    button.click()
                except:
                    print('no ad')

                time.sleep(30)
    path = 'data/' + search_word + '_experiment_1.csv'
    data.to_csv(path, index=False)
    return data


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('YOUTUBE_TOKEN')
    youtube = build('youtube', 'v3', developerKey=api_key)
    search_words = ast.literal_eval(sys.argv[1])
    for word in search_words:
        collect_recommendations(1, word, youtube)

