import json, sys
from pypdf import PdfReader
r = PdfReader(sys.argv[1]); nd = r.named_destinations
out = {"fam": {}, "param": {}}
for k, v in nd.items():
    name = k.lstrip("/")
    pg = r.get_destination_page_number(v) + 1
    if name.startswith("fam-"):
        out["fam"][name[4:]] = pg
    else:
        out["param"][name] = pg
json.dump(out, open(sys.argv[2], "w"), indent=0)
print(len(r.pages), len(out["fam"]), len(out["param"]), out["fam"].get("ATC"), out["param"].get("ATC_RAT_RLL_P"), out["param"].get("index"))
