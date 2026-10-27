# -*- coding: utf-8 -*-
"""ArduCopter パラメータ日本語解説（非公式）— data.json と訳文から単一 HTML を生成する。

使い方: python3 build_html.py OUT.html [--pages pages.json]
  --pages を渡すと、索引に PDF のページ番号を入れる（PDF 用の 2 回目の生成）。
"""
import json, re, sys, os, html, datetime, collections

HERE = os.path.dirname(os.path.abspath(__file__))
def load(name, default=None):
    p = os.path.join(HERE, name)
    if not os.path.exists(p):
        return default
    return json.load(open(p, encoding="utf-8"))

OUT = sys.argv[1]
PAGES = None
if "--pages" in sys.argv:
    PAGES = json.load(open(sys.argv[sys.argv.index("--pages") + 1], encoding="utf-8"))
PRINT_MODE = "--print" in sys.argv

D = load("data.json")
TR_D = load("tr_desc.json")
TR_L = load("tr_label.json")
NOTES = load("notes.json", {})      # {"PARAM": "注記本文"}
REVIEW = load("review.json", {})    # {"PARAM": "確認済み"}
META = load("meta.json")            # 版・作者などの固定情報

esc = html.escape
TODAY = META["build_date"]

# ---------------- テンプレートの復元 ----------------
def fill(tmpl, names_nums):
    names, nums = names_nums
    s = re.sub(r"\{P([a-z])\}", lambda m: names[ord(m.group(1)) - 97], tmpl)
    s = re.sub(r"\{(\d+)\}", lambda m: nums[int(m.group(1))], s)
    return s

LAB_EN = {t["id"]: t["en"] for t in D["labels"]}
def label_ja(item):
    t = TR_L.get(str(item["lid"]))
    if t is None:
        return None
    return fill(t, item["nums"])

# ---------------- ファミリー（目次のまとまり） ----------------
FAM_JA = {
    "ACRO": "Acro モード", "ADSB": "ADS-B 受信機", "AFS": "高度フェイルセーフ（AFS）", "AHRS": "姿勢推定（AHRS）",
    "ANGLE": "傾き角", "ARMING": "アーム前チェック", "AROT": "ヘリのオートローテーション", "ARSPD": "対気速度センサ",
    "ATC": "姿勢制御（角度・角速度 PID）", "AUTO": "Auto モード", "AUTOTUNE": "AutoTune（自動調整）",
    "AVD": "ADS-B による回避", "AVOID": "障害物・フェンス回避", "BARO": "気圧計", "BATT": "バッテリー監視",
    "BCN": "ビーコン測位", "BRD": "フライトコントローラ基板", "BTN": "ボタン入力", "CAM": "カメラ",
    "CAN": "CAN バス・DroneCAN", "CC": "カスタム制御器", "CHUTE": "パラシュート", "CIRCLE": "Circle モード",
    "COMPASS": "磁気コンパス", "CUST": "カスタム取付角", "DDS": "DDS（ROS 2 連携）", "DEV": "開発者向け",
    "DID": "OpenDroneID（リモート ID）", "DISARM": "自動ディスアーム", "EAHRS": "外部 AHRS", "EFI": "電子燃料噴射（EFI）",
    "EK2": "EKF2", "EK3": "拡張カルマンフィルタ（EKF3）", "ESC": "ESC", "FENCE": "ジオフェンス", "FFT": "ジャイロ FFT 解析",
    "FHLD": "FlowHold モード", "FILT": "汎用フィルタ", "FLIGHT": "飛行オプション", "FLOW": "オプティカルフロー",
    "FLTMODE": "フライトモード割り当て", "FOLL": "Follow（追従）", "FORMAT": "パラメータ形式", "FRAME": "フレーム",
    "FRSKY": "FrSky テレメトリ", "FS": "フェイルセーフ", "FSTRATE": "高速レートスレッド", "GCS": "地上局（GCS）",
    "GEN": "発電機", "GND": "地面効果", "GPS": "GPS／GNSS", "GRIP": "グリッパー", "GUID": "Guided モード",
    "H": "ヘリコプター", "IM": "ヘリのコレクティブ入力", "INITIAL": "起動時モード", "INS": "慣性センサ（IMU）",
    "KDE": "KDE ESC", "LAND": "着陸", "LGR": "ランディングギア", "LOG": "ログ記録", "LOIT": "Loiter モード",
    "MAV": "MAVLink 通信", "MIS": "ミッション", "MNT": "マウント（ジンバル）", "MOT": "モーター出力",
    "MSP": "MSP（OSD 等）", "NET": "ネットワーク（Ethernet・PPP）", "NMEA": "NMEA 出力", "NTF": "通知（LED・ブザー）",
    "OA": "経路計画型の障害物回避", "OSD": "OSD（画面表示）", "PHLD": "PosHold モード", "PILOT": "パイロット操作",
    "PLDP": "ペイロード配置", "PLND": "精密着陸", "PRX": "近接センサ", "PSC": "位置・速度・加速度制御",
    "RALLY": "ラリーポイント", "RC": "RC 入力", "RCMAP": "RC チャンネル割り当て", "RELAY": "リレー",
    "RNGFND": "距離センサ（レンジファインダ）", "RPM": "回転数センサ", "RSSI": "受信信号強度", "RTL": "RTL（帰還）",
    "SCHED": "スケジューラ", "SCR": "Lua スクリプト", "SERIAL": "シリアルポート", "SERVO": "出力チャンネル（サーボ・モーター）",
    "SID": "システム同定", "SIM": "シミュレータ（SITL）専用", "SIMPLE": "Simple モード", "SPRAY": "散布機",
    "SRTL": "SmartRTL", "STAT": "統計情報", "SUPER": "Super Simple モード", "SURFTRAK": "地表追従",
    "TCAL": "温度キャリブレーション", "TEMP": "温度センサ", "TERRAIN": "地形データ", "THR": "スロットル",
    "THROW": "Throw モード", "TKOFF": "離陸", "TUNE": "送信機ノブによる調整", "VISO": "ビジュアルオドメトリ",
    "VTX": "映像送信機", "WINCH": "ウインチ", "WP": "ウェイポイント航法", "WVANE": "ウェザーベーン", "ZIGZ": "ZigZag モード",
    "SCRIPTS": "Lua スクリプト（アプレット・ドライバ）用", "RCK": "Rockblock（衛星通信）", "STAT_": "統計",
}

