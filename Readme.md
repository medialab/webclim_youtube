# YouTube Recommendation data collection
This repository contains two approaches to collect data from YouTube with web scraping. The aim of these experiments is to 
simulate the user behaviour.
## General installation

The code was developped on Python 3.8.10.

To install the needed libraries, run in your terminal:

```
pip install -r requirements.txt
```
## Data Collection
### Collect video information 
Run the following command
```
   python3 code/collect_youtube_data.py "filename_and_path.csv"
```
Replace the "filename_and_path.csv" wih the name and path of the csv file that contains a column with video ids of the videos you want to collect their data. The column name should be 'video_id'

The Data collected is {video title, view count, likes, dislikes, comments count, channel name, channel id, subscribers count, video duration, video id}
The code will return a csv "data/collected_youtube_data.csv"
### Experiment 1: Collect the recommendation based on search word(s)
Run the following command
```
  python3 code/experiment_1.py "['search_word_1','search_word_2']"
```
After running the code csv files will be created for every search word in the data file. The collection is done for the recommendations in the main search page. Then for every video in the main list the system will go through each and collect
the recommended/related videos. 
### Experiment 2: Collect the recommendation based on starting with a video_id
Run the following command
```
  python3 code/experiment_2.py "['video_id_1','video_id_2']"
```
After running the code csv files will be created for every video in the list and it will be in the data file. The collection is done
for the recommended/related videos for the starting video then the system will go through the top 10 videos and collect their recommendations.


To simulate user behaviour the system play part of the videos either half of it or around 1 min based on the length of the video. You can change
these numbers in the ```time.sleep()``` functions.
### Experiment 3: Collect the recommendation based with user history
Experiment 3 starts with creating a user history by running 5 videos. To specify the list of videos the program will choose these videos from, supply csv file in the first argument of the command and it should have both the 'video_id','view_counts' and 'duration'. It is better to use collect_youtube_data.py to get a correct csv will all therequired columns.

Then the system will collect recommendation in two levels starting from the most viewed video from the provided list. To specify how many times to run the experiment, the user can change the second argument in the command.
```
 python3 code/experiment_3.py "videos_to_Choose_from.csv" "1"
```
The output of the code is two csv files. One is for a control group (without a history) under "expr3_control_group.csv" and the second one for experimental group with a history before initiating the data collection "exper3_experimental_group.csv". 


