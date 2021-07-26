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


def get_data_video(v_url, curr_depth, vid_id, parent_id = 'None', level='None', order='None'):
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
            data = np.append(data,[subs_count,v_url,level,parent_id,order])
        except:
            print('Error')
        return data,time_to_run


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


def random_walk(depth, vid_to_start, youtube):
    data = pd.DataFrame([], columns=['id', 'video_title', 'view_counts', 'likes', 'dislikes', 'comments', 'video_id',
                                     'channel_name', 'channel_id', 'published_at', 'duration', 'subscriber_count',
                                     'video_url', 'level', 'parent_id', 'order'])
    options = webdriver.ChromeOptions()
    options.add_argument("start-maximized")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    driver = webdriver.Chrome(ChromeDriverManager().install())
    baseurl = "http://youtube.com"
    driver.get("http://youtube.com")
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
    x_data, duration = get_data_video(vid, curr, vid_id)
    time.sleep(duration)
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
        data_reco = mini_walk(recos[reco], reco_id, vid_id, driver, data, reco)
        data = data.append(data_reco, ignore_index=True)
    for reco_s in range(10, len(recos)):
        reco_id = uuid.uuid4()
        reco_data, duration = get_data_video(recos[reco_s], depth_current, reco_id, vid_id, 1, reco_s)
        r_series = pd.Series(reco_data, index=data.columns)
        data = data.append(r_series, ignore_index=True)
    driver.close()
    path = 'data/' + vid_to_start + ' _experiment_2.csv'
    data.to_csv(path, index=False)


def mini_walk(vid_url, reco_id, main_id, driver, data_s, order):
    data = pd.DataFrame([], columns=['id', 'video_title', 'view_counts', 'likes', 'dislikes', 'comments', 'video_id',
                                     'channel_name', 'channel_id', 'published_at', 'duration', 'subscriber_count',
                                     'video_url', 'level', 'parent_id', 'order'])
    code = vid_url.split('v=')[1]
    baseurl = "http://youtube.com"
    driver.get(f'{baseurl}/watch?v={code}')
    time.sleep(6)
    try:
        button = driver.find_element_by_class_name('ytp-ad-skip-button-container')
        button.click()
    except:
        print('no ad')

    #vid_id = uuid.uuid4()
    curr = 0
    x_data, duration = get_data_video(f'{baseurl}/watch?v={code}', curr, reco_id, main_id, 1, order)
    time.sleep(duration)

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
                                             reco_id, 2, reco)
        r_series = pd.Series(reco_data, index=data_s.columns)
        data = data.append(r_series, ignore_index=True)

    return data


if __name__=="__main__":
    load_dotenv()
    # the list_is correspond to the id of channels [OANN, Tony Heller]
    api_key = os.getenv('YOUTUBE_TOKEN')
    youtube = build('youtube', 'v3', developerKey=api_key)
    videos = ast.literal_eval(sys.argv[1])
    for video in videos:
        random_walk(1, video,youtube)
