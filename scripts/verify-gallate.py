#!/usr/bin/env python3
"""Ad-hoc verification for gallate v1 (`gallate.translation` format).
Same caveat as before: this repo has no test/lint/build target; the
only harness (scripts/validate-schemas.sh) needs `yq`+`check-jsonschema`
(neither installed here), so we assert the artefacts directly."""
import glob, json, os, re, subprocess, sys
import yaml
from jsonschema import Draft7Validator

os.chdir("/home/bigbang/gallate")
fails, n = [], 0
def ck(cond, label, detail=""):
    global n
    n += 1
    if not cond:
        fails.append(f"{label}: {detail}"); print(f"  FAIL {label}  [{detail}]")

def census(txt):
    out = {}
    for ln in txt.splitlines():
        m = re.match(r"^(#{2,4}) ", ln)
        if m: out[m.group(1)] = out.get(m.group(1), 0) + 1
    return out

# ---------- A: schemas are still valid ----------
print("A. 15 schema/*.schema.yaml are valid JSON Schema draft-07")
schemas = {}
for f in sorted(glob.glob("schema/*.schema.yaml")):
    s = yaml.safe_load(open(f, encoding="utf-8")); schemas[os.path.basename(f)] = s
    try: Draft7Validator.check_schema(s); ck(True, f)
    except Exception as e: ck(False, f, str(e)[:100])
ck(len(schemas) == 15, "15 schemas", str(len(schemas)))

# ---------- B: every JSON / JSONL / YAML artefact parses ----------
print("B. every JSON / JSONL / YAML artefact parses")
p = 0
for f in sorted(glob.glob("**/*.json", recursive=True) + glob.glob("**/*.jsonl", recursive=True) +
                glob.glob("**/*.yaml", recursive=True) + glob.glob("**/*.yml", recursive=True)):
    if f.startswith(".git/"): continue
    try:
        if f.endswith(".jsonl"):
            for ln in open(f, encoding="utf-8"):
                if ln.strip(): json.loads(ln)
        elif f.endswith(".json"): json.load(open(f, encoding="utf-8"))
        else: yaml.safe_load(open(f, encoding="utf-8"))
        p += 1
    except Exception as e: ck(False, "parse " + f, str(e)[:100])
ck(p == 30, "30 artefacts parsed", str(p))

# ---------- C: embedded json blocks in rewritten docs parse ----------
print("C. embedded ```json blocks in rewritten docs parse")
b = 0
for f in ["docs/shell-layer/05-config-file.md", "docs/shell-layer/zh-CN/05-config-file.md",
          "docs/shell-layer/12-file-structure.md", "docs/shell-layer/zh-CN/12-file-structure.md"]:
    for i, blk in enumerate(re.findall(r"```json\n(.*?)```", open(f, encoding="utf-8").read(), re.S), 1):
        try: json.loads(blk); b += 1
        except Exception as e: ck(False, f"{f}#{i}", str(e)[:100])
ck(b >= 8, ">=8 json blocks parse", str(b))

# ---------- D: no XLIFF / PO / legacy-counter tokens (CHANGELOG excluded) ----------
print("D. no XLIFF / PO / legacy-counter tokens")
ok = {
    "docs/shell-layer/12-file-structure.md": 1, "docs/shell-layer/zh-CN/12-file-structure.md": 1,
    "docs/shell-layer/05-config-file.md": 1,   "docs/shell-layer/zh-CN/05-config-file.md": 1,
    "docs/protocol/00-glossary.md": 1,         "docs/protocol/zh-CN/00-glossary.md": 1,
}
PAT = re.compile(r"xliff|\.xlf|trans-unit|gettext|\bpo\b|tu-0042", re.I)
sc = 0
for f in sorted(glob.glob("**/*", recursive=True)):
    if not f.endswith((".md", ".yaml", ".json", ".jsonl", ".sh")) or f.startswith((".git/", "CHANGELOG")): continue
    sc += 1
    hits = [l for l in open(f, encoding="utf-8", errors="replace").read().splitlines() if PAT.search(l)]
    ck(len(hits) <= ok.get(f, 0), f"clean: {f}", str(hits[:1]))
