import sys
from playwright.sync_api import sync_playwright
src, out = sys.argv[1], sys.argv[2]
foot = ('<div style="font-family:\'Noto Sans CJK JP\',sans-serif;font-size:7px;width:100%;text-align:center;color:#a00;padding:0 14mm">'
        'ArduPilot 公式のものではない、非公式の日本語訳 ｜ ArduCopter 4.7.2 パラメータ日本語解説 ｜ GPL-3.0 ｜ '
        '<span class="pageNumber"></span> / <span class="totalPages"></span></div>')
with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page()
    pg.goto("file://" + src, wait_until="load", timeout=600000)
    pg.emulate_media(media="print")
    pg.pdf(path=out, format="A4", print_background=True, display_header_footer=True,
           header_template="<div></div>", footer_template=foot,
           margin={"top": "14mm", "bottom": "16mm", "left": "14mm", "right": "14mm"})
    b.close()