def family_of(p):
    name = p["name"]
    tok = name.split("_")[0]
    if re.fullmatch(r"EK[23]", tok):
        return tok
    tok = re.sub(r"\d+$", "", tok)
    if re.fullmatch(r"BATT[A-G]", tok):
        return "BATT"
    if tok == "RNGFNDA":
        return "RNGFND"
    if tok == "CC" and name.startswith("CC"):
        return "CC"
    return tok

params = D["params"]
for p in params:
    p["fam"] = family_of(p)
    p["is_script"] = (p["group"] == "")
# 1〜2 項目しかないスクリプト由来のファミリーはまとめる
cnt = collections.Counter(p["fam"] for p in params)
for p in params:
    if p["is_script"] and cnt[p["fam"]] <= 2:
        p["fam"] = "SCRIPTS"
def nkey(name):
    return [int(t) if t.isdigit() else t for t in re.split(r"(\d+)", name)]
fams = collections.OrderedDict()
for p in sorted(params, key=lambda x: (x["fam"], nkey(x["name"]))):
    fams.setdefault(p["fam"], []).append(p)
fam_order = sorted(fams.keys(), key=lambda f: (f == "SCRIPTS", f))
script_fams = {f for f in fams if all(x["is_script"] for x in fams[f])}

# ---------------- 部品 ----------------
def default_html(p):
    if p["default"] is None:
        return '<span class="na">—</span>'
    mark = {"S": "S", "C": "C"}[p["default_src"]]
    title = {"S": "SITL（クアッド機）で初期化直後に読み出した値", "C": "ソースコードに記載された既定値"}[p["default_src"]]
    lab = ""
    for it in (p["values"] or []):
        try:
            if float(it["key"]) == float(p["default"]):
                lab = " = " + esc(label_ja(it) or it["en"])
        except ValueError:
            pass
    return f'{esc(p["default"])}{lab}<sup class="src" title="{title}">{mark}</sup>'

