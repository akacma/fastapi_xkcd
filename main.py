from typing import List, Set
from functools import lru_cache
from fastapi import Depends, FastAPI, Query, HTTPException, Request
import config
from models import Comic, HTTPStatusCodeError
import requests
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import uvicorn

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@lru_cache
def get_settings():
    """
    Returns and cashes settings
    """
    return config.Settings()


@lru_cache
def get_comic_data_by_id(comic_id: int, host_address: str, info: str):
    """
    Returns and caches the data of a comic by its ID
    """
    return Comic().get_comic_by_id(comic_id, host_address, info)


@app.get("/comics/current")
@limiter.limit(get_settings().rate_limit)
async def fetch_current_comic_data(request: Request, settings: config.Settings = Depends(get_settings)):
    """
    Returns the data of a current comic
    """
    return Comic().get_current_comic(settings.host_address, settings.info)


@app.get("/comics/many", response_model=List[Comic])
@limiter.limit(get_settings().rate_limit)
async def fetch_many_comics(request: Request, comic_ids: List[int] = Query(...), settings: config.Settings = Depends(get_settings)):
    """
    Returns the data of multiple comics by their IDs 
    """
    comic_ids = sorted(list(set(comic_ids)))
    return [get_comic_data_by_id(comic_id, settings.host_address, settings.info) for comic_id in comic_ids]


@app.get("/comics/download", response_model=Set[Comic])
@limiter.limit(get_settings().rate_limit)
async def get_images(request: Request, comic_ids: Set[int] = Query(...), settings: config.Settings = Depends(get_settings)):
    """
    Downloads comic images by their IDs
    """
    downloaded_ids = Comic.get_downloaded_images_ids(settings.images)
    ids_to_download = comic_ids - downloaded_ids
    for comic_id in ids_to_download:
        comic = get_comic_data_by_id(
            comic_id, settings.host_address, settings.info)
        comic.download_image_by_id(comic_id, comic.url, settings.images)


@app.get("/comics/{comic_id}", response_model=Comic)
@limiter.limit(get_settings().rate_limit)
async def fetch_comic_data_by_id(request: Request, comic_id: int, settings: config.Settings = Depends(get_settings)):
    """
    Returns the data of a comic by its ID with settings
    """
    comic = get_comic_data_by_id(
        comic_id, settings.host_address, settings.info)
    return comic
