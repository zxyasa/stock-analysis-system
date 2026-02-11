"""Structured application entry for stock1."""

from src.data.fetcher import main as build_report
from src.execution.notion import upload_report_to_notion
from src.execution.telegram import send_report_to_telegram
import config
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def run() -> None:
    report_md = build_report()
    try:
        upload_report_to_notion(report_md, title=config.REPORT_TITLE)
    except Exception as e:
        print(f"⚠️ Notion 推送失败，已跳过: {e}")

    try:
        send_report_to_telegram(report_md)
    except Exception as e:
        print(f"⚠️ Telegram 推送失败，已跳过: {e}")

    print("报告已生成，推送流程已执行（失败项已跳过）。")


if __name__ == "__main__":
    run()