first_values = {}   # 選択肢の重複表示を避ける
def values_html(p, kind):
    items = p[kind]
    if not items:
        return ""
    key = kind + json.dumps([(i["key"], i["en"]) for i in items])
    head = "選択肢" if kind == "values" else "ビットマスク"
    if key in first_values and len(items) > 6:
        ref = first_values[key]
        return f'<div class="vals"><span class="k">{head}</span> <a href="#{ref}">{ref}</a> と同じ（{len(items)} 項目）</div>'
    first_values.setdefault(key, p["name"])
    parts = []
    for it in items:
        ja = label_ja(it)
        k = ("bit" + it["key"]) if kind == "bitmask" else it["key"]
        if ja and ja != it["en"]:
            parts.append(f'<span class="v"><b>{esc(k)}</b>: {esc(ja)} <span class="en">({esc(it["en"])})</span></span>')
        else:
            parts.append(f'<span class="v"><b>{esc(k)}</b>: {esc(it["en"])}</span>')
    return f'<div class="vals"><span class="k">{head}</span> ' + '<span class="sep">／</span>'.join(parts) + "</div>"

def row_html(p):
    tr = TR_D.get(str(p["tid"]))
    ja = fill(tr, p["tnums"]) if tr else ""
    meta = []
    if p["units"]:
        meta.append(f'<span><span class="k">単位</span> {esc(p["units"])}</span>')
    if p["range"]:
        meta.append(f'<span><span class="k">範囲</span> {esc(str(p["range"][0]))} 〜 {esc(str(p["range"][1]))}</span>')
    if p["increment"]:
        meta.append(f'<span><span class="k">増分</span> {esc(str(p["increment"]))}</span>')
    meta.append(f'<span><span class="k">既定値</span> {default_html(p)}</span>')
    badges = []
    if p["reboot"]:
        badges.append('<span class="b reboot">再起動が必要</span>')
    if p["readonly"]:
        badges.append('<span class="b ro">読み取り専用</span>')
    st = REVIEW.get(p["name"], "未確認")
    badges.append(f'<span class="b st {"ok" if st == "確認済み" else "ng"}">{"確認済み" if st == "確認済み" else "未確認（AI下訳）"}</span>')
    note = NOTES.get(p["name"], "").strip()
    note_html = f'<div class="note"><span class="k">研究注記</span> {esc(note)}</div>' if note else ""
    search = (p["name"] + " " + p["display"] + " " + ja + " " + p["desc_en"]).lower()
    return (f'<tr id="{esc(p["name"])}" data-s="{esc(search)}">'
            f'<td class="n"><div class="pn">{esc(p["name"]).replace("_", "_<wbr>")}</div>'
            f'<div class="dn">{esc(p["display"])}</div><div class="badges">{"".join(badges)}</div></td>'
            f'<td class="d"><div class="ja">{esc(ja)}</div>'
            f'<div class="orig">{esc(p["desc_en"])}</div>'
            f'<div class="meta">{"".join(meta)}</div>'
            f'{values_html(p, "values")}{values_html(p, "bitmask")}{note_html}</td></tr>')

# ---------------- 本文 ----------------
total = len(params)
n_trans = sum(1 for p in params if str(p["tid"]) in TR_D)
n_def = sum(1 for p in params if p["default"] is not None)
n_defS = sum(1 for p in params if p["default_src"] == "S")
n_reboot = sum(1 for p in params if p["reboot"])
n_ok = sum(1 for p in params if REVIEW.get(p["name"]) == "確認済み")

body = []
for f in fam_order:
    ps = fams[f]
    title = FAM_JA.get(f, "")
    if f in script_fams and f != "SCRIPTS":
        title = (title + "（Lua スクリプト用）") if title else "Lua スクリプト（アプレット／ドライバ）用"
    body.append(f'<section class="fam" id="fam-{esc(f)}"><h2><span class="fc">{esc(f if f != "SCRIPTS" else "その他")}</span>'
                f'{esc(title)}<span class="cnt">{len(ps)} 項目</span></h2>')
    body.append('<table class="pt"><colgroup><col class="c1"><col class="c2"></colgroup><thead><tr><th>パラメータ</th><th>説明（上：日本語訳／下：原文）</th></tr></thead><tbody>')
    body.extend(row_html(p) for p in ps)
    body.append("</tbody></table></section>")

