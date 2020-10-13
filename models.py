from pydantic import BaseModel
import requests
import json
from datetime import datetime
from fastapi import HTTPException
from pathlib import Path


class MyException(Exception):
    pass


class HTTPStatusCodeError(MyException):
    def __init__(self, code, message):
        self.code = code
        self.message = message


class Comic(BaseModel):
    id: str = ""
    description: str = ""
    date: str = ""
    title: str = ""
    url: str = ""

    def set_comic_data(self, url_address: str):
        """
        Sets the attributes, retrieved from a GET request sent to a given url, to the Comic object 
        """
        response = requests.get(url_address)
        if response.status_code == 200:
            data = response.json()

            self.id = data['num']
            self.description = data['alt']
            self.date = f"{datetime(int(data['year']), int(data['month']), int(data['day'])):%y-%m-%d}"
            self.title = data['title'].lower()
            self.url = data['img']
        else:
            raise HTTPStatusCodeError(response.status_code, "Item not found")

    def get_comic_by_id(self, comic_id: int, host_address: str, info: str):
        """
        Returns the Comic object with a given ID, after having sent a GET request to the host address
        """
        try:
            self.set_comic_data(f"{host_address}{comic_id}/{info}")
        except HTTPStatusCodeError as err:
            raise HTTPException(status_code=err.code,
                                detail=f"For comic id={comic_id}: {err.message}")
        except:
            print("Unexpected error")
        else:
            return self

    def get_current_comic(self, host_address: str, info: str):
        """
        Returns the current Comic object, after having sent a GET request to the host address
        """
        try:
            self.set_comic_data(f"{host_address}{info}")
        except HTTPStatusCodeError as err:
            raise HTTPException(status_code=err.code, detail=err.message)
        except:
            print("Unexpected error")
        else:
            return self

    def download_image_to_directory(self, url: str, path: Path):
        """
        Downloads the comic image, retrieved from a GET request sent to a given url, to a given path
        """
        response = requests.get(url)
        with open(path, "wb") as file:
            file.write(response.content)

    def download_image_by_id(self, comic_id: int, comic_url: str, download_directory: str):
        """
        Downloads the comic image by its ID to the indicated directory, under the name derived from that ID
        """
        downloaded_ids = Comic.get_downloaded_images_ids(download_directory)
        self.download_image_to_directory(
            comic_url, (Path() / download_directory / f"{comic_id}.{comic_url.split('.')[-1]}"))

    @staticmethod
    def get_downloaded_images_ids(download_directory: str):
        """
        Returns a set of downloaded images' IDs
        """
        path = Path() / download_directory
        ids = {int(p.stem) for p in path.iterdir()}
        return ids
