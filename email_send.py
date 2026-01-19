import os
import base64
from email.mime.text import MIMEText

from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

# ==============================
# 설정
# ==============================
SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
CREDENTIALS_FILE = "client_secret.json"
TOKEN_FILE = "token.json"


# ==============================
# OAuth 인증 처리
# ==============================
def get_gmail_credentials():
    """
    1. token.json 존재 시 재사용
    2. 없거나 만료 시 OAuth 브라우저 로그인
    """
    creds = None

    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(
            TOKEN_FILE, SCOPES
        )

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            CREDENTIALS_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open(TOKEN_FILE, "w", encoding="utf-8") as token:
            token.write(creds.to_json())

    return creds


# ==============================
# Gmail API 메일 발송
# ==============================
def send_email_gmail_api(
    creds,
    sender_email,
    receiver_email,
    subject,
    body_text
):
    service = build("gmail", "v1", credentials=creds)

    message = MIMEText(body_text, "plain", "utf-8")
    message["to"] = receiver_email
    message["from"] = sender_email
    message["subject"] = subject

    raw_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode("utf-8")

    result = service.users().messages().send(
        userId="me",
        body={"raw": raw_message}
    ).execute()

    return result


# ==============================
# 실행 진입점
# ==============================
if __name__ == "__main__":
    # 발신 / 수신 정보
    SENDER_EMAIL = "aiagentsender@gmail.com"
    RECEIVER_EMAIL = "enidThe@outlook.com"

    SUBJECT = "Gmail API OAuth 발송 테스트"
    BODY = """안녕하세요.

이 메일은 Gmail API + OAuth 2.0 방식으로
Python에서 발송되었습니다.

감사합니다.
"""

    creds = get_gmail_credentials()

    result = send_email_gmail_api(
        creds=creds,
        sender_email=SENDER_EMAIL,
        receiver_email=RECEIVER_EMAIL,
        subject=SUBJECT,
        body_text=BODY
    )

    print("메일 발송 완료")
    print(f"Message ID: {result.get('id')}")
