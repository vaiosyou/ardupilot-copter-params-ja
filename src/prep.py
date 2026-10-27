"""公式メタデータ＋既定値を1つのJSONにまとめ、訳すべきテンプレート一覧を作る"""
import json, re, sys, os, collections
SCR = sys.argv[1]; OUT = sys.argv[2]
j = json.load(open(os.path.join(SCR, "pdef_paths.json")))
src = json.load(open(os.path.join(SCR, "src_defaults.json")))
sitl = json.load(open(os.path.join(SCR, "sitlrun/defaults_raw.json")))
AP = os.path.join(SCR, "apfull")

# #define 解決用
defines = {}
for root in ("libraries", "ArduCopter"):
    for dp, dn, fn in os.walk(os.path.join(AP, root)):
        if "SITL" in dp or "examples" in dp: continue
        for f in fn:
            if not f.endswith((".h", ".cpp")): continue
            for m in re.finditer(r"^\s*#\s*define\s+(\w+)\s+([^\n/]+)", open(os.path.join(dp, f), errors="ignore").read(), re.M):
                defines.setdefault(m.group(1), set()).add(m.group(2).strip())
def num(x, depth=0):
    if x is None or depth > 4: return None
    x = x.strip()
    x = re.sub(r"^\((?:float|int\d*_t|uint\d*_t|int|int8_t)\)\s*", "", x)
    x = re.sub(r"^(?:float|int\d*_t|uint\d*_t)\((.*)\)$", r"\1", x)
    x = x.strip("()").strip()
    if x in ("true",): return 1
    if x in ("false",): return 0
    m = re.fullmatch(r"(-?\d+(?:\.\d*)?(?:e-?\d+)?)[fFuUlL]*", x)
    if m: return float(m.group(1))
    m = re.fullmatch(r"0x([0-9a-fA-F]+)[uUlL]*", x)
    if m: return float(int(m.group(1), 16))
    if re.fullmatch(r"\w+", x) and x in defines and len(defines[x]) == 1:
        return num(next(iter(defines[x])), depth + 1)
    # 単純な四則演算
    if re.fullmatch(r"[0-9.\s+\-*/()fe]+", x):
        try: return float(eval(re.sub(r"(\d)f", r"\1", x)))
        except Exception: return None
    return None

RUNTIME = re.compile(r"(DEV_?ID\d*$|_ID\d*$|PRIO\d_ID|GND_PRESS|CALTEMP|^STAT_|^FORMAT_VERSION$|^SIM_|^BRD_SAFETY_MASK$|^RELAY\d_PIN$|^COMPASS_EXTERN|^COMPASS_SCALE|^COMPASS_OFS|^COMPASS_DIA|^COMPASS_ODI|^INS_.*OFFS|^INS_.*SCAL|^AHRS_TRIM|^MIS_TOTAL$|^FENCE_TOTAL$|^RALLY_TOTAL$|^STAT_)")

def fmt(v):
    if v is None: return None
    if abs(v - round(v)) < 1e-9: return str(int(round(v)))
    return ("%.6g" % v)

def family(g, name):
    base = g if g else name.split("_")[0] + "_"
    m = re.match(r"([A-Z]+)", base)
    return m.group(1) if m else base

norm_num = re.compile(r"\d+(?:\.\d+)?")
templates = {}; tmpl_order = []
labels = {}; label_order = []
NAME = re.compile(r"\b[A-Z][A-Za-z0-9]*(?:_[A-Za-z0-9{}*]+)+\b")
def tmpl_of(text, store, order, fam):
    names = NAME.findall(text)
    k = iter(range(1000))
    t0 = NAME.sub(lambda m: "{P%s}" % chr(97 + next(k)), text)
    nums = norm_num.findall(t0)
    i = iter(range(1000))
    t = norm_num.sub(lambda m: "{%d}" % next(i), t0)
    nums = (names, nums)
    if t not in store:
        store[t] = {"id": len(store), "fam": fam, "count": 0}
        order.append(t)
    store[t]["count"] += 1
    return store[t]["id"], nums

params = []
stats = collections.Counter()
for g, ps in j.items():
    if not isinstance(ps, dict): continue
    for n, v in ps.items():
        if not isinstance(v, dict): continue
        fam = family(g, n)
        desc = re.sub(r"\s+", " ", v.get("Description", "")).strip()
        tid, tnums = tmpl_of(desc, templates, tmpl_order, fam)
        def labs(d):
            if not d: return None
            out = []
            for k, lab in sorted(d.items(), key=lambda kv: float(kv[0]) if re.fullmatch(r"-?[\d.]+", kv[0]) else 1e18):
                lid, lnums = tmpl_of(lab.strip(), labels, label_order, fam)
                out.append({"key": k, "en": lab.strip(), "lid": lid, "nums": lnums})
            return out
        # 既定値
        dv = None; dsrc = None
        if n in sitl and not RUNTIME.search(n) and not v.get("ReadOnly") and not v.get("Calibration"):
            dv = fmt(sitl[n]); dsrc = "S"
        if dv is None:
            x = num(src.get(n))
            if x is not None:
                dv = fmt(x); dsrc = "C"
        stats[dsrc] += 1
        rng = v.get("Range")
        params.append({
            "name": n, "group": g, "family": fam,
            "display": v.get("DisplayName", "").strip(),
            "desc_en": desc, "tid": tid, "tnums": tnums,
            "units": v.get("Units"), "range": [rng.get("low"), rng.get("high")] if isinstance(rng, dict) else None,
            "increment": v.get("Increment"),
            "values": labs(v.get("Values")), "bitmask": labs(v.get("Bitmask")),
            "reboot": bool(v.get("RebootRequired") in ("True", True)),
            "readonly": bool(v.get("ReadOnly")),
            "user": v.get("User"),
            "default": dv, "default_src": dsrc,
            "status": "未確認", "note": "",
        })
params.sort(key=lambda p: p["name"])
json.dump({"params": params,
           "templates": [{"id": templates[t]["id"], "en": t, "fam": templates[t]["fam"], "count": templates[t]["count"]} for t in tmpl_order],
           "labels": [{"id": labels[t]["id"], "en": t, "count": labels[t]["count"]} for t in label_order]},
          open(OUT, "w"), ensure_ascii=False, indent=0)
print("params", len(params), "templates", len(templates), "labels", len(labels), "default src", dict(stats), file=sys.stderr)
