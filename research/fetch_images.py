"""품질 후보 상위 리포트가 들어 있는 저장소에서 대시보드 캡처 이미지를 받아 온다.

Desktop 없이 '눈으로 보는' 검토를 하려는 것이다. 포트폴리오 저장소는 대부분 README용 캡처를 함께 올린다.
- 후보: summaries.jsonl을 aggregate.score로 정렬한 상위 N개 리포트의 저장소
- 저장소마다 이미지 파일 이름으로 점수를 매겨 최대 3장 (dashboard·screenshot·overview 우대, logo·icon 제외)
- 결과: research/collected/images/<저장소>/..., images.json

사용법: python fetch_images.py summaries.jsonl [--top 40] [--per-repo 3]
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

from aggregate import score
from fetch_files import GIT, SCAN_DIR, UA, download, head_size, raw_url

HERE = Path(__file__).parent
IMG_DIR = HERE / "collected" / "images"
GOOD = re.compile(r"dashboard|screenshot|screen|overview|report|page|preview|summary|home|대시보드", re.I)
BAD = re.compile(r"logo|icon|badge|avatar|banner|favicon|gif$", re.I)


def repo_of(file_path: str) -> str | None:
    m = re.search(r"[/\\](?:files|_scan)[/\\]([^/\\]+__[^/\\]+)[/\\]", file_path)
    return m.group(1).replace("__", "/", 1) if m else None


def pick_images(repo: str, n: int) -> list[str]:
    d = SCAN_DIR / repo.replace("/", "__")
    names = subprocess.run(GIT + ["-C", str(d), "ls-tree", "-r", "--name-only", "HEAD"],
                           capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout.splitlines()
    imgs = [p for p in names if p.lower().endswith((".png", ".jpg", ".jpeg", ".webp")) and not BAD.search(p)]
    return sorted(imgs, key=lambda p: (not GOOD.search(p), len(p)))[:n]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("jsonl")
    ap.add_argument("--top", type=int, default=40)
    ap.add_argument("--per-repo", type=int, default=3)
    args = ap.parse_args()
    inv = json.load(open(HERE / "inventory.json", encoding="utf-8"))
    rows = [json.loads(l) for l in open(args.jsonl, encoding="utf-8") if l.strip()]
    rows = [r for r in rows if "error" not in r and r.get("visuals")]

    repos = []
    for r in sorted(rows, key=score, reverse=True):
        repo = repo_of(r["file"])
        if repo and repo not in repos and inv.get(repo, {}).get("images", 0) > 0:
            repos.append(repo)
        if len(repos) >= args.top:
            break

    result = {}
    for repo in repos:
        branch = inv[repo].get("branch") or "main"
        saved = []
        for path in pick_images(repo, args.per_repo):
            url = raw_url(repo, branch, path)
            try:
                if head_size(url) > 5 * 1024 ** 2:
                    continue
                dest = IMG_DIR / repo.replace("/", "__") / path.replace("/", "_")
                download(url, dest)
                saved.append(str(dest))
            except Exception as e:
                print(repo, path, "ERR", e)
        result[repo] = saved
        print(f"{repo}: {len(saved)}장")
    json.dump(result, open(HERE / "images.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