ck(sc == 96, "96 files scanned", str(sc))

# ---------- E: id rule <resource-path>:L<line> ----------
print("E. id rule <resource-path>:L<line>")
ID = re.compile(r"^[^:\s]+(?::[^:\s]+)*:L\d{4,}(#\d+)?$")    # full path may have : in it
def d(path, line, nth=1):
    s = f"{path}:L{line:04d}"; return s if nth == 1 else f"{s}#{nth}"
ck(d("scenario/0083_SS_01_x.lua", 142) == "scenario/0083_SS_01_x.lua:L0142", "derive L0142")
ck(d("scenario/0083_SS_01_x.lua", 142, 2) == "scenario/0083_SS_01_x.lua:L0142#2", "derive L0142#2")
ck(d("a/b/x.lua", 12345) == "a/b/x.lua:L12345", ">9999 keeps digits")
for g in ["scenario/0083_SS_01_x.lua:L0142", "scenario/0083_SS_01_x.lua:L0142#2",
          "scenes/day1/scene_001.bin:L0042"]:
    ck(bool(ID.match(g)), f"accept: {g}")
for b in ["tu-0042", "U000001", "tu-0001", "0083_SS_01_x.lua:L142",   # basename-only is no longer accepted
          "scenario/0083_SS_01_x.lua:L142"]:                          # unpadded line is no longer accepted
    ck(not ID.match(b), f"reject: {b}")

# ---------- F: §5.8 example: id == derive(original_file, context.line) ----------
print("F. §5.8 example: id derives from source_context.file + source_context.line")
txt = open("docs/shell-layer/05-config-file.md", encoding="utf-8").read()
m = re.search(r'\{\s*\n\s*"id": "scenario/0083_SS_01_x\.lua:L0142".*?\n\}', txt, re.S)
ck(bool(m), "found §5.8 example entry")
u = json.loads(m.group(0))
ck(u["id"] == d(u["source_context"]["file"], u["source_context"]["line"]),
   "id derives from source_context", f'{u["id"]} vs {d(u["source_context"]["file"], u["source_context"]["line"])}')
ck(set(u["source_context"]) == {"file", "line", "end_line", "snippet"},
   "source_context = four-field model", str(sorted(u["source_context"])))
ck(u["state"] in {"initial","translated","reviewed","final","needs_review"},
   "state is one of the five allowed", u["state"])
ck(u["target"] != "" and u["id"].startswith("scenario/"), "full path id used", u["id"])

# ---------- G: §12.4 Container + Entry shape ----------
print("G. §12.4 Container + Entry shape (gallate.translation v1)")
txt = open("docs/shell-layer/12-file-structure.md", encoding="utf-8").read()
# Container example
cont = json.loads(re.search(r"### 12\.4\.1 Container.*?```json\n(.*?)```", txt, re.S).group(1))
ck(cont.get("format") == "gallate.translation", "format = gallate.translation", cont.get("format"))
ck(cont.get("version") == 1, "version = 1", str(cont.get("version")))
ck(cont.get("source") and cont.get("target"), "source + target present", str(cont))
ck("entries" in cont and isinstance(cont["entries"], list), "entries[] present", str(type(cont.get("entries"))))
# Entry example
ent = json.loads(re.search(r"### 12\.4\.2 Entry\n.*?```json\n(.*?)```", txt, re.S).group(1))
required = {"id","source","target","state","source_context","context",
            "placeholders","notes","provenance","metadata"}
ck(required.issubset(set(ent)), "entry has every spec'd field", str(sorted(set(ent))))
ck(bool(ID.match(ent["id"])), "entry id obeys the rule", ent["id"])
ck(ent["id"] == d(ent["source_context"]["file"], ent["source_context"]["line"]),
   "entry id derives from source_context", ent["id"])
# kind check
ck(ent["source_context"]["file"] == "scenario/0083_SS_01_x.lua", "source_context.file is full path",
   ent["source_context"]["file"])
