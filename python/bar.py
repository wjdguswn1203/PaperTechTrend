from streamlit_echarts import JsCode
from streamlit_echarts import st_echarts
import requests
import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), '../.env'))

FASTAPI_URL1 = os.getenv('FASTAPI_URL1')
FASTAPI_URL2 = os.getenv('FASTAPI_URL2')
FASTAPI_URL3 = os.getenv('FASTAPI_URL3')

def single_bar_all(time1_percent, time2_percent, time3_percent, count_percent1, count_percent2, count_percent3):
    
    options = {
        "grid": {
        "left": "10%",  # 왼쪽 여백
        "right": "10%",  # 오른쪽 여백
        "width": "80%",  # 그리드의 너비
        },
        "xAxis": {
            "type": "category",
            "data": ["bart", "t5", "t5+의미론적추론"],
        },
        "yAxis": {
            "name": "%",
            "type": "value",
            "min": 0,  
            "max": 100, 
            "interval":20,  # y축 간격 설정
        },
        "series": [
            {
                "data": [time1_percent, time2_percent, time3_percent],
                "type": "bar",
                "barWidth": '30%',  # 막대 너비 설정
                "itemStyle": {
                    "color": "#F0BD75"  # 막대 색상 설정
                }
            },
            {
                "data": [count_percent1, count_percent2, count_percent3],
                "type": "bar",
                "barWidth": '30%',  # 막대 너비 설정
                "itemStyle": {
                    "color": "#EFE4B0"  # 막대 색상 설정
                }
            },
               
        ],
    }
    st_echarts(options, height="400px")
    

    
def single_bar_time(time1, time2, time3):
    data = [time1, time2, time3]
    options = {
        "xAxis": {
            "type": "category",
            "data": ["bart", "t5", "t5+의미론적추론"],
        },
        "yAxis": {
            "name": "%",
            "type": "value",
            "min" : 0,
            "max" : 100,
            "interval":20,  # y축 간격 설정
        },
        "series": [
            {
                "data": data,
                "type": "bar",
                "barWidth": '30%',  # 막대 너비 설정
                "itemStyle": {
                    "color": "#F0BD75"  # 막대 색상 설정
                }
            },
            
        ],
    }
    st_echarts(options, height="400px")


def single_bar_accuracy(bert_count1, bert_count2, bert_count3, rank_count1, rank_count2, rank_count3):

    options = {
        "legend": {
        "data": ["keybert", "textrank"],
        "top": "top",  # 범례를 상단에 배치
        "right": "right",  # 범례를 오른쪽에 배치
        },
        "xAxis": {
            "type": "category",
            "data": ["bart", "t5", "t5+의미론적추론"],
           
        }, 
        "yAxis": {
            "name": "%",
            "type": "value",
        },
        "series": [
            {
                "name": "keybert",
                "data": [bert_count1, bert_count2, bert_count3], # 실제 데이터로 변경해야함
                "type": "bar",
                "barWidth": '25%',  # 막대 너비 설정
                "itemStyle": {
                    "color": "#5470C6"  # 막대 색상 설정
                }
            }, 
            {
                "name": "textrank",
                "data": [rank_count1, rank_count2, rank_count3],
                "type": "bar",
                "barWidth": '25%',  # 막대 너비 설정
                "itemStyle": {
                    "color": "#91CC75"  # 막대 색상 설정
                }
            }
        ],
    }
    st_echarts(options, height="400px")

    
    #5470C6
    #91CC75