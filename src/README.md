# 再生成の手順（ArduCopter 4.7.2 パラメータ日本語解説）

- `data.json` … 公式メタデータ＋既定値（prep.py で生成）
- `tr_desc.json` / `tr_label.json` … 説明文・選択肢の訳（テンプレート ID → 訳文。{0} は数値、{Pa} はパラメータ名の差し込み位置）
- `notes.json` … 研究注記（パラメータ名 → 本文。空欄は表示されない）
- `review.json` … 確認状況（パラメータ名 → "確認済み"）。ここに追記すると表紙の件数とバッジが変わる
- `meta.json` … 表紙・出典・ライセンス・変更履歴

```
python3 build_html.py out.html                     # 画面用 HTML
python3 make_pdf.py $PWD/out.html pass1.pdf        # 1 回目の PDF
python3 pages.py pass1.pdf pages.json              # ページ番号を取得
python3 build_html.py print.html --pages pages.json
python3 make_pdf.py $PWD/print.html final.pdf      # 索引にページ番号入りの PDF
```
（Playwright + Chromium、pypdf が必要）

## ライセンス
本キットと資料は GPL-3.0（LICENSE を参照）。原文は ArduPilot ソースコード（Copter-4.7.2）のパラメータ定義コメント（GPL-3.0）。
