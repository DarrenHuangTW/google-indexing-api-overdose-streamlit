import os
import json
import base64
import datetime
from datetime import datetime, timedelta, timezone
import requests
from google.oauth2 import service_account
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build
import streamlit as st
import pytz

# 讀取 secrets
secrets = st.secrets["secrets"]

# 建立服務帳戶金鑰
service_account_info = {
    "type": secrets["type"],
    "project_id": secrets["project_id"],
    "private_key_id": secrets["private_key_id"],
    "private_key": secrets["private_key"],
    "client_email": secrets["client_email"],
    "client_id": secrets["client_id"],
    "auth_uri": secrets["auth_uri"],
    "token_uri": secrets["token_uri"],
    "auth_provider_x509_cert_url": secrets["auth_provider_x509_cert_url"],
    "client_x509_cert_url": secrets["client_x509_cert_url"],
}

credentials = service_account.Credentials.from_service_account_info(
    service_account_info, scopes=["https://www.googleapis.com/auth/indexing"]
)

# 建立 Google API 客戶端
google_client = build("indexing", "v3", credentials=credentials)

# Streamlit 應用介面
st.title("Google 索引提交")

urls_input = st.text_area("請輸入要提交的網址（每行一個）")
submit_button = st.button("提交")

if submit_button and urls_input:
    urls = urls_input.strip().split("\n")

    def submit_urls(urls):
        responses = []
        for url in urls:
            try:
                response = google_client.urlNotifications().publish(
                    body={"url": url, "type": "URL_UPDATED"}
                ).execute()
                responses.append((url, response))
            except HttpError as e:
                responses.append((url, e))
        return responses

    responses = submit_urls(urls)

    for url, response in responses:
        if isinstance(response, HttpError):
            st.error(f"{url} | 提交失敗，是不是客戶授權失敗啦！")
        else:
            notify_time_str = response.get("urlNotificationMetadata", {}).get("latestUpdate", {}).get("notifyTime", "")
            notify_time = datetime.strptime(notify_time_str.split('.')[0].rstrip('Z'), "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc)
            notify_time = notify_time.replace(microsecond=0)time.strftime('%Y年%m月%d日 %H:%M')}")
            
            # 將時間轉換為 UTC+8
            tz = pytz.timezone('Asia/Taipei')
            notify_time = notify_time.astimezone(tz)
            
            st.success(f"{url} | 提交成功，提交時間為 {notify_time.strftime('%Y年%m月%d日 %H:%M')}")
