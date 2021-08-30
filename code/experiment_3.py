import uuid
import time
import re
import os
import sys
import ast

import numpy as np
import pandas as pd
from googleapiclient.discovery import build
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from dotenv import load_dotenv



def get_data_video(v_url, curr_depth, vid_id,history='None', parent_id = 'None', level='None', order='None'):
        data = np.array([])
        code = v_url.split('v=')[1][0:11]
        vid_suff = code
        request = youtube.videos().list(
        part="snippet,contentDetails,statistics",
        id = vid_suff
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
            time_to_run = time_collect(duration)
            request_channel = youtube.channels().list(
            part = "statistics",
            id = main_info['channelId']
        )
            data = np.append(data,np.array([vid_id,video_title,view_counts,likes,dislikes,comments , video_ids,channel_name,channel_ids,published_ats,duration]))
            channels_info = request_channel.execute()
            if (channels_info['items'][0]['statistics']['hiddenSubscriberCount']==False):

                subs_count = channels_info['items'][0]['statistics']['subscriberCount']
            else:
                subs_count = None
            data = np.append(data,[subs_count,v_url,level,parent_id,order,history])
        except:
            print('Error')
            time_to_run = 0
        return data,time_to_run

# specify video run time
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

# choose a random set of videos from the provided csv and sixth video from the most viewed ones and not from the 5 videos
def choose_set_videos(videos_flagged, run):
    videos_visit = videos_flagged.sample(n=5)
    indexs_remove = list(videos_visit.index)
    videos_flagged = videos_flagged.drop(indexs_remove)
    first_video = videos_flagged.iloc[run]

    return videos_visit, first_video

# first level of recommendation collection
def collect_recommendation_first_level(depth, vid_to_start, youtube,driver,history='None'):
    data = pd.DataFrame([], columns=['id', 'video_title', 'view_counts', 'likes', 'dislikes', 'comments', 'video_id',
                                     'channel_name', 'channel_id', 'published_at', 'duration', 'subscriber_count',
                                     'video_url', 'level', 'parent_id', 'order','history'])

    baseurl = "http://youtube.com"
    driver.get(f'{baseurl}/watch?v={vid_to_start}')
    vid = f'{baseurl}/watch?v={vid_to_start}'
    list_youtube = []
    vid_id = uuid.uuid4()
    time.sleep(10)
    try:
        button = driver.find_element_by_class_name('ytp-ad-skip-button-container')
        button.click()
    except:
        print('no ad')

    # time.sleep(30)
    curr = 0
    x_data, duration = get_data_video(vid, curr, vid_id,history)
    time.sleep(10)
    a_series = pd.Series(x_data, index=data.columns)
    data = data.append(a_series, ignore_index=True)

    depth_current = 0
    wait = WebDriverWait(driver, 10)
    presence = EC.presence_of_element_located
    wait.until(presence((By.ID, "related")))
    list_recommendation = driver.find_elements_by_xpath('//*[@id="dismissible"]/div/div[1]/a')
    recos = []
    for i in range(0, len(list_recommendation)):
        recos.append(list_recommendation[i].get_attribute("href"))
    for reco in range(0, 10):
        reco_id = uuid.uuid4()
        wait = WebDriverWait(driver, 10)
        presence = EC.presence_of_element_located
        wait.until(presence((By.ID, "related")))
        try:
            data_reco = collect_recommendation_second_level(recos[reco], reco_id, vid_id, driver, data, reco,history)
            data = data.append(data_reco, ignore_index=True)
        except:
            print('error in main small run')
    for reco_s in range(10, len(recos)):
        reco_data, duration = get_data_video(recos[reco_s], depth_current, reco_id, history,vid_id, 1, reco_s)
        r_series = pd.Series(reco_data, index=data.columns)
        data = data.append(r_series, ignore_index=True)
    driver.close()

    return data

#second level of recommendation collection
def collect_recommendation_second_level(vid_url, reco_id, main_id, driver, data_s, order,history):
    data = pd.DataFrame([], columns=['id', 'video_title', 'view_counts', 'likes', 'dislikes', 'comments', 'video_id',
                                     'channel_name', 'channel_id', 'published_at', 'duration', 'subscriber_count',
                                     'video_url', 'level', 'parent_id', 'order','history'])
    code = vid_url.split('v=')[1]
    baseurl = "http://youtube.com"
    driver.get(f'{baseurl}/watch?v={code}')
    time.sleep(6)
    try:
        button = driver.find_element_by_class_name('ytp-ad-skip-button-container')
        button.click()
    except:
        print('no ad')
    try:
        vid_id = uuid.uuid4()
        curr = 0
        x_data, duration = get_data_video(f'{baseurl}/watch?v={code}', curr, reco_id, history,main_id, 1, order)
        time.sleep(10)
        a_series = pd.Series(x_data, index=data_s.columns)
        data = data.append(a_series, ignore_index=True)
        depth_current = 0
        wait = WebDriverWait(driver, 10)
        presence = EC.presence_of_element_located
        wait.until(presence((By.ID, "related")))
        list_recommendation = driver.find_elements_by_xpath(('//*[@id="dismissible"]/div/div[1]/a'))
        for reco in range(0, len(list_recommendation)):
            wait = WebDriverWait(driver, 10)
            wait.until(presence((By.ID, "related")))
            reco_id_t = uuid.uuid4()
            reco_data, duration = get_data_video(list_recommendation[reco].get_attribute("href"), depth_current, reco_id_t,
                                                 history,reco_id, 2, reco)
            r_series = pd.Series(reco_data, index=data_s.columns)
            data = data.append(r_series, ignore_index=True)
    except:
         print('no data small run')

    return data


def full_run(videos_visit, test_video):
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(ChromeDriverManager().install())

    baseurl = "http://youtube.com"
    driver.get("http://youtube.com")
# Number of videos to run before starting the data collection
    for i in range(0, 5):
        video_di = videos_visit['video_id'].iloc[i]
        driver.get(f'{baseurl}/watch?v={video_di}')
        time.sleep(10)
        try:
            button = driver.find_element_by_class_name('ytp-ad-skip-button-container')
            button.click()
        except:
            print('no ad')
        dur = time_collect(videos_visit['duration'].iloc[i])
        #time.sleep(dur)
        time.sleep(12)
    video_di = test_video['video_id']
    driver.get(f'{baseurl}/watch?v={video_di}')
    time.sleep(10)
    try:
        button = driver.find_element_by_class_name('ytp-ad-skip-button-container')
        button.click()
    except:
        print('no ad')
    dur = time_collect(test_video['duration'])
    #time.sleep(dur)
    time.sleep(12)
    # start the collection of the recommendations
    data_collection = collect_recommendation_first_level(1, test_video['video_id'], youtube, driver, list(videos_visit['video_id']))
    # control group setting, first visit the same video we started the collection from in the previous experiment
    #if you want to remove control group just comment thess line and their data from return

    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(ChromeDriverManager().install())
    baseurl = "http://youtube.com"
    driver.get("http://youtube.com")
    video_di = test_video['video_id']
    driver.get(f'{baseurl}/watch?v={video_di}')
    time.sleep(10)
    try:
        button = driver.find_element_by_class_name('ytp-ad-skip-button-container')
        button.click()
    except:
        print('no ad')
    dur = time_collect(test_video['duration'])
    #time.sleep(dur)
    time.sleep(10)
    data_collection_2 = collect_recommendation_first_level(1, test_video['video_id'], youtube, driver)
    return data_collection, data_collection_2




if __name__=="__main__":
    load_dotenv()
    api_key = os.getenv('YOUTUBE_TOKEN')
    youtube = build('youtube', 'v3', developerKey=api_key)
    youtube = build('youtube', 'v3', developerKey=api_key)
    file_name = sys.argv[1]
    count_to_run = int(sys.argv[2])
    videos_to_choose_from = pd.read_csv(file_name)
    videos_to_choose_from = videos_to_choose_from.sort_values(by=['view_counts'], ascending=False)
    videos_to_choose_from = videos_to_choose_from[videos_to_choose_from['view_counts'] > 10000]
    data_control_group= pd.DataFrame([],
                             columns=['id', 'video_title', 'view_counts', 'likes', 'dislikes', 'comments', 'video_id',
                                      'channel_name', 'channel_id', 'published_at', 'duration', 'subscriber_count',
                                      'video_url', 'level', 'parent_id', 'order', 'history'])
    data_experimental_group = pd.DataFrame([], columns=['id', 'video_title', 'view_counts', 'likes', 'dislikes', 'comments',
                                               'video_id', 'channel_name', 'channel_id', 'published_at', 'duration',
                                               'subscriber_count', 'video_url', 'level', 'parent_id', 'order',
                                               'history'])
    # create the csv to start appending to it
    data_control_group.to_csv('data/exper3_control_group.csv')
    data_experimental_group.to_csv('data/exper3_experimental_group.csv')

    for i in range(0, count_to_run):
        current_run = 0
        videos_visit, test_video = choose_set_videos(videos_to_choose_from.iloc[0:], current_run)
        collect_user_with_his, collect_user_no_his = full_run(videos_visit, test_video)
        data_experimental_group = data_experimental_group.append(collect_user_with_his)
        collect_user_with_his.to_csv('data/exper3_experimental_group.csv', mode='a', header=False)
        data_control_group = data_control_group.append(collect_user_no_his)
        collect_user_no_his.to_csv('data/exper3_control_group.csv', mode='a', header=False)
        print(current_run)
        current_run = current_run + 1
