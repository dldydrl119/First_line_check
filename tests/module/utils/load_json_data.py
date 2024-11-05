# load_json_data.py
import json

def load_json_data(current_json):
    try:
        with open(current_json, 'r', encoding='utf-8') as file:
            json_data = json.load(file)
        return json_data  # json_data가 리스트인지 확인
    except FileNotFoundError as e:
        print(f"JSON 파일을 찾을 수 없습니다: {e}")
        raise
