"""PBIR 형식으로 저장된 PBIX/PBIT에서 리포트 폴더(.Report)를 꺼낸다. Desktop이 필요 없다.

최근 Desktop이 저장한 PBIX는 안쪽 리포트가 이미 PBIR 형식이다(zip 안에 Report/definition/ 폴더).
이 경우 zip을 풀기만 하면 PBIP의 .Report 폴더와 같은 파일(page.json, visual.json, 테마)이 나온다.
구형(Report/Layout 한 파일) PBIX는 Desktop에서 열어 PBIP로 저장해야 하므로 여기서는 건너뛴다.

결과: research/collected/pbip/<저장소>__<파일명>.Report/
  - definition/...            (페이지·비주얼 JSON)
  - StaticResources/...       (테마, 이미지)
  - definition.pbir           (모델 연결 정보 대신 출처 메모. 연구용이라 Desktop에서 열리지 않는다)

사용법: python extract_pbir.py <PBIX/PBIT 파일 또는 폴더>...
"""
import json
import re
import sys
import zipfile
from pathlib import Path

HERE = Path(__file__).parent
OUT = HERE / "collected" / "pbip"


def extract(src: Path) -> str:
    with zipfile.ZipFile(src) as z:
        names = [n for n in z.namelist() if n.startswith("Report/definition/") or n.startswith("Report/StaticResources/")]
        if not any(n.startswith("Report/definition/") for n in names):
            return "건너뜀 (구형 Layout 형식)"
        repo = src.parent.relative_to(HERE / "collected" / "files").parts[0] if "files" in src.parts else "local"
        name = re.sub(r"[^\w가-힣.-]+", "_", f"{repo}__{src.stem}")[:120]
        dest = OUT / f"{name}.Report"
        for n in names:
            if n.endswith("/"):
                continue
            target = dest / n[len("Report/"):]
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(z.read(n))
        (dest / "definition.pbir").write_text(json.dumps(
            {"$comment": f"연구용 추출본. 원본: {src.as_posix()}", "version": "4.0"}, ensure_ascii=False, indent=2),
            encoding="utf-8")
        n_visuals = sum(1 for n in names if n.endswith("/visual.json"))
        return f"추출 → {dest.name} (visual.json {n_visuals}개)"


def main() -> None:
    targets = []
    for p in map(Path, sys.argv[1:]):
        targets += [q for q in p.rglob("*") if q.suffix.lower() in (".pbix", ".pbit")] if p.is_dir() else [p]
    for t in targets:
        try:
            print(f"{t.name}: {extract(t.resolve())}")
        except Exception as e:
            print(f"{t.name}: 오류 {type(e).__name__}: {e}"[:200])


if __name__ == "__main__":
    main()
