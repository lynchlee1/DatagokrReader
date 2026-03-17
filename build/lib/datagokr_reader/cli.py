from __future__ import annotations

import argparse
import json
import sys

from datagokr_reader.workflow import run_bond_workflow


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="datagokr-reader")
    parser.add_argument("--api-key", required=True, help="data.go.kr serviceKey")
    parser.add_argument("--bond-name", required=True, help="채권명 (띄어쓰기/대소문자 무관)")
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty JSON 출력",
    )
    args = parser.parse_args(argv)

    result = run_bond_workflow(args.api_key, args.bond_name)
    if args.pretty:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))

