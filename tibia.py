from typing import Union, List
from pydantic import BaseModel

from bs4 import BeautifulSoup, ResultSet, Tag, NavigableString
import requests
import re
import json

import sys
import os
import time

class Pages(BaseModel):
    news: str = "https://www.tibia.com/news/"
    worlds: str = "https://www.tibia.com/community/?subtopic=worlds"
    highscores: str = "https://www.tibia.com/community/?subtopic=highscores"
    characters: str = "https://www.tibia.com/community/?name="
    
class Character(BaseModel):
    name: str
    title: str = ""
    sex: str = ""
    vocation: str = ""
    level: int = 0
    achievement_points: int = 0
    world: str = ""
    residence: str = ""
    married_to: str = ""
    house: str = ""
    guild_membership: str = ""
    lastlogin: str = ""
    comment: str = ""
    account_status: str = ""
    
class Notice(BaseModel):
    title: str
    timestamp: str
    content: str
    image: str
    figures: List[str] = []
    
class World(BaseModel):
    name: str
    online: str
    location: str
    pvp_type: str
    info: str

class Tibia:
    def __init__(self):
        self.pages : Pages = Pages()
        
    def extractNewsPage(self) -> Union[Tag, NavigableString, None]:
        response = requests.get(self.pages.news)
        soup = BeautifulSoup(response.text, "html.parser")
        news = soup.find("div", {"id": "News"}).find("div", {"class": "BoxContent"})
        return news
        
    def extractNoticeData(self, headline_tag, table_tag=None) -> Notice:
        title = headline_tag.find("p").text
        timestamp = headline_tag.find("div", {"class": "NewsHeadlineDate"}).text.replace(" - ", "")
        new_notice = Notice(title=title, timestamp=timestamp, content="", image="", figures=[])

        if table_tag:
            table_container = table_tag.find("td", {"class": "NewsTableContainer"})
            result = ""
            for row in table_container:
                if row.name == "p":
                    result += row.text + "\n"
                    if row.img:
                        for img in row.find_all("img"):
                            if '/letters/' not in img["src"]:
                                new_notice.image = img["src"]
                            else:
                                letter = img["src"].split("/")[-1].split("_")[-1].split(".")[0]
                                result = letter + result
                elif row.name == "ul":
                    for li in row:
                        if li.name == "li":
                            result += li.text + "\n"
                elif row.name == "figure":
                    for center in row:
                        if center.name == "center":
                            for img in center:
                                if img.name == "img":
                                    new_notice.figures.append(img["src"])

            new_notice.content = result

        return new_notice

    def getNews(self) -> List[Notice]:
        try:
            news = self.extractNewsPage()
            news_headlines = news.find_all("div", {"class": "NewsHeadline"})
            news_tables = news.find_all("table", {"class": "NewsTable"})
            data = []

            for headline, table in zip(news_headlines, news_tables):
                new_notice = self.extractNoticeData(headline, table)
                data.append(new_notice)

            return data
        except Exception as e:
            print(e)
            return [Notice(title="Error", timestamp=str(time.time()), content="Error", image="", figures=[])]

    def getLastNew(self) -> Notice:
        try:
            news = self.extractNewsPage()
            latest_headline = news.find("div", {"class": "NewsHeadline"})
            latest_table = news.find("table", {"class": "NewsTable"})
            if latest_headline and latest_table:
                return self.extractNoticeData(latest_headline, latest_table)
            else:
                return Notice(title="Error", timestamp=str(time.time()), content="No news found", image="", figures=[])
        except Exception as e:
            print(f"An error occurred: {e}")
            return Notice(title="Error", timestamp=str(time.time()), content="Error", image="", figures=[])
        
    def extractWorldsPage(self) -> Union[Tag, NavigableString, None]:
        response = requests.get(self.pages.worlds)
        soup = BeautifulSoup(response.text, "html.parser")
        worlds = soup.find("div", {"class": "InnerTableContainer"})
        return worlds
    
    def getWorlds(self) -> List[World]:
        #* 0-World 1-Online 2-Location 3-PvP 4-BattleEye 5-AdditionalInfo
        worlds = self.extractWorldsPage()
        tables = worlds.find_all("table", {"class": "TableContent"})[2]
        trs = tables.find_all("tr")
        data = []
        for tr in trs:
            if tr.find(name="td"):
                tempdata = tr.find_all("td")
                world = World(name=tempdata[0].text, online=tempdata[1].text, location=tempdata[2].text, pvp_type=tempdata[3].text, info=tempdata[5].text)
                data.append(world)
                
        data.pop(0)
                
        return data
    
    def getCharacter(self, character) -> Union[Character,None]:
        url = self.pages.characters + character
        soup = BeautifulSoup(requests.get(url).text, "html.parser")
        mainboxcontent = soup.find("div", {"class": "BoxContent"})
        table = mainboxcontent.find("table", {"class": "TableContent"})
        char = Character(name=character)
        for tr in table.find_all("tr"):
            label = tr.find("td", {"class": "LabelV175"})
            if label:
                attrName = label.text.strip().lower().replace(":","").replace(" ","_")
                value = tr.findNext("td")
                if value:
                    setattr(char, attrName, value.text.strip())
                    
        return char
    
if __name__ == "__main__":
    tibia = Tibia()
    news = tibia.getCharacter("Divepu Paladino Supremo")
    print(news)