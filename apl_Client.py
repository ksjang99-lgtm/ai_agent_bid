import os
import requests
from urllib.parse import urlparse
from urllib.parse import unquote
import re
import subprocess
from extract_text import get_text



def download_file(filename, contents):
    # 다운로드 폴더 지정
    download_folder = "download"
    os.makedirs(download_folder, exist_ok=True)  # 폴더가 없으면 생성
    # 다운로드 폴더 경로와 결합
    file_path = os.path.join(download_folder, filename)
    # 파일 저장
    with open(file_path, "wb") as f:
        f.write(contents)
    return file_path

def get_filename_from_header(file_url):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        file_url,
        headers=headers,
        stream=True,
        timeout=30
    )
    response.raise_for_status()

    cd = response.headers.get("Content-Disposition")
    filename = None

    if cd:
        # 1️⃣ filename*=UTF-8''xxx
        match = re.search(r"filename\*=UTF-8''(.+)", cd, re.IGNORECASE)
        if match:
            filename = unquote(match.group(1))

        # 2️⃣ filename="xxx"
        if not filename:
            match = re.search(r'filename="(.+)"', cd, re.IGNORECASE)
            if match:
                filename = match.group(1)

        # 3️⃣ filename=URLENCODED_STRING  ← ⭐ 지금 케이스
        if not filename:
            match = re.search(r"filename=([^;]+)", cd, re.IGNORECASE)
            if match:
                filename = unquote(match.group(1))

    if not filename:
        filename = "unknown.hwp"

    return {
        "filename": filename,
        "contents": response.content
    }


def get_bid_pblanc_list_info_cnstwk(bidNtceNo):
    url = "https://apis.data.go.kr/1230000/ad/BidPublicInfoService/getBidPblancListInfoCnstwk"
    params = {
        "serviceKey": "f4ed16dbd7abd47ff69d9bf8061f79c40d43e67933f2dee2227bb2de8caeda0a",
        "pageNo": 1,
        "numOfRows": 1,
        "inqryDiv": 2,
        "inqryBgnDt": "",
        "inqryEndDt": "",
        "bidNtceNo": bidNtceNo,
        "type": "json"
    }


    headers = {
        "accept": "*/*"
    }

    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP 에러 발생 시 예외

        data = response.json()
        items = data.get("response", {}).get("body", {}).get("items", {})
        # print("API 결과:", items)
        ret = []
        for item in items:
            for i in range(1, 11):
                key = f"ntceSpecDocUrl{i}"
                file_url = item.get(key)
                # count = len(file_url)
                if file_url :
                    try:
                        # print(f"[다운로드]: {file_url}")
                        parsed_url = urlparse(file_url)
                        result = get_filename_from_header(file_url)
                        file_name = result["filename"]
                        contents = result["contents"]
                       
                        if file_name:
                            # 파일 저장
                            file_path = download_file(file_name, contents=contents)
                            text = get_text(file_path)
                            if text:
                                cnt = len(text)
                                ret.append({"filename": file_name,  "text": text, "filePath": file_path}) 
                            else:
                                # print(f"[다운로드]: {file_name}")
                                ret.append({"filename": file_name,  "text": "", "filePath": file_path})                    
                    except Exception as e:
                        print(f"[다운로드 실패] {file_url}: {e}")
        return ret
    except requests.exceptions.RequestException as e:
        print("API 요청 오류:", e)
        return None

# JSON 파싱
# data = get_bid_pblanc_list_info_cnstwk("R26BK01276773")
# print(data)