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