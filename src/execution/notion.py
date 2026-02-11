# notion_uploader.py
from notion_client import Client
import config


def upload_report_to_notion(report_md: str, title: str = None):
    if not config.NOTION_TOKEN or not config.NOTION_PAGE_ID:
        raise ValueError("Missing NOTION_TOKEN or NOTION_PAGE_ID in environment variables.")
    notion = Client(auth=config.NOTION_TOKEN)
    title = title or config.REPORT_TITLE
    # 多段大文本切分
    blocks = []
    for i in range(0, len(report_md), 1800):
        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {"type": "text", "text": {"content": report_md[i:i+1800]}}
                ]
            }
        })
    notion.pages.create(
        parent={"page_id": config.NOTION_PAGE_ID},
        properties={
            "title": [
                {"type": "text", "text": {"content": title}}
            ]
        },
        children=blocks
    )
