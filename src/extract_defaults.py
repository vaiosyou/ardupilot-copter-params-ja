"""ソースコードから各パラメータの既定値（AP_GROUPINFO の第5引数など）を抜き出す"""
import json, os, re, sys, collections
AP = sys.argv[1]; PD = sys.argv[2]; OUT = sys.argv[3]
j = json.load(open(PD))
# basename -> paths
idx = collections.defaultdict(list)
for root in ("libraries", "ArduCopter"):
    for dp, dn, fn in os.walk(os.path.join(AP, root)):
        for f in fn:
            if f.endswith((".cpp", ".h", ".lua")):
                idx[f].append(os.path.join(dp, f))
cache = {}
def text(p):
    if p not in cache:
        cache[p] = open(p, errors="ignore").read()
    return cache[p]
def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{": depth += 1
        if ch in ")]}":
            if depth == 0: break
            depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    out.append(cur.strip())
    return out
res = {}; why = collections.Counter()
for g, ps in j.items():
    if not isinstance(ps, dict): continue
    for full, v in ps.items():
        if not isinstance(v, dict): continue
        rp = v.get("real_path") or ""
        short = full[len(g):] if g and full.startswith(g) else full
        cands = []
        if rp:
            q = os.path.normpath(os.path.join(AP, "ArduCopter", rp)) if rp.startswith("..") else None
            if q and os.path.exists(q): cands = [q]
            else: cands = idx.get(os.path.basename(rp), [])
        found = None
        for c in cands:
            t = text(c)
            if c.endswith(".lua"):
                m = re.search(r"@Param(?:\{[^}]*\})?:\s*%s\b" % re.escape(full), t)
                if m:
                    mb = re.compile(r"(?:bind_add_param|add_param)\(([^)]*)\)").search(t, m.end())
                    if mb:
                        a = split_args(mb.group(1))
                        nums = [x for x in a if not x.startswith(("'", '"'))]
                        if a and a[-1] and not a[-1].startswith(("'", '"')):
                            found = a[-1]; break
                # bind_add_param('NAME', idx, default) / param:add_param(key, idx, 'NAME', default)
                m = re.search(r"bind_add_param\(\s*['\"]%s['\"]\s*,\s*[^,]+,\s*([^)]+)\)" % re.escape(short), t)
                if m: found = m.group(1).strip(); break
                m = re.search(r"add_param\([^,]+,\s*[^,]+,\s*['\"]%s['\"]\s*,\s*([^)]+)\)" % re.escape(short), t)
                if m: found = m.group(1).strip(); break
                continue
            # まず AP_GROUPINFO("SHORT", ...) を直接探す
            md = re.compile(r"AP_GROUPINFO(?:_FLAGS|_FRAME|_FLAGS_FRAME)?\s*\(\s*\"%s\"\s*,(.*)" % re.escape(short), re.S).search(t)
            if md:
                args = split_args(md.group(1))
                if len(args) >= 4: found = args[3]; break
            md = re.compile(r"GSCALAR\s*\(\s*\w+\s*,\s*\"%s\"\s*,\s*(.*)" % re.escape(short), re.S).search(t)
            if md:
                args = split_args(md.group(1)); found = args[0]; break
            m = re.search(r"@Param(?:\{[^}]*\})?:\s*%s\b" % re.escape(short), t)
            if not m: continue
            m2 = re.compile(r"AP_GROUPINFO(_FLAGS|_FRAME|_FLAGS_FRAME|_FLAGS_DEFAULT_POINTER)?\s*\(\s*\"([A-Z0-9_]+)\"\s*,(.*)", re.S).search(t, m.end())
            m3 = re.compile(r"GSCALAR\s*\(\s*\w+\s*,\s*\"([A-Z0-9_]+)\"\s*,\s*(.*)", re.S).search(t, m.end())
            m4 = re.compile(r"GOBJECT|AP_SUBGROUP|AP_NESTEDGROUP").search(t, m.end())
            cand = [x for x in (m2, m3) if x]
            if not cand: continue
            mm = min(cand, key=lambda x: x.start())
            if mm is m2:
                name = m2.group(2); args = split_args(m2.group(3))
                kind = m2.group(1) or ""
                # args: idx, class, member, default[, flags/frame]
                if len(args) >= 4: found = args[3]
            else:
                name = m3.group(1); args = split_args(m3.group(2)); found = args[0] if args else None
            if name != short and not short.endswith(name):
                found = None; why["name_mismatch"] += 1
            break
        if found is None and re.search(r"_[XYZ]$", short):
            base = short[:-2]
            for c in cands:
                t = text(c)
                md = re.compile(r"AP_GROUPINFO(?:_FLAGS|_FRAME|_FLAGS_FRAME)?\s*\(\s*\"%s\"\s*,(.*)" % re.escape(base), re.S).search(t)
                if md:
                    a = split_args(md.group(1))
                    if len(a) >= 4: found = a[3]; break
        if found is None and g.startswith("OSD") and re.match(r"OSD\d_$", g):
            mo = re.match(r"(.+)_(EN|X|Y)$", short)
            if mo:
                scr = text(os.path.join(AP, "libraries/AP_OSD/AP_OSD_Screen.cpp"))
                ms = re.search(r"AP_SUBGROUPINFO\((\w+),\s*\"%s\"" % re.escape(mo.group(1)), scr)
                if ms:
                    hdr = text(os.path.join(AP, "libraries/AP_OSD/AP_OSD.h"))
                    mh = re.search(r"AP_OSD_Setting\s+%s\s*\{([^}]*)\}" % ms.group(1), hdr)
                    if mh:
                        a = split_args(mh.group(1))
                        k = {"EN": 0, "X": 1, "Y": 2}[mo.group(2)]
                        if len(a) > k: found = a[k]
        if found is None:
            why["notfound"] += 1; continue
        res[full] = found
print(len(res), dict(why), file=sys.stderr)
json.dump(res, open(OUT, "w"), ensure_ascii=False, indent=0)
