"""Claude Code 세션 기록에서 특정 시간 구간의 토큰 사용량을 합산한다.

예제 하나를 만드는 데 토큰이 얼마나 들었는지 기록하려고 쓴다.
Claude Code는 대화를 ~/.claude/projects/<프로젝트>/<세션>.jsonl 에 저장하고,
응답마다 usage(입력·캐시·출력 토큰)를 남긴다.

사용법:
  python tools/token_usage.py --start 2026-09-12T04:36:55Z [--end 2026-09-12T06:00:00Z]
"""
import argparse
import datetime as dt
import json
import re
from pathlib import Path

def default_project_dir() -> Path:
    """Claude Code는 프로젝트 경로의 영문·숫자 외 문자를 '-'로 바꾼 이름의 폴더에 기록한다."""
    name = re.sub(r"[^A-Za-z0-9]", "-", str(Path.cwd()))
    return Path.home() / ".claude" / "projects" / (name[:1].lower() + name[1:])


PROJECT_DIR = default_project_dir()
FIELDS = ["input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens", "output_tokens"]


def parse_time(text: str) -> dt.datetime:
    return dt.datetime.fromisoformat(text.replace("Z", "+00:00"))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True, help="ISO 시각 (UTC, 예: 2026-09-12T04:36:55Z)")
    ap.add_argument("--end", help="ISO 시각 (생략하면 지금까지)")
    ap.add_argument("--dir", default=str(PROJECT_DIR), help="세션 jsonl 폴더")
    args = ap.parse_args()
    start = parse_time(args.start)
    end = parse_time(args.end) if args.end else dt.datetime.now(dt.timezone.utc)

    totals = dict.fromkeys(FIELDS, 0)
    seen, turns = set(), 0
    for path in Path(args.dir).glob("*.jsonl"):
        for line in path.open(encoding="utf-8", errors="ignore"):
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            msg = rec.get("message") or {}
            usage = msg.get("usage") if isinstance(msg, dict) else None
            if not usage or "timestamp" not in rec:
                continue
            if not (start <= parse_time(rec["timestamp"]) <= end):
                continue
            key = msg.get("id") or rec.get("uuid")  # 응답 하나가 여러 줄로 기록되므로 중복 제거
            if key in seen:
                continue
            seen.add(key)
            turns += 1
            for f in FIELDS:
                totals[f] += usage.get(f) or 0

    fresh_input = totals["input_tokens"] + totals["cache_creation_input_tokens"]
    print(f"구간: {start.isoformat()} ~ {end.isoformat()}")
    print(f"모델 응답 수: {turns}")
    for f in FIELDS:
        print(f"  {f:30s} {totals[f]:>12,d}")
    print(f"  {'새 입력 (input + cache 생성)':30s} {fresh_input:>12,d}")
    print(f"  {'전체 (캐시 읽기 포함)':30s} {sum(totals.values()):>12,d}")


if __name__ == "__main__":
    main()
