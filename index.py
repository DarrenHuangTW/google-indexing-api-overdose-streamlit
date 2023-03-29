import os
import base64
import json
import datetime
from dateutil import parser
import httplib2
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import streamlit as st

# 環境變量
JSON_KEY_FILE_BASE64 = os.environ["JSON_KEY_FILE_BASE64"]

# 將 Base64 字串解碼為字典
json_key_file_content = base64.b64decode(JSON_KEY_FILE_BASE64).decode("utf-8")
json_key_file = json.loads(json_key_file_content)

# 初始化 Google API 用戶端
SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"

credentials = service_account.Credentials.from_service_account_info(json_key_file, SCOPES)
http = credentials.authorize(httplib2.Http())

# 函數：提交 URLs 到 Google
def submit_urls(urls):
    response_messages = []
    for url in urls:
        url = url.strip()
        if not url:
            continue

        content = f"""{{
            "url": "{url}",
            "type": "URL_UPDATED"
        }}"""

        response, content = http.request(ENDPOINT, method="POST", body=content)
        content_json = json.loads(content.decode('utf-8'))

        # 解析回應內容，生成易懂的訊息
        if 'urlNotificationMetadata' in content_json:
            notify_time_str = content_json['urlNotificationMetadata']['latestUpdate']['notifyTime']
            notify_time = parser.isoparse(notify_time_str).replace(microsecond=0)
            formatted_notify_time = notify_time.strftime('%Y年%m月%d日 %H:%M')
            response_message = f"{url} | 提交成功，提交時間為 {formatted_notify_time}"
        else:
            response_message = f"{url}: 提交失敗"

        response_messages.append(response_message)

    return response_messages

# Streamlit 介面
st.title("Google 索引提交工具")

urls = st.text_area("請在下方輸入需要提交的網址，每行一個")
submit_button = st.button("提交")

if submit_button:
    if urls:
        url_list = urls.split("\n")
        responses = submit_urls(url_list)

        for response in responses:
            st.write(response)
    else:
        st.error("請輸入至少一個網址")
