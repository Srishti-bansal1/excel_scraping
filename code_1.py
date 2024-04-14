from dataclasses import dataclass, asdict
import pandas as pd
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

@dataclass
class Detail:
    urls : str
    text : str
    links : list
    images : list

@dataclass
class DetailList:
    detail_list = []
    save_at = 'output'

    def dataframe(self):
        return pd.json_normalize((asdict(detail) for detail in self.detail_list), sep="_")

    def save_to_csv(self, filename):
        if not os.path.exists(self.save_at):
            os.makedirs(self.save_at)
        self.dataframe().to_csv(f"{self.save_at}/{filename}.csv", index=False)

def fetch_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise exception for bad response
        return response
    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch URL: {url}")
        print(f"Error: {e}")
        return None

def main():
    csv_file = open("urls.csv","r")
    r = csv_file.read()
    urls = r.split("\n")

    detail_list = DetailList()

    for url in urls:
        # Fetch HTML content of the URL
        response = fetch_url(url)
        if response is not None:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract text
            text = soup.get_text()
            text_replace = text.replace('\n'," ")
            text_strip = text_replace.strip()
            texts = " ".join(text_strip.split())        

            # Extract links
            _links = [urljoin(url, link.get('href')) for link in soup.find_all('a')]
            print(_links)
            _links_strip = str(_links).strip()
            links =  " ".join(str(_links_strip).split())

            # Extract images
            _images = [urljoin(url,img.get("src") or img.get("data-src") or img.get("data-lsrc")) for img in soup.select("img")]
            print(soup.select("img"))
            _images_strip = str(_images).strip()
            images = " ".join(str(_images_strip).split())

            # Create Detail object
            detail = Detail(urls= url,text=texts, links=links, images=images)
            detail_list.detail_list.append(detail)

    # Save details to CSV file
    detail_list.save_to_csv("data")

if __name__ == "__main__":
    main()