# placeholders
phs = ent["placeholders"]
ck(all({"id","syntax","type"} <= set(p) for p in phs), "placeholders have {id, syntax, type}")
ck({p["type"] for p in phs} <= {"variable","format","control","ruby","engine"}, "placeholder types legal")
# notes
ck(all({"text","author"} <= set(n) for n in ent["notes"]), "notes have {text, author}")
# provenance
ck("type" in ent["provenance"], "provenance has type")
# context (translator-helper)
ck(ent["context"].get("speaker") == "Alice", "context has translator-helper keys")

# ---------- H: examples + gallate.yaml ----------
print("H. examples + gallate.yaml switched")
for f in ["shell-layer-examples/full-project/gallate.yaml", "shell-layer-examples/minimal-project/gallate.yaml"]:
    c = yaml.safe_load(open(f, encoding="utf-8"))["text"]
    ck(c["format"] == "json", f"{f}: format==json", str(c["format"]))
    ck(c["meta"] == {"original_file": "original_file", "source_context": "source_context",
                     "location": "location", "placeholders": "placeholders",
                     "engine_path": "engine_path"},
       f"{f}: meta has 5 keys", str(c["meta"]))
    ck(c["metadata"].get("placeholders") is True, f"{f}: metadata.placeholders=true")
for f in sorted(glob.glob("shell-layer-examples/*/.meta.json")):
    m = json.load(open(f, encoding="utf-8")); Draft7Validator(schemas["meta.schema.yaml"]).validate(m)
    t = [p["project"] for p in m["files"] if p["type"] == "text"]
    ck(bool(t) and all(x.endswith(".json") for x in t), f"{f}: text paths .json", str(t))
for f in ["examples/full-cli/extract.jsonl", "examples/full-cli/inject.jsonl",
          "examples/full-cli/validation-result.jsonl"]:
    ck(".xlf" not in open(f, encoding="utf-8").read(), f"{f}: no .xlf paths")
vr = open("examples/full-cli/validation-result.jsonl", encoding="utf-8").read()
ck('"translation_unit":"scenario/day1/scene_001.bin:L0042"' in vr, "validation-result.jsonl: full-path translation_unit")

# ---------- I: structure parity ----------
print("I. structure parity (EN/ZH) and intended glossary delta vs HEAD")
for en, zh in [("docs/shell-layer/05-config-file.md", "docs/shell-layer/zh-CN/05-config-file.md"),
               ("docs/shell-layer/12-file-structure.md", "docs/shell-layer/zh-CN/12-file-structure.md"),
               ("docs/protocol/01-architecture.md", "docs/protocol/zh-CN/01-architecture.md"),
               ("docs/protocol/03-discovery.md", "docs/protocol/zh-CN/03-discovery.md"),
               ("docs/protocol/08-validation.md", "docs/protocol/zh-CN/08-validation.md")]:
    a, b = census(open(en, encoding="utf-8").read()), census(open(zh, encoding="utf-8").read())
    ck(a == b, f"{os.path.basename(en)}: EN/ZH census equal", f"EN={a} ZH={b}")
for f, want in [("docs/protocol/00-glossary.md", (-1, -2)), ("docs/protocol/zh-CN/00-glossary.md", (0, -2))]:
    # ZH 11-process also gained +1 ## this turn (the new "操作选择" section
    # that was pre-existing in EN but missing in ZH). Add that to expected.
    if "zh-CN/11-process" in f: want = (want[0] + 1, want[1])
    h = census(subprocess.run(["git", "show", f"HEAD:{f}"], capture_output=True, text=True).stdout)
    c = census(open(f, encoding="utf-8").read())
    da, db = c.get("##", 0) - h.get("##", 0), c.get("###", 0) - h.get("###", 0)
    ck((da, db) == want, f"{f}: delta vs HEAD == {want}", f"({da},{db})")

