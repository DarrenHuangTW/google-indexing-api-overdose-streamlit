import json
import streamlit as st
from oauth2client.service_account import ServiceAccountCredentials
import httplib2
import datetime
from dateutil import parser
import re

SCOPES = ["https://www.googleapis.com/auth/indexing"]
ENDPOINT = "https://indexing.googleapis.com/v3/urlNotifications:publish"
JSON_KEY_FILE = "service_account.json"

credentials = ServiceAccountCredentials.from_json_keyfile_name(JSON_KEY_FILE, scopes=SCOPES)
http = credentials.authorize(httplib2.Http())

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
            response_message = f"{url}: 提交成功，提交時間為 {formatted_notify_time}"
        else:
            response_message = f"{url}: 提交失敗"

        response_messages.append(response_message)

    return response_messages


st.title("Google URL 提交工具")
url_textarea = st.text_area("在此處輸入多行 URL（每行一個）")

if st.button("提交"):
    urls = url_textarea.split('\n')
    responses = submit_urls(urls)
    for response in responses:
        st.write(response)
