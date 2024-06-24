import requests
import os
import re
from bs4 import BeautifulSoup
from fastapi import FastAPI, Request
from sqlalchemy import create_engine, exists
from sqlalchemy.orm import sessionmaker
from models import Collection
from dotenv import load_dotenv
# import weaviate

# streamlit app.py
from typing import List
from pydantic import BaseModel
import warnings
import numpy as np
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from concurrent.futures import ThreadPoolExecutor
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

# 경고 메시지 무시
warnings.filterwarnings("ignore", category=FutureWarning, module='huggingface_hub')

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

FASTAPI_URL1 = os.getenv('FASTAPI_URL1')
FASTAPI_URL2 = os.getenv('FASTAPI_URL2')

# Database connection settings
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')

DB_URL = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

app = FastAPI()

# 2. Hugging Face 요약 모델 설정
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

# cuda == gpu
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model.to(device)

@app.get('/')
async def health_check():
    return "OK"

@app.post('/summarize')
async def summarize(request: Request):
    body = await request.json()
    title = body.get("title", "")
    split_texts = body.get("texts", [])

    summaries = []
    
    # summary 존재 여부 확인
    get_summary = requests.get(f"{FASTAPI_URL1}/getSummary1?title={title}")
    res = get_summary.json().get("resultCode", "")
    if res == 200:
        res = get_summary.json().get("data", "")
        summaries = res.split("\n")
    else:
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(summarize_paragraph, paragraph) for paragraph in split_texts]
            for future in futures:
                summaries.append(future.result())
    if summaries:
        url = f"{FASTAPI_URL1}/saveSummary1"
        summaries_string = "\n".join(summaries)
        save_sum = requests.post(url, json={"title": title,"text": summaries_string})
        print(save_sum)
        return {"resultCode" : 200, "data" : summaries}
    else:
        return {"resultCode" : 404, "data" : summaries}
    
def summarize_paragraph(paragraph):
    try:
        inputs = tokenizer(paragraph, return_tensors="pt", max_length=1024, truncation=True).to(device)
        summary_ids = model.generate(inputs["input_ids"], max_length=512, min_length=30, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        print(f"Summary is okey\n")
        return summary
    except Exception as e:
        print(f"Error summarizing paragraph: {e}")
        return paragraph

# 구어체 기반 weaviate 검색 
# searchword = 'Why Deepfake Videos Are Really Visible'
# @app.get('/getColl')
# async def getColl(searchword: str):
#     result = []
#     # print(searchword)
#     result = []
#     questions  = client.collections.get("Paper")
#     response = questions.query.near_text(
#         query=searchword,
#         limit=10
#     )
#     res = []
#     # 오브젝트가 있으면
#     if response.objects:
#         for object in response.objects:
#             res.append(object.properties) # 반환 데이터에 추가
#         return {"resultCode" : 200, "data" : res}
#     else:
#         return {"resultCode" : 404, "data" : response}


@app.get('/dbpiasearch')
async def get_trend_keywords():
    # 요청할 URL
    url = 'https://www.dbpia.co.kr/curation/best-node/top/20?bestCode=ND'

    # requests를 사용하여 JSON 데이터 가져오기
    response = requests.get(url)
    response.raise_for_status()  # 오류 체크

    # JSON 데이터 파싱
    data = response.json()

    # node_id 값을 추출하고 전체 URL 생성
    base_url = 'https://www.dbpia.co.kr/journal/articleDetail?nodeId='
    urls = [base_url + item['node_id'] for item in data]
    
    # 각 URL에서 해시태그 추출
    all_keywords = []
    for url in urls:
        keywords = extract_keywords(url)
        filtered_keywords = filter_keywords(keywords)
        all_keywords.extend(filtered_keywords)
        # print(f"Extracted keywords from {url}: {filtered_keywords}")

    if all_keywords:
            return {"resultCode" : 200, "keywords" : all_keywords}
    else:
        return {"resultCode" : 404, "keywords" : all_keywords}

def extract_keywords(url):
    try:
        response = requests.get(url)
        response.raise_for_status()  # 오류 체크
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 클래스 이름이 'keywordWrap__keyword'인 요소 찾기
        keywords = [tag.text.strip() for tag in soup.find_all(class_='keywordWrap__keyword')]
        # 불필요한 첫 글자(#) 제거
        keywords = [keyword[1:] if keyword.startswith("#") else keyword for keyword in keywords]
        return keywords
    except Exception as e:
        print(f"Error extracting keywords from {url}: {e}")
        return []

def filter_keywords(keywords):
    filtered_keywords = []
    for keyword in keywords:
        # 한글이 포함된 키워드 제거
        if re.search('[가-힣]', keyword):
            continue
        # 괄호 안에 한글 설명이 포함된 키워드 제거
        if re.search(r'\([가-힣]+\)', keyword):
            continue
        filtered_keywords.append(keyword)
    return filtered_keywords

def keyword_exists(db_session, keyword):
    return db_session.query(exists().where(Collection.searchword == keyword)).scalar()

# @app.get('/searchPopularkeyord')
# async def search_popular_keyword():
#     # dbpia API에서 인기있는 검색어 가져오기
#     response = await get_trend_keywords()
#     keywords = response.get("keywords", [])
#     db = SessionLocal()
    
#     # 새 키워드만 가져오기
#     new_keywords = [keyword for keyword in keywords if not keyword_exists(db, keyword)]
#     results = []
#     for keyword in new_keywords:
#         try:
#             keyword_response = requests.get(f'{FASTAPI_URL1}/getMeta?searchword={keyword}')
#             keyword_data = keyword_response.json()
#             results.append({'keyword': keyword, 'length': len(keyword_data)})
#         except Exception as e:
#             print(f'Error fetching data for keyword: {keyword}', e)
#             results.append({'keyword': keyword, 'length': 0})

#     db.close()
    
#     if results:
#         return {"resultCode" : 200, "data" : results}
#     else:
#         return {"resultCode" : 404, "data" : results}