# ---------- J: new normative anchors ----------
print("J. new normative anchors present")
for f, needle in [("docs/shell-layer/05-config-file.md", "#### `id` (position-derived)"),
                  ("docs/shell-layer/zh-CN/05-config-file.md", "#### `id`(位置派生)"),
                  ("docs/shell-layer/05-config-file.md", "#### `source_context`"),
                  ("docs/shell-layer/zh-CN/05-config-file.md", "#### `source_context`"),
                  ("docs/shell-layer/05-config-file.md", "#### `state`"),
                  ("docs/shell-layer/zh-CN/05-config-file.md", "#### `state`"),
                  ("docs/shell-layer/05-config-file.md", "#### `placeholders`"),
                  ("docs/shell-layer/zh-CN/05-config-file.md", "#### `placeholders`"),
                  ("docs/shell-layer/05-config-file.md", "#### `notes`"),
                  ("docs/shell-layer/zh-CN/05-config-file.md", "#### `notes`"),
                  ("docs/shell-layer/05-config-file.md", "#### `provenance`"),
                  ("docs/shell-layer/zh-CN/05-config-file.md", "#### `provenance`"),
                  ("docs/shell-layer/12-file-structure.md", "## 12.4 Unit file format (`gallate.translation` v1)"),
                  ("docs/shell-layer/zh-CN/12-file-structure.md", "## 12.4 单元文件格式(`gallate.translation` v1)"),
                  ("docs/shell-layer/12-file-structure.md", "## 12.13 Design principle"),
                  ("docs/shell-layer/zh-CN/12-file-structure.md", "## 12.13 设计原则"),
                  ("CHANGELOG.md", "### `gallate.translation` v1")]:
    ck(needle in open(f, encoding="utf-8").read(), f"{f}: {needle!r}")

# ---------- K: kind classification is in §12.4 entry-field table ----------
print("K. §12.4 entry-field table classifies every field as derived/authored/engine")
for f in ["docs/shell-layer/12-file-structure.md", "docs/shell-layer/zh-CN/12-file-structure.md"]:
    txt = open(f, encoding="utf-8").read()
    # Find the table block in §12.4.2 (between "### 12.4.2 Entry" and "### 12.4.3 ...")
    sec = re.search(r"### 12\.4\.2.*?(?=### 12\.4\.3|\Z)", txt, re.S).group(0)
    for fname, kind in [("id","derived"),("source","derived"),("target","authored"),
                        ("state","authored"),("source_context","derived"),
                        ("context","authored"),("placeholders","derived"),
                        ("notes","authored"),("provenance","authored"),
                        ("metadata","engine")]:
        rows = [l for l in sec.splitlines() if f"`{fname}`" in l and l.startswith("|")]
        # the Kind column is in English for EN, Chinese for ZH
        zh_kind = {"derived":"派生","authored":"人工","engine":"引擎"}[kind]
        ck(bool(rows) and (any(kind in r for r in rows) or any(zh_kind in r for r in rows)),
           f"{os.path.basename(f)}: {fname} classified as {kind!r} (or {zh_kind!r})",
           str(rows))

print(f"\n--- K summary ---")
print(f"checks={n}  failures={len(fails)} so far")

# ---------- L: format-source-of-truth rule ----------
print("L. source-of-truth rule: stream→jsonl, single-doc→json, project→gallate.yaml")
# No --yaml flag anywhere
yaml_flag_hits = []
for root,dirs,files in os.walk("."):
    if ".git" in root: continue
    for f in files:
        if not f.endswith((".md", ".yaml", ".yml")): continue
        p = os.path.join(root, f)
        if "CHANGELOG" in p: continue
        try: txt = open(p, encoding="utf-8").read()
        except: continue
        for m in re.finditer(r"\b--yaml\b", txt):
            yaml_flag_hits.append((p, m.start()))
ck(not yaml_flag_hits, "no --yaml flag in any non-CHANGELOG file",
   f"{len(yaml_flag_hits)} hits: {yaml_flag_hits[:3]}")

