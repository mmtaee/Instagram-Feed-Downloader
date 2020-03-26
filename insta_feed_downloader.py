from InstagramAPI import InstagramAPI
from collections import defaultdict
import requests
import json
import sys
import os
import re 
import time
import getpass

class Processor:
    def __init__(self, username, password, ):
        self.API = InstagramAPI(username, password)
        self.API.login()
        self.API.getSelfUsernameInfo()
        self.username = username
        self.pagename = None

    def setPageName(self, pagename):
        self.pagename = pagename
        return self.pagename

    def getImageUrl(self):
        self.API.searchUsername(self.pagename)
        info = self.API.LastJson

        if 'user' not in info:
            print(f"User : '{self.pagename}' Not Found")
            return False

        # if info['user']['is_private'] == True:
        #     import json
        #     print(json.dumps(info['user']))
        #     print(f"User : '{self.pagename}' is Private .")
        #     return "False2"

        page_id = info["user"]["pk"]
        image = info['user']['hd_profile_pic_url_info']['url']
        return image, page_id

    def getUserFeed(self, usernameId):
        user_feed = []
        next_max_id = ''
        count = 0
        count_max_id =0
        while True:
            self.API.getUserFeed(usernameId, next_max_id)
            temp = self.API.LastJson
            if "message" in temp:
                print(f"'{self.pagename}' : Private Account")
                return False

            if "num_results" in temp:
                if temp['num_results'] == 0:
                    print(f"'{self.pagename}' : Has No post")
                    return False

            number = input("Number Of Post [0/Return]: ")
            while not number.isnumeric():
                number = input("Number Of Post : ")
            if number == "0":
                print("Return To Select Another Page ...")
                return False

            print("\n Requesting for User Feeds ...")
            for item in temp["items"]:
                user_feed.append(item)
                count += 1
                if count == number :
                    return user_feed
            if temp["more_available"] is False:
                return user_feed
            next_max_id = temp["next_max_id"]
            count_max_id += 1
            if count == 20 :
                count = 0 
                time.sleep(60)
                print('sleep')


       
    def processFeeds(self, feeds_list):
        feeds = defaultdict(list)
        for feed in feeds_list:
            if feed["media_type"] == 2:
                vid_url = feed['video_versions'][0]['url']
                feeds["videos"].append(vid_url)
            else : 
                if "carousel_media" in feed :
                    carousel_count = int(feed['carousel_media_count'])
                    for i in range(carousel_count):
                        img_url = feed['carousel_media'][i]['image_versions2']['candidates'][0]["url"]
                        feeds["images"].append(img_url)
                else : 
                    img_url = feed['image_versions2']['candidates'][0]["url"]
                    feeds["images"].append(img_url)
        path = os.getcwd() + f"/insta_files/{self.pagename}/"
        if not os.path.exists(path):
            os.mkdir(path)
        return dict(feeds)

    def pathToFile(self,feeds):
        name = os.getcwd() + f"/insta_files/{self.pagename}/urls.txt"
        with open(name, "a") as file:
            for item in feeds:
                if item == "videos":
                    file.write("Videos \n\n")

                    video_urls = feeds[item]
                    for url in video_urls:
                        text = url + "\n\n"
                        file.write(text)

                if item == "images":
                    file.write("Images \n\n")

                    image_urls = feeds[item]
                    for url in image_urls:
                        text = url + "\n\n"
                        file.write(text)

    def imageDownloader(self, image_urls):
        path = os.getcwd() + f"/insta_files/{self.pagename}/images/"
        if not os.path.isdir(path) :
            os.system("mkdir -p {}".format(path))
        print ("Start Images Downloading ...")
        for image in image_urls:
            name_file = re.findall(r"\/(\w+.jpg)" ,image)
            jpg_file = path + name_file[0]
            if not os.path.exists(jpg_file) :
                os.mknod(jpg_file)
                img = requests.get(image)
                with open (jpg_file , "wb") as file :
                    file.write(img.content)
            else : pass

    def videoDownloader(self, video_urls) :
        path_vid = os.getcwd() + f"/insta_files/{self.pagename}/videos/"
        if not os.path.isdir(path_vid):
            os.system("mkdir -p {}".format(path_vid))

        print("Start Video Downloading ...")
        for video in video_urls:
            name_file = re.findall(r"\/(\w+.mp4)" ,video)
            vid_file = path_vid + name_file[0]
            if not os.path.exists(vid_file) :
                os.mknod(vid_file)
                vid = requests.get(video)
                with open (vid_file , "wb") as file :
                    file.write(vid.content)
            else : pass
                

def main():
    repeat = True
    while repeat != False:  # username , password
        username = input("Instagram Username : ")
        password = getpass.getpass("Instagram Password : ")
        try:
            processor = Processor(username, password)
            repeat = False
        except:
            print("Invalid Username or Password !!!")
    
    base_loop = True
    while base_loop:
        main_loop = True
        while main_loop:
            page_name = input('pagename : ')
            processor.setPageName(page_name)
            hd_pic = processor.getImageUrl()
            if hd_pic == False:
                main_loop = False
                break
            # elif hd_pic == "False2":
            #     main_loop = False
            #     break

            print("\n", f"HD Profile Url : \n {hd_pic[0]}", end="\n\n")

            feeds = processor.getUserFeed(hd_pic[1])
            if feeds == False :
                main_loop = False
                break


            processfeeds = processor.processFeeds(feeds)

            inner_loop = True
            while inner_loop :
                choices = ["0", "1", "2", "3"]
                choose = input(
                    "Choose a number : \n \
                    1 - Get Urls in File \n \
                    2 - Download Images \n \
                    3 - Download Videos \n\
                    0 - Try Another Page \n \
                    Your Choise : "
                    )
                while choose not in choices:
                    choose = input(
                        "Choose a number : \n \
                        1 - Get Urls in File \n \
                        2 - Download Images \n \
                        3 - Download Videos \n\
                        0 - Try Another Page \n \
                        Your Choise : "
                        )
                
                if choose == "1" :
                    processor.pathToFile(processfeeds)
                    print("Urls Writed in File")

                if choose == "2":
                    if "images" in processfeeds :
                        processor.imageDownloader(processfeeds['images'])
                        print("All Images Downloaded")
                    else :
                        print("No Images in Feed")
                
                if choose == "3":
                    if "videos" in processfeeds:
                        processor.videoDownloader(processfeeds['videos'])
                        print("All Videos Downloaded")
                    else:
                        print("No Videos in Feed")

                if choose == "0":
                    inner_loop = False
                    break


if __name__ == "__main__" :
    main()
