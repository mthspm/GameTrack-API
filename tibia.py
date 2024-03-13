from typing import Union, List
from pydantic import BaseModel

from bs4 import BeautifulSoup, ResultSet
import requests
import re
import json

import os
import time

class Pages(BaseModel):
    news: str = "https://www.tibia.com/news/"
    worlds: str = "https://www.tibia.com/community/?subtopic=worlds"
    highscores: str = "https://www.tibia.com/community/?subtopic=highscores"
    characters: str = "https://www.tibia.com/community/?subtopic=characters"
    
class Notice(BaseModel):
    title: str
    timestamp: str
    content: str
    image: str
    figures: List[str] = []

class Tibia:
    def __init__(self):
        self.pages : Pages = Pages()
        
    def exctract_news_page(self) -> ResultSet:
        response = requests.get(self.pages.news)
        soup = BeautifulSoup(response.text, "html.parser")
        news = soup.find("div", {"id": "News"}).find("div", {"class": "BoxContent"})
        return news
        
    def extract_notice_data(self, headline_tag, table_tag=None) -> Notice:
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
            news = self.exctract_news_page()
            news_headlines = news.find_all("div", {"class": "NewsHeadline"})
            news_tables = news.find_all("table", {"class": "NewsTable"})
            data = []

            for headline, table in zip(news_headlines, news_tables):
                new_notice = self.extract_notice_data(headline, table)
                data.append(new_notice)

            return data
        except Exception as e:
            print(e)
            return [Notice(title="Error", timestamp=str(time.time()), content="Error", image="", figures=[])]

    def getLastNew(self) -> Notice:
        try:
            news = self.exctract_news_page()
            latest_headline = news.find("div", {"class": "NewsHeadline"})
            latest_table = news.find("table", {"class": "NewsTable"})
            if latest_headline and latest_table:
                return self.extract_notice_data(latest_headline, latest_table)
            else:
                return Notice(title="Error", timestamp=str(time.time()), content="No news found", image="", figures=[])
        except Exception as e:
            print(f"An error occurred: {e}")
            return Notice(title="Error", timestamp=str(time.time()), content="Error", image="", figures=[])
    
if __name__ == "__main__":
    tibia = Tibia()
    news = tibia.getLastNew()
    print(news)