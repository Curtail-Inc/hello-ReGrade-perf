"""Optional: record the ReGrade web-UI delta view as a supplementary clip.
Usage: python capture/record_ui.py <replay_url> <out.webm>
Requires: pip install playwright && playwright install chromium
"""
import sys
from playwright.sync_api import sync_playwright


def record(url: str, out_webm: str) -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch()
        ctx = browser.new_context(viewport={"width": 1920, "height": 1080},
                                  record_video_dir="capture/", record_video_size={"width": 1920, "height": 1080})
        page = ctx.new_page()
        page.goto(url, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(4000)          # let the delta view settle / animate
        ctx.close()                           # closing the CONTEXT flushes the .webm
        import os
        os.replace(page.video.path(), out_webm)
        browser.close()
        print(f"wrote {out_webm}")


if __name__ == "__main__":
    record(sys.argv[1], sys.argv[2])
