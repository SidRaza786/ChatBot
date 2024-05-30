import requests, json
from collections.abc import Iterator
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os
import copy


text_splitter=RecursiveCharacterTextSplitter(chunk_size=200,chunk_overlap=40)

class DataProcessor:
    def __init__(self):
        pass

    def CreateChunkDict(self, item, chunk):
        chunk_dict_list = []
        for indx, chunk in enumerate(chunk):
            chunk_dict = item.copy()
            del chunk_dict["content"]
            chunk_dict["chunk"] = chunk
            chunk_dict["chunk_index"] = indx
            chunk_dict_list.append(chunk_dict)
        return chunk_dict_list


    def ExtractText(self, html: str) -> str:
        """
        Extract text from HTML content
        """
        soup = BeautifulSoup(html, features="html.parser")
        for script in soup(["script", "style"]):
            script.decompose()

        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = '\n'.join(chunk for chunk in chunks if chunk)
        return text


    def FetchWordPress_Content(self, base_url):
        contents = ["pages", "posts", "comments"]
        for content in contents:
            link = f"{base_url}/wp-json/wp/v2/{content}"
            response = requests.get(link, {"per_page": 100, "page": 1})
            if "X-WP-TotalPages" not in response.headers:
                # Handle the case where the header is missing
                total_pages = 1
            else:
                total_pages = int(response.headers["X-WP-TotalPages"])

            for i in range(1, total_pages+1):
                if i != 1:
                    response = requests.get(link, {"per_page":100, "page":i})
                response = response.json()

                for d in response:
                    if content == "comments":
                        # comment pages has no title
                        d["title"] = {"rendered": "Comment"}
                        
                    yield{
                        "id": str(d["id"]),
                        "date" : d["date_gmt"],
                        "title" : d["title"]["rendered"],
                        "link" : d["link"],
                        "content": d["content"]["rendered"],
                        }


    def get_data(self, base_url):
        site_contents: Iterator[dict[str, str]] = self.FetchWordPress_Content(base_url)

        data_list = []
        for item in site_contents:
            item["content"] = self.ExtractText(item["content"])
            # create lis of chunks
            chunk = text_splitter.split_text(item["content"])
            # create a chunk dict
            chunk_dict_list = self.CreateChunkDict(item, chunk)
            for chunk_dict in chunk_dict_list:
                data_list.append(chunk_dict)

        for item in data_list:
            # save chunk and title
            chunk = item["chunk"]
            title = item["title"]
            del item["chunk"]
            del item["title"]
            # create chunk with title and content
            item["chunk"] = f"Title = {title}\n{chunk}"
        return data_list




    






