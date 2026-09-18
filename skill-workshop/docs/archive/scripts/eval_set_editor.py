"""Open or export the bundled eval JSON editor page."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import tempfile
import webbrowser

ASSET_NAME = "eval_set_editor.html"
PRELOAD_PLACEHOLDER = "/*__PRELOADED_EVALS__*/ null"


def asset_path() -> Path:
    return Path(__file__).resolve().parents[2] / "assets" / ASSET_NAME


def load_json(input_path: Path) -> object:
    try:
        return json.loads(input_path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"Input JSON not found: {input_path}") from exc
    except IsADirectoryError as exc:
        raise ValueError(f"Input path is a directory: {input_path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Input JSON is invalid: {exc.msg} (line {exc.lineno}, column {exc.colno})"
        ) from exc
    except OSError as exc:
        raise ValueError(f"Failed to read input JSON: {exc}") from exc


def _normalize_queries(items: list[object], source_name: str) -> list[dict]:
    queries: list[dict] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Input item {index} must be an object")
        query = item.get("query")
        should_trigger = item.get("should_trigger")
        if not isinstance(query, str) or not query.strip():
            raise ValueError(f"Input item {index} must include a non-empty string 'query'")
        if not isinstance(should_trigger, bool):
            raise ValueError(f"Input item {index} must include boolean 'should_trigger'")
        queries.append({"query": query, "should_trigger": should_trigger})
    if not queries:
        raise ValueError("Input eval set must not be empty")
    return [{"id": 1, "name": source_name, "queries": queries}]


def normalize_editor_payload(data: object, source_name: str) -> list[dict]:
    if not isinstance(data, list):
        raise ValueError("Input JSON must be an array")
    if not data:
        raise ValueError("Input JSON must not be empty")

    if all(
        isinstance(item, dict) and "query" in item and "should_trigger" in item for item in data
    ):
        return _normalize_queries(data, source_name)

    normalized: list[dict] = []
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(f"Eval set {index} must be an object")
        name = item.get("name")
        queries = item.get("queries")
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"Eval set {index} must include a non-empty string 'name'")
        if not isinstance(queries, list) or not queries:
            raise ValueError(f"Eval set {index} must include a non-empty 'queries' array")
        normalized_queries = []
        for q_index, query_item in enumerate(queries, start=1):
            if not isinstance(query_item, dict):
                raise ValueError(f"Eval set {index} query {q_index} must be an object")
            query = query_item.get("query")
            should_trigger = query_item.get("should_trigger")
            if not isinstance(query, str) or not query.strip():
                raise ValueError(
                    f"Eval set {index} query {q_index} must include a non-empty string 'query'"
                )
            if not isinstance(should_trigger, bool):
                raise ValueError(
                    f"Eval set {index} query {q_index} must include boolean 'should_trigger'"
                )
            normalized_queries.append({"query": query, "should_trigger": should_trigger})
        normalized.append({
            "id": index,
            "name": name,
            "queries": normalized_queries,
        })
    return normalized


def render_editor_html(preloaded_evals: list[dict] | None = None) -> str:
    template = asset_path().read_text(encoding="utf-8")
    if preloaded_evals is None:
        return template.replace(PRELOAD_PLACEHOLDER, "null", 1)
    payload = json.dumps(preloaded_evals, ensure_ascii=False)
    return template.replace(PRELOAD_PLACEHOLDER, payload, 1)


def write_editor_html(output_path: Path, preloaded_evals: list[dict] | None = None) -> Path:
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_editor_html(preloaded_evals), encoding="utf-8")
    return output_path


def open_editor(target: Path) -> None:
    webbrowser.open(target.resolve().as_uri())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Preview or export the bundled eval JSON editor page"
    )
    parser.add_argument(
        "--input",
        "-i",
        type=Path,
        default=None,
        help="Preload editor data from an eval JSON file",
    )
    parser.add_argument(
        "--static",
        "-s",
        type=Path,
        default=None,
        help="Write a standalone HTML copy to this path",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not open the editor page in a browser",
    )
    parser.add_argument(
        "--print-path",
        action="store_true",
        help="Print the source or exported HTML path",
    )
    args = parser.parse_args(argv)

    source = asset_path()
    if not source.exists():
        print(f"Error: editor asset not found: {source}", file=sys.stderr)
        return 1

    preloaded_evals = None
    if args.input is not None:
        try:
            data = load_json(args.input)
            preloaded_evals = normalize_editor_payload(data, args.input.stem)
        except ValueError as exc:
            print(f"Error: {exc}", file=sys.stderr)
            return 1

    target = source
    if args.static is not None:
        target = write_editor_html(args.static, preloaded_evals)
        print(f"Eval set editor exported to: {target}")
    elif preloaded_evals is not None:
        temp_path = Path(tempfile.mkstemp(prefix="eval-set-editor-", suffix=".html")[1])
        target = write_editor_html(temp_path, preloaded_evals)
        print(f"Eval set editor prepared with input data: {target}")

    if args.static is None and (args.print_path or args.no_open) and preloaded_evals is None:
        print(f"Eval set editor asset: {target}")
    elif args.print_path:
        print(target)

    if not args.no_open:
        open_editor(target)
        print(f"Opened eval set editor: {target}")

    return 0
