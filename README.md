# ArduCopter 全パラメータ 日本語解説（非公式）

> **ArduPilot 公式のものではない、非公式の日本語訳です。** ArduPilot プロジェクトが作成・承認したものではありません。

オープンソースの飛行制御ソフトウェア [ArduPilot](https://ardupilot.org/) のマルチコプター用ファームウェア **ArduCopter 4.7.2** の全パラメータ（5,687 項目）について、説明文と選択肢の意味を日本語に訳した資料です。

| ファイル | 内容 |
|---|---|
| [`ArduCopter_4.7.2_parameters_ja.pdf`](ArduCopter_4.7.2_parameters_ja.pdf) | 印刷用（A4・614 ページ）。目次・索引にページ番号とリンク付き |
| [`ArduCopter_4.7.2_parameters_ja.html`](ArduCopter_4.7.2_parameters_ja.html) | 単一 HTML。ページ内の絞り込み検索付き（外部通信なし） |
| [`src/`](src/) | ソース一式（訳文データ・パラメータデータ・生成スクリプト）。再生成手順は [src/README.md](src/README.md) |
| [`LICENSE`](LICENSE) | GNU General Public License version 3 |

## 収録内容

- 各パラメータの日本語訳と原文、単位、範囲、増分、既定値、再起動の要否、選択肢（Values）、ビットマスク（Bitmask）
- パラメータ名・単位・数値は原文のまま。機種名など固有名詞の選択肢も原文のまま
- 既定値：ArduCopter 4.7.2 の SITL（クアッド機）で初期化直後に読み出した値（S）と、ソースコード記載の値（C）

## 作成方法と確認状況

1. GitHub [ArduPilot/ardupilot](https://github.com/ArduPilot/ardupilot) のタグ `Copter-4.7.2`（コミット `fb77356`）から、公式 Complete Parameter List と同じツール（`Tools/autotest/param_metadata/param_parse.py`）でパラメータ定義を取得
2. 説明文と選択肢名を AI（Anthropic「Claude」、Claude Code 環境）で日本語に下訳。訳文中の数値・パラメータ名が原文と一致することはプログラムで全件照合済み
3. 人による原文との照合（確認）は順次実施。**第 1 版の時点では全項目が「未確認（AI 下訳）」です。** 実機の設定には必ず原文と公式ドキュメントを確認してください

## ライセンス

パラメータの説明文は ArduPilot のソースコード（GPL-3.0）中のパラメータ定義コメントです。本資料はその日本語訳（改変物）として、資料・データ・スクリプトの全体を **GNU General Public License version 3（GPL-3.0）** で提供します。

- 原文：© ArduPilot Development Team and contributors
- 日本語訳・解説・注記：© 2026 内海 翔
- 本資料は無保証です（GPL-3.0 第 15・16 条）。ArduPilot および製品名は各権利者の商標です。

## 引用

[CITATION.cff](CITATION.cff) を参照してください（GitHub の「Cite this repository」から書式を取得できます）。

## 誤りの報告

誤訳や不備は Issues でお知らせください。

---

*Unofficial Japanese translation of the ArduCopter 4.7.2 Complete Parameter List. Not affiliated with or endorsed by the ArduPilot project. Licensed under GPL-3.0, same as the original parameter documentation in the ArduPilot source code. Translated with AI assistance; not yet human-reviewed.*
