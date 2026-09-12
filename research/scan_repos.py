"""GitHub 저장소 후보에서 Power BI 파일(.pbix/.pbit/.pbip, PBIR visual.json)을 찾는다.

API 한도를 피하려고 저장소마다 '파일 목록만' 받는 clone(--filter=blob:none --no-checkout --depth 1)을 한다.
파일 내용은 받지 않으므로 빠르다. clone은 research/collected/_scan/ 에 남겨 두고,
나중에 고른 파일만 `git checkout HEAD -- <경로>`로 내려받는다.

입력: candidates_search.json   출력: inventory.json
"""
import concurrent.futures as cf
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
SCAN_DIR = HERE / "collected" / "_scan"
GIT = ["git", "-c", "core.longpaths=true", "-c", "core.quotepath=false"]


def scan(name: str) -> tuple[str, dict]:
    d = SCAN_DIR / name.replace("/", "__")
    if not (d / ".git").exists():
        r = subprocess.run(GIT + ["clone", "-q", "--filter=blob:none", "--no-checkout", "--depth", "1",
                                  f"https://github.com/{name}.git", str(d)],
                           capture_output=True, text=True, timeout=180)
        if r.returncode:
            return name, {"error": r.stderr.strip()[-200:]}
    # 주의: `ls-tree -l`(크기 표시)은 partial clone에서 파일 내용을 하나씩 전부 내려받게 만든다.
    # 크기 없이 목록과 blob 해시만 읽는다 (해시가 같으면 같은 파일 → 정확한 중복 제거).
    out = subprocess.run(GIT + ["-C", str(d), "ls-tree", "-r", "HEAD"],
                         capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout
    res = {"pbix": [], "pbit": [], "pbip": [], "report_dirs": set(), "visual_json": 0, "images": 0, "license_file": False}
    for line in out.splitlines():
        if "\t" not in line:
            continue
        meta, path = line.split("\t", 1)
        parts = meta.split()
        sha = parts[2] if len(parts) > 2 else ""
        low = path.lower()
        if low.endswith(".pbix"):
            res["pbix"].append([path, sha])
        elif low.endswith(".pbit"):
            res["pbit"].append([path, sha])
        elif low.endswith(".pbip"):
            res["pbip"].append([path, sha])
        elif low.endswith("/visual.json"):
            res["visual_json"] += 1
        elif low.endswith((".png", ".jpg", ".jpeg", ".gif", ".webp")):
            res["images"] += 1
        if ".report/" in low:
            res["report_dirs"].add(path[: low.index(".report/") + len(".report")])
        if "/" not in path and low.startswith(("license", "licence", "copying")):
            res["license_file"] = True
    res["report_dirs"] = sorted(res["report_dirs"])
    res["branch"] = subprocess.run(GIT + ["-C", str(d), "rev-parse", "--abbrev-ref", "HEAD"],
                                   capture_output=True, text=True).stdout.strip() or "main"
    return name, res


def main() -> None:
    SCAN_DIR.mkdir(parents=True, exist_ok=True)
    cands = json.load(open(HERE / "candidates_search.json", encoding="utf-8"))
    inv_path = HERE / "inventory.json"
    inv = json.load(open(inv_path, encoding="utf-8")) if inv_path.exists() else {}
    todo = [n for n in cands if n not in inv]
    print(f"후보 {len(cands)}개, 남은 스캔 {len(todo)}개", flush=True)
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(scan, n): n for n in todo}
        for i, f in enumerate(cf.as_completed(futs), 1):
            n = futs[f]
            try:
                name, res = f.result()
            except Exception as e:  # 타임아웃 등
                name, res = n, {"error": str(e)[-200:]}
            inv[name] = {**cands[name], **res}
            if i % 25 == 0:
                json.dump(inv, open(inv_path, "w", encoding="utf-8"), ensure_ascii=False)
                print(f"{i}/{len(todo)}", flush=True)
    json.dump(inv, open(inv_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    hits = {k: v for k, v in inv.items() if v.get("pbix") or v.get("pbit") or v.get("pbip") or v.get("report_dirs")}
    print(f"완료: Power BI 파일이 있는 저장소 {len(hits)}개 / "
          f"PBIX {sum(len(v.get('pbix', [])) for v in hits.values())} · "
          f"PBIT {sum(len(v.get('pbit', [])) for v in hits.values())} · "
          f"PBIP {sum(len(v.get('pbip', [])) for v in hits.values())}", flush=True)


if __name__ == "__main__":
    sys.exit(main())
