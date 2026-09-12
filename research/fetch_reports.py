""".Report 폴더(PBIP·PBIR)를 파일 단위로 내려받는다.

처음에는 스캔용 partial clone에서 `git checkout HEAD -- <폴더>`로 받았지만, 77개 저장소 모두
`cannot create directory ... Directory not empty`로 도중에 멈춰 폴더가 비거나 일부만 받아졌다.
그래서 git으로 풀어 쓰지 않고, 파일 목록(ls-tree, 내용 없이)만 git에서 읽고
각 파일은 raw.githubusercontent.com에서 받는다. 텍스트 파일이라 작다.

결과: research/collected/files/<저장소>/<원래 경로> (PBIX와 같은 위치 규칙)
사용법: python fetch_reports.py [--max-files 3000]
"""
import argparse
import concurrent.futures as cf
import json
import subprocess

from fetch_files import FILES_DIR, GIT, HERE, SCAN_DIR, download, raw_url

KEEP_EXT = (".json", ".pbir", ".pbip", ".platform")  # 디자인 분석에 필요한 것만 (이미지·커스텀 비주얼 제외)


def list_files(repo: str, dirs: list[str]) -> list[str]:
    d = SCAN_DIR / repo.replace("/", "__")
    out = subprocess.run(GIT + ["-C", str(d), "ls-tree", "-r", "--name-only", "HEAD", "--"] + dirs,
                         capture_output=True, text=True, encoding="utf-8", errors="ignore").stdout
    return [p for p in out.splitlines() if p.lower().endswith(KEEP_EXT) and "/customvisuals/" not in p.lower()]


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-files", type=int, default=3000, help="저장소당 파일 수 상한 (테스트 자료 과다 방지)")
    args = ap.parse_args()
    inv = json.load(open(HERE / "inventory.json", encoding="utf-8"))
    jobs = []
    for repo, v in inv.items():
        if v.get("report_dirs") and "error" not in v:
            files = list_files(repo, v["report_dirs"])[: args.max_files]
            jobs += [(repo, v.get("branch") or "main", p) for p in files]
    print(f".Report 파일 {len(jobs)}개 내려받기", flush=True)

    ok = fail = 0
    with cf.ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(download, raw_url(r, b, p), FILES_DIR / r.replace("/", "__") / p): (r, p) for r, b, p in jobs}
        for i, f in enumerate(cf.as_completed(futs), 1):
            try:
                f.result()
                ok += 1
            except Exception:
                fail += 1
            if i % 1000 == 0:
                print(f"{i}/{len(jobs)}", flush=True)
    print(f"완료: 성공 {ok}개, 실패 {fail}개", flush=True)


if __name__ == "__main__":
    main()
