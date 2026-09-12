"""inventory.json에서 Power BI 파일을 골라 실제로 내려받는다.

- PBIX/PBIT: raw.githubusercontent.com 주소로 크기를 먼저 확인(HEAD)하고 상한 이하만 내려받는다.
  API를 쓰지 않으므로 GitHub API 한도와 무관하다. Git LFS 파일은 media 주소로 다시 받는다.
- 중복 제거: git blob 해시가 같으면 같은 파일 → 한 번만 받는다 (포트폴리오 저장소에 MS 샘플 사본이 많다)
- .Report 폴더(PBIP·PBIR): 텍스트라 작으므로 스캔용 clone에서 해당 폴더만 checkout 한다
- 결과: research/collected/files/<저장소>/<원래 경로>, fetched.json (출처·라이선스·크기 기록)

사용법: python fetch_files.py [--max-mb 80] [--budget-gb 15]
"""
import argparse
import concurrent.futures as cf
import json
import subprocess
import threading
import urllib.parse
import urllib.request
from pathlib import Path

HERE = Path(__file__).parent
FILES_DIR = HERE / "collected" / "files"
SCAN_DIR = HERE / "collected" / "_scan"
GIT = ["git", "-c", "core.longpaths=true", "-c", "core.quotepath=false"]
UA = {"User-Agent": "pbi-design-research"}
# 라이브러리의 테스트 자료처럼 디자인과 무관한 PBIX가 모인 폴더
SKIP_SEGMENTS = ("/test/", "/tests/", "/testdata/", "/test_data/", "/fixtures/", "/__tests__/", "/testfiles/")
lock = threading.Lock()


def raw_url(repo: str, branch: str, path: str, media: bool = False) -> str:
    host = "https://media.githubusercontent.com/media" if media else "https://raw.githubusercontent.com"
    return f"{host}/{repo}/{branch}/{urllib.parse.quote(path)}"


def head_size(url: str) -> int:
    req = urllib.request.Request(url, headers=UA, method="HEAD")
    with urllib.request.urlopen(req, timeout=60) as r:
        return int(r.headers.get("Content-Length") or 0)


def download(url: str, dest: Path) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=600) as r, open(dest, "wb") as f:
        n = 0
        while chunk := r.read(1 << 20):
            f.write(chunk)
            n += len(chunk)
    return n


def fetch_one(repo: str, branch: str, path: str, max_bytes: int) -> dict:
    url = raw_url(repo, branch, path)
    size = head_size(url)
    if size < 1024:  # LFS 포인터(작은 텍스트)일 가능성 → media 주소로
        url = raw_url(repo, branch, path, media=True)
        size = head_size(url)
    if size > max_bytes:
        return {"path": path, "skipped": f"{size / 1024 ** 2:.0f}MB > 상한"}
    dest = FILES_DIR / repo.replace("/", "__") / path
    n = dest.stat().st_size if dest.exists() and dest.stat().st_size == size else download(url, dest)
    return {"path": path, "bytes": n}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-mb", type=float, default=40, help="파일당 상한. 큰 파일은 데이터가 많을 뿐 디자인과 무관")
    ap.add_argument("--budget-gb", type=float, default=15)
    ap.add_argument("--per-repo", type=int, default=4, help="저장소당 PBIX/PBIT 최대 개수")
    ap.add_argument("--dry-run", action="store_true", help="무엇을 받을지만 보여 주고 끝낸다")
    ap.add_argument("--only-curated", action="store_true",
                    help="직접 고른 출처(MS 공식 샘플 등)만, 저장소당 개수 제한 없이 받는다")
    args = ap.parse_args()
    max_bytes, budget = int(args.max_mb * 1024 ** 2), args.budget_gb * 1024 ** 3
    inv = json.load(open(HERE / "inventory.json", encoding="utf-8"))

    # 우선순위: 스크린샷 이미지가 있는 저장소(포트폴리오일 가능성↑) → 별 많은 순. 같은 파일은 먼저 나온 쪽을 원본으로.
    order = sorted(inv.items(), key=lambda kv: (kv[1].get("images", 0) == 0, -kv[1].get("stars", 0)))
    seen, jobs, report_dirs = set(), [], {}
    for repo, v in order:
        if "error" in v:
            continue
        curated = v.get("query") == "curated"
        if args.only_curated and not curated:
            continue
        # 개수 제한은 라이브러리 테스트 자료를 거르려는 것 — 직접 고른 출처(MS 공식 샘플 등)에는 적용하지 않는다
        cap = None if curated else args.per_repo
        picked = 0
        for path, sha in v.get("pbix", []) + v.get("pbit", []):
            low = "/" + path.lower()
            if sha in seen or any(seg in low for seg in SKIP_SEGMENTS):
                continue
            if cap is not None and picked >= cap:
                break
            seen.add(sha)
            picked += 1
            jobs.append((repo, v.get("branch") or "main", path))
        if v.get("report_dirs") and not args.only_curated:  # .Report 폴더는 본 실행에서 이미 받는다
            report_dirs[repo] = v["report_dirs"]
    print(f"PBIX/PBIT 고유 파일 {len(jobs)}개, .Report 폴더가 있는 저장소 {len(report_dirs)}개", flush=True)
    if args.dry_run:
        repos = {r for r, _, _ in jobs}
        print(f"대상 저장소 {len(repos)}개 (스크린샷 이미지 있는 저장소 "
              f"{sum(1 for r in repos if inv[r].get('images', 0) > 0)}개)")
        return

    fetched, total = {}, 0
    with cf.ThreadPoolExecutor(max_workers=8) as ex:
        futs = {ex.submit(fetch_one, r, b, p, max_bytes): (r, p) for r, b, p in jobs}
        for i, f in enumerate(cf.as_completed(futs), 1):
            repo, path = futs[f]
            try:
                res = f.result()
            except Exception as e:
                res = {"path": path, "error": str(e)[:150]}
            with lock:
                total += res.get("bytes", 0)
                v = inv[repo]
                entry = fetched.setdefault(repo, {"stars": v.get("stars"), "license": v.get("license"),
                                                  "license_file": v.get("license_file"),
                                                  "url": f"https://github.com/{repo}", "files": []})
                entry["files"].append(res)
            if i % 50 == 0:
                print(f"{i}/{len(jobs)}  누적 {total / 1024 ** 3:.2f} GB", flush=True)
            if total > budget:
                print("용량 상한 도달 — 남은 작업 취소", flush=True)
                ex.shutdown(cancel_futures=True)
                break

    for repo, dirs in report_dirs.items():  # PBIP/PBIR 폴더
        d = SCAN_DIR / repo.replace("/", "__")
        r = subprocess.run(GIT + ["-C", str(d), "checkout", "HEAD", "--"] + dirs,
                           capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=900)
        v = inv[repo]
        fetched.setdefault(repo, {"stars": v.get("stars"), "license": v.get("license"),
                                  "license_file": v.get("license_file"), "url": f"https://github.com/{repo}", "files": []})
        fetched[repo]["report_dirs"] = {"paths": dirs, "error": r.stderr.strip()[-200:] if r.returncode else ""}

    out_name = "fetched_curated.json" if args.only_curated else "fetched.json"
    json.dump(fetched, open(HERE / out_name, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    ok = sum(1 for v in fetched.values() for f in v["files"] if "bytes" in f)
    print(f"완료: PBIX/PBIT {ok}개 ({total / 1024 ** 3:.2f} GB), .Report 폴더 저장소 {len(report_dirs)}개", flush=True)


if __name__ == "__main__":
    main()