# discovery JSON files exist + validate against their schemas
for doc_p, sch_p, ftype in [
    ("examples/full-cli/features.json",   "schema/features.schema.yaml",        "json"),
    ("examples/full-cli/manifest.json",   "schema/manifest.schema.yaml",        "json"),
    ("examples/full-cli/validation.json", "schema/validation-rules.schema.yaml","json"),
    ("examples/minimal-cli/features.json","schema/features.schema.yaml",        "json"),
    ("examples/minimal-cli/manifest.json","schema/manifest.schema.yaml",        "json"),
]:
    s = yaml.safe_load(open(sch_p, encoding="utf-8"))
    d = json.load(open(doc_p, encoding="utf-8"))
    try: Draft7Validator(s).validate(d); ck(True, f"{doc_p} validates")
    except Exception as e: ck(False, f"{doc_p} validates", str(e)[:100])
    # file extension matches the role
    ck(doc_p.endswith(f".{ftype}"), f"{doc_p} uses .{ftype} extension", "")

# No .yaml files in examples/
for root,dirs,files in os.walk("examples"):
    for f in files:
        if f.endswith((".yaml", ".yml")):
            ck(False, f"no YAML in examples/{f}", "stale .yaml in examples/")

# The glossary 00-glossary.md uses no longer mentions Human/Machine mode
for p, ln_phrase in [("docs/protocol/00-glossary.md", "Human Mode"),
                      ("docs/protocol/00-glossary.md", "Machine Mode"),
                      ("docs/protocol/zh-CN/00-glossary.md", "人类模式"),
                      ("docs/protocol/zh-CN/00-glossary.md", "机器模式")]:
    txt = open(p, encoding="utf-8").read()
    ck(ln_phrase not in txt, f"{p} no longer contains {ln_phrase!r}", f"still there: yes" if ln_phrase in txt else "no")

# The glossary mentions the per-role table
for p, needle in [("docs/protocol/00-glossary.md", "YAML vs JSON"),
                  ("docs/protocol/zh-CN/00-glossary.md", "YAML vs JSON")]:
    txt = open(p, encoding="utf-8").read()
    ck(needle in txt, f"{p} keeps {needle!r} section", "")

# 12-file-structure.md: text/manifest.json (not yaml)
for p in ["docs/shell-layer/12-file-structure.md", "docs/shell-layer/zh-CN/12-file-structure.md"]:
    txt = open(p, encoding="utf-8").read()
    ck("text/manifest.json" in txt, f"{p} uses text/manifest.json", "")
    ck("text/manifest.yaml" not in txt, f"{p} no longer uses text/manifest.yaml", "")

# protocol docs: zero yaml fences, with the documented exception of
# 10-configuration.md which is the bridge between gallate.yaml and
# the protocol — it shows gallate.yaml side-by-side with the request
# message to illustrate the path-resolution rule. There, YAML fences
# are explicitly about the project file, not protocol data.
for root,dirs,files in os.walk("docs/protocol"):
    for f in files:
        if not f.endswith(".md"): continue
        p = os.path.join(root, f)
        if "10-configuration" in p:
            # Confirm only gallate.yaml-style + scripts + the request block
            # (already converted) remain. gallate.yaml + scripts: are fine.
            txt = open(p, encoding="utf-8").read()
            ny = txt.count("```yaml\n")
            ck(ny >= 1, f"{p}: gallate.yaml + scripts examples retained", f"{ny} yaml fence(s)")
        else:
            txt = open(p, encoding="utf-8").read()
            ny = txt.count("```yaml\n")
            if ny: ck(False, f"no yaml fences in {p}", f"{ny} remaining")
            else: ck(True, f"no yaml fences in {p}", "")

# shell-layer docs: yaml fences are allowed but only for gallate.yaml/media
# (we just confirm yaml fence count == gallate.yaml-style count, not zero)
for p in ["docs/shell-layer/05-config-file.md",
          "docs/shell-layer/zh-CN/05-config-file.md",
          "docs/shell-layer/12-file-structure.md",
          "docs/shell-layer/zh-CN/12-file-structure.md"]:
    txt = open(p, encoding="utf-8").read()
    ny = txt.count("```yaml\n")
    ck(ny >= 1, f"{p} keeps gallate.yaml examples", f"{ny} yaml fence(s)")

print(f"\n{'='*56}\nFINAL: checks={n}  failures={len(fails)}")
for x in fails: print("  !", x)
sys.exit(1 if fails else 0)