toc = ['<ol class="toc">']
for f in fam_order:
    title = FAM_JA.get(f, "")
    if f in script_fams and f != "SCRIPTS":
        title = (title + "（Lua スクリプト用）") if title else "Lua スクリプト用"
    pg = f'<span class="pg">{PAGES["fam"].get(f, "")}</span>' if PAGES else ""
    toc.append(f'<li><a href="#fam-{esc(f)}"><span class="fc">{esc(f if f != "SCRIPTS" else "その他")}</span> {esc(title)} '
               f'<span class="cnt">（{len(fams[f])}）</span></a>{pg}</li>')
toc.append("</ol>")

idx = ['<div class="index">']
cur = None
for p in sorted(params, key=lambda x: nkey(x["name"])):
    c = p["name"][0]
    if c != cur:
        idx.append(f'<div class="il">{c}</div>')
        cur = c
    pg = f' <span class="pg">{PAGES["param"].get(p["name"], "")}</span>' if PAGES else ""
    idx.append(f'<div class="ie"><a href="#{esc(p["name"])}">{esc(p["name"])}</a>{pg}</div>')
idx.append("</div>")

M = META
CSS = r"""
:root{--ink:#111;--sub:#555;--line:#666;--head:#d9e2f3;--bg:#fff;--note:#f3f3f3;--accent:#1f3b73}
*{box-sizing:border-box}
html{background:var(--bg)}
body{font-family:'Yu Gothic','游ゴシック','Meiryo','Noto Sans CJK JP','IPAGothic',sans-serif;font-size:10pt;line-height:1.55;color:var(--ink);background:var(--bg);margin:0 auto;padding:16px;max-width:19cm}
h1{font-size:20pt;margin:0 0 8px}
h2{font-size:13pt;margin:22px 0 8px;border-bottom:1px solid #444;padding-bottom:2px;break-after:avoid}
h2 .fc{font-family:Consolas,'DejaVu Sans Mono','Courier New',monospace;background:var(--head);padding:0 6px;margin-right:8px;border:1px solid var(--line)}
h2 .cnt{float:right;font-size:9pt;color:var(--sub);font-weight:normal;margin-top:4px}
h3{font-size:11.5pt;margin:16px 0 6px}
a{color:var(--accent);text-decoration:none}
.unofficial{border:2px solid #b00;color:#b00;font-weight:bold;padding:4px 8px;display:inline-block;margin:6px 0}
.notice{background:var(--note);border:1px solid #ccc;padding:8px 10px;font-size:9.5pt;margin:8px 0}
.cover{min-height:24cm;display:flex;flex-direction:column;justify-content:center;break-after:page}
.cover .sub{font-size:13pt;color:var(--sub);margin-bottom:18px}
.cover table{border-collapse:collapse;margin-top:18px;font-size:10.5pt}
.cover td{border:1px solid var(--line);padding:4px 8px;vertical-align:top}
.cover td:first-child{background:var(--head);white-space:nowrap}
.chapter{break-before:page}
table.pt{border-collapse:collapse;width:100%;table-layout:fixed;margin-bottom:6px}
table.pt col.c1{width:4.3cm}
table.pt th,table.pt td{border:1px solid var(--line);padding:3px 5px;vertical-align:top;font-size:8.6pt;overflow-wrap:anywhere}
table.pt th{background:var(--head);font-weight:bold}
table.pt thead{display:table-header-group}
table.pt tr{break-inside:avoid}
.pn{font-family:Consolas,'DejaVu Sans Mono','Courier New',monospace;font-weight:bold;font-size:8.8pt}
.dn{color:var(--sub);font-size:7.6pt;margin-top:2px}
.badges{margin-top:3px}
.b{display:inline-block;font-size:7pt;border:1px solid #999;padding:0 3px;margin:1px 2px 0 0;border-radius:2px;white-space:nowrap}
.b.reboot{border-color:#b55;color:#a22}
.b.ro{border-color:#777;color:#444}
.b.st.ng{border-color:#bbb;color:#777}
.b.st.ok{border-color:#2a7;color:#175}
.ja{font-size:9pt}
.orig{color:#666;font-size:7.6pt;margin-top:2px;font-family:Arial,Helvetica,sans-serif}
.meta{margin-top:3px;font-size:8pt}
.meta>span{margin-right:10px;white-space:nowrap}
.k{display:inline-block;background:#eef1f7;border:1px solid #c9d2e3;font-size:7.2pt;padding:0 3px;margin-right:3px;color:#333}
.src{font-size:6.5pt;color:#36c;margin-left:1px}
.na{color:#999}
.vals{margin-top:3px;font-size:7.9pt}
.vals .v{white-space:normal}
.vals .en{color:#777;font-size:7.2pt}
.vals .sep{color:#bbb;margin:0 2px}
.note{margin-top:4px;border-left:3px solid #2a7;background:#f2faf5;padding:2px 6px;font-size:8.4pt}
ol.toc{columns:2;column-gap:1cm;padding-left:0;list-style:none;font-size:9pt}
ol.toc li{break-inside:avoid;margin:1px 0;display:flex;justify-content:space-between}
ol.toc .fc{font-family:Consolas,'DejaVu Sans Mono',monospace;font-weight:bold}
ol.toc .cnt{color:var(--sub);font-size:8pt}
.pg{color:var(--sub);font-variant-numeric:tabular-nums;padding-left:6px}
.index{columns:3;column-gap:.6cm;font-size:7.8pt;font-family:Consolas,'DejaVu Sans Mono','Courier New',monospace}
.index .il{font-weight:bold;font-size:10pt;margin-top:6px;border-bottom:1px solid #999;break-after:avoid;font-family:inherit}
.index .ie{display:flex;justify-content:space-between;break-inside:avoid}
table.info{border-collapse:collapse;width:100%;font-size:9pt;margin:6px 0}
table.info td,table.info th{border:1px solid var(--line);padding:3px 6px;vertical-align:top;text-align:left}
table.info th{background:var(--head);width:4.5cm}
.searchbar{position:sticky;top:0;background:var(--bg);padding:8px 0;border-bottom:1px solid #ccc;z-index:5}
.searchbar input{width:100%;font-size:11pt;padding:6px 8px;border:1px solid #888}
.searchbar .hint{font-size:8.5pt;color:var(--sub)}
.topnote{font-size:8.5pt;color:#b00;text-align:center;border-bottom:1px solid #b00;padding:2px 0;margin-bottom:6px}
ul,ol{padding-left:1.4em}
code{font-family:Consolas,'DejaVu Sans Mono','Courier New',monospace;font-size:90%}
@page{size:A4;margin:16mm 14mm 16mm 14mm}
@media print{
  body{max-width:none;padding:0}
  .searchbar,.screen-only{display:none!important}
  a{color:inherit}
}
@media screen and (max-width:700px){table.pt col.c1{width:34%}ol.toc{columns:1}.index{columns:2}}
"""

