from urllib.parse import urlencode
import pandas as pd
from urllib.parse import urlparse, parse_qs

import json
import redis
from redis import from_url


def build_url(query):
    name = f"{query.get('first_name')} {query.get('last_name')}".strip()
    city_state = f"{query.get('city')}, {query.get('state')}"
    zipcode = query.get("zipcode")
    params = {"name":name, "citystatezip": city_state or zipcode}
    url = f"https://www.truepeoplesearch.com/results?{urlencode(params)}"
    return url


urls = []
df = pd.read_excel("input.xlsx")
df_filtered = df.drop_duplicates(subset=['First_name', 'Last_name', 'City', 'State'])
for idx, row in df_filtered.iterrows():
    query = {
        "first_name": row['First_name'],
        "last_name": row['Last_name'],
        "city": row['City'],
        "state": row['State'],
        "zipcode": ''
    }
    url = build_url(query)
    urls.append(url)
    if idx == 500:
        break

DB_SERVER = '159.65.146.183'
redisClient = redis.from_url(f'redis://{DB_SERVER}')
pipe = redisClient.pipeline()  # Create a pipeline

for url in urls:
    jsn = json.dumps({"url": url})
    pipe.lpush("people:start_urls", jsn)  # Add commands to the pipeline

pipe.execute() 

