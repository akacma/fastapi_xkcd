# Comics API

An application built with FastAPI which returns data about comics made available by XKCD API  

## Features  

- GET endpoints:  
  - `GET /comics/current`  
  - `GET /comics/<comic_id>`  
  - `GET /comics/many?comic_ids=<comic_1>&comic_ids=<comic_id_2>&...&comic_ids=<comic_id_n>`  
  - `GET /comics/download?comic_ids=<comic_1>&comic_ids=<comic_id_2>&...&comic_ids=<comic_id_n>`  
- cache for fetched data  using `lru_cache`
- rate limiter for requests using SlowApi library

## Installation  

Copy the repository and to install the necessary modules type:  

    pip install -r requirements.txt  

## Configuration  

Edit `.env file`

## Start  

To start server type:  

    uvicorn app:main --reload  

## Testing  

To test type:  

    python -m testpy  
        
## Issues  

- The rate limiter for requests made from `/comics{id}` endpoint works only if they are repeated requests for the same ID. If requests concern different IDs, the limit is ignored.  
- The rate limiter configuration in the `test_main.py` file does not work. 