JS = r"""
(function(){
  var q=document.getElementById('q'); if(!q) return;
  var rows=[].slice.call(document.querySelectorAll('table.pt tbody tr'));
  var secs=[].slice.call(document.querySelectorAll('section.fam'));
  var cnt=document.getElementById('qc'); var t=null;
  function run(){
    var v=q.value.trim().toLowerCase(); var n=0;
    var terms=v.split(/\s+/).filter(Boolean);
    rows.forEach(function(r){
      var s=r.getAttribute('data-s'); var ok=terms.every(function(x){return s.indexOf(x)>=0;});
      r.style.display=ok?'':'none'; if(ok) n++;
    });
    secs.forEach(function(sc){
      var vis=sc.querySelector('tbody tr:not([style*="none"])'); sc.style.display=vis?'':'none';
    });
    cnt.textContent = terms.length ? (n+' 件該当') : '';
  }
  q.addEventListener('input',function(){clearTimeout(t);t=setTimeout(run,150);});
})();
"""

license_rows = "".join(f"<tr><th>{esc(k)}</th><td>{v}</td></tr>" for k, v in M["license_rows"])
src_rows = "".join(f"<tr><th>{esc(k)}</th><td>{v}</td></tr>" for k, v in M["source_rows"])
hist = "".join(f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in M["history"])

doc = f"""<!DOCTYPE html>
<html lang="ja"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(M["title_short"])}</title>
<meta name="description" content="{esc(M["title"])}（非公式の日本語訳）">
<style>{CSS}</style></head><body>
<div class="topnote screen-only">ArduPilot 公式のものではない、非公式の日本語訳です。</div>

<section class="cover">
  <div class="unofficial">ArduPilot 公式のものではない、非公式の日本語訳</div>
  <h1>{esc(M["title"])}</h1>
  <div class="sub">{esc(M["subtitle"])}</div>
  <table>
    <tr><td>対象</td><td>ArduCopter {esc(M["version"])}（{esc(M["version_note"])}）</td></tr>
    <tr><td>収録数</td><td>{total} パラメータ（{len(fam_order)} グループ）</td></tr>
    <tr><td>作成日</td><td>{esc(TODAY)}（第 {esc(M["edition"])} 版）</td></tr>
    <tr><td>作者</td><td>{esc(M["author"])}</td></tr>
    <tr><td>ライセンス</td><td>{M["license_short"]}</td></tr>
    <tr><td>元データ</td><td>{M["source_short"]}</td></tr>
    <tr><td>確認状況</td><td>確認済み {n_ok} ／ 未確認（AI 下訳のまま） {total - n_ok}</td></tr>
  </table>
  <div class="notice" style="margin-top:18px">本資料は ArduPilot プロジェクトが作成・承認したものではありません。訳文には誤りが含まれる可能性があります。実機の設定には、必ず原文（各パラメータの下段）と公式ドキュメントを確認してください。</div>
</section>

<section class="chapter" id="intro">
<h2>はじめに</h2>
<p>本資料は、オープンソースの飛行制御ソフトウェア ArduPilot のマルチコプター用ファームウェア ArduCopter {esc(M["version"])} の全パラメータ（{total} 項目）について、説明文と選択肢の意味を日本語に訳したものです。日本語で全パラメータを網羅した資料が見当たらなかったため、研究・教育での参照用に作成しました。</p>
<h3>収録内容</h3>
<ul>
<li>パラメータ名・単位・数値は原文のまま。説明文と選択肢（Values）・ビットマスク（Bitmask）の名前を日本語に訳しました。機種名・製品名・プロトコル名など固有名詞の選択肢は原文のままです。</li>
<li>各パラメータに、単位、範囲、増分、既定値、再起動の要否、読み取り専用かどうか、翻訳の確認状況を付けています。</li>
<li>OSD・シミュレータ（SIM_）・Lua スクリプト用など、公式一覧に含まれるパラメータもすべて収録しています。</li>
</ul>
<h3>使い方</h3>
<ul>
<li>目次のグループ（パラメータ名の接頭辞）から探すか、巻末の索引（アルファベット順）を使ってください。</li>
<li>PDF 版ではビューアの検索機能で、HTML 版では本文冒頭の絞り込み欄で、パラメータ名・日本語・英語のどれでも検索できます（HTML 版は外部と通信しません）。</li>
<li>各行の上段が日本語訳、下段（灰色）が原文です。判断に迷う場合は原文を優先してください。</li>
<li>同じ選択肢一覧を持つパラメータ（SERVO1〜32_FUNCTION など）は、2 回目以降を「○○ と同じ」として省略しています。</li>
</ul>
<h3>表記の約束</h3>
<table class="info">
<tr><th>既定値</th><td>右肩の <b>S</b> は、ArduCopter {esc(M["version"])} を SITL（ソフトウェアシミュレータ、クアッド機）で設定を消去して起動した直後に読み出した値。<b>C</b> は、ソースコードに記載された既定値（SITL では表示されない項目）。<b>—</b> は、ソース上で条件によって値が変わる、またはボード固有のため一意に決められなかった項目（{total - n_def} 項目）。実機の既定値はボードや機体設定により異なる場合があります。</td></tr>
<tr><th>再起動が必要</th><td>変更を反映するためにフライトコントローラの再起動が必要な項目（{n_reboot} 項目）。</td></tr>
<tr><th>読み取り専用</th><td>自動で設定される値で、手動で変更しない項目。</td></tr>
<tr><th>確認状況</th><td>「未確認（AI 下訳）」は AI による下訳のままで、人による確認が済んでいないもの。人が原文と照合したものだけを「確認済み」とします。</td></tr>
<tr><th>研究注記</th><td>作者の研究（長尺アーム付きマルチコプターの強化学習制御）での経験に基づく補足。姿勢制御（ATC_）、位置制御（PSC_）、センサ・EKF 系（EK3_、INS_ など）から順に追記します。現在の版で記入済みの注記は {sum(1 for v in NOTES.values() if v.strip())} 件です。</td></tr>
</table>
<h3>作成方法（AI による下訳と確認）</h3>
<ol>
<li><b>元データの取得</b>：GitHub の ArduPilot リポジトリからタグ {esc(M["tag"])} を取得し、公式のパラメータ一覧（Complete Parameter List）を生成するのと同じツール（<code>Tools/autotest/param_metadata/param_parse.py</code>）で全パラメータの定義（説明・単位・範囲・選択肢など）を JSON に書き出しました。</li>
<li><b>既定値の取得</b>：公式の一覧には既定値が載っていないため、同じタグのファームウェアを SITL 用にビルドし、設定を消去した状態で起動して全パラメータを読み出しました。SITL で表示されない項目は、ソースコード中の定義から既定値を抽出しました。</li>
<li><b>AI による下訳</b>：Anthropic 社の AI「Claude」（Claude Code 環境）で説明文と選択肢名を日本語に下訳しました。番号違いの同文（例：BATT2〜BATT9）は 1 つの文型にまとめて訳し、数値とパラメータ名は機械的に差し込んでいます。訳文中の数値・パラメータ名が原文と一致することはプログラムで全件照合済みです。</li>
<li><b>人による確認</b>：作者が原文と照合し、確認したパラメータから「確認済み」に変えていきます。現時点の確認済みは {n_ok} 項目です。</li>
</ol>
<p class="notice">AI の下訳には、専門用語の誤訳や意味の取り違えが含まれる可能性があります。「未確認」の項目は特に原文を併せて確認してください。誤りの報告を歓迎します。</p>
</section>

<section class="chapter" id="toc">
<h2>目次（グループ別）</h2>
<p style="font-size:9pt">グループはパラメータ名の接頭辞（最初の「_」まで、末尾の番号を除く）で分けています。括弧内は項目数です。</p>
{"".join(toc)}
<p style="font-size:9pt">巻末：<a href="#index">索引（アルファベット順）</a> ／ <a href="#license">出典・ライセンス・変更履歴</a></p>
</section>

<section class="chapter" id="body">
<div class="searchbar screen-only"><input id="q" type="search" placeholder="絞り込み：パラメータ名・日本語・英語（例：ATC_RAT、ホバリング、failsafe）"><div class="hint"><span id="qc"></span> 空白区切りで AND 検索。外部通信はしません。</div></div>
<h2 style="border:none">本文</h2>
{"".join(body)}
</section>

<section class="chapter" id="index">
<h2>索引（アルファベット順）</h2>
{"".join(idx)}
</section>

<section class="chapter" id="license">
<h2>出典・ライセンス・変更履歴</h2>
<h3>出典</h3>
<table class="info">{src_rows}</table>
<h3>ライセンス</h3>
<table class="info">{license_rows}</table>
<h3>変更履歴</h3>
<table class="info">{hist}</table>
<div class="notice">ArduPilot 公式のものではない、非公式の日本語訳です。ArduPilot および関連名称は各権利者に帰属します。本資料に広告は含まれません。</div>
</section>
<script>{JS}</script>
</body></html>"""

open(OUT, "w", encoding="utf-8").write(doc)
print("written", OUT, "params", total, "families", len(fam_order), "translated", n_trans, "defaults", n_def, "S", n_defS, file=sys.stderr)
