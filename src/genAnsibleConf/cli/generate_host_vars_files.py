#!/usr/bin/env python3
# -*- mode: python; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
#
# Copyright (c) 2025 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。

"""host_vars_structured.yaml から host_vars ファイル群を生成する。

このスクリプトは, host_vars_structured.yaml を入力に, 指定ディレクトリへ
ホストごとの host_vars ファイルを生成する。出力時は各項目の直前に
field_metadata.yaml の説明をコメントとして挿入する。

コメント形式:
- ``# <key>: <description>``
- 1行 80 文字以内に折り返す。

description が見つからない項目は, ``(description missing)`` を出力する。
"""

from __future__ import annotations

import argparse
import sys
import textwrap
from pathlib import Path
from typing import Any, cast

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from genAnsibleConf.lib.cli_defaults import (
    DEFAULT_FIELD_METADATA,
    DEFAULT_HOST_VARS_STRUCTURED,
    resolve_schema_file,
)
from genAnsibleConf.lib.yaml_io import (
    load_yaml_file,
    load_yaml_mapping,
    yaml_value_to_string,
)


def load_yaml(file_path: Path) -> dict[str, Any]:
    """YAML ファイルを読み込む。

    Args:
        file_path (Path): 読み込み対象 YAML のパス。

    Returns:
        dict[str, Any]: 読み込み結果。

    Raises:
        FileNotFoundError: ファイルが存在しない場合。
        ValueError: YAML のトップレベルが dict でない場合。
    """
    return load_yaml_mapping(file_path)


def normalize_path(path: str) -> str:
    """配列インデックスを除去した正規化パスを返す。

    Args:
        path (str): 変換対象の YAML パス。

    Returns:
        str: ``[<number>]`` を除去したパス。
    """
    result: list[str] = []
    idx: int = 0
    while idx < len(path):
        char: str = path[idx]
        if char == "[":
            end: int = path.find("]", idx)
            if end != -1:
                token: str = path[idx + 1 : end]
                if token.isdigit():
                    idx = end + 1
                    continue
        result.append(char)
        idx += 1
    return "".join(result)


def extract_leaf_name(path: str) -> str:
    """YAML パスから末尾キー名を抽出する。

    Args:
        path (str): YAML パス。

    Returns:
        str: 末尾キー名。
    """
    no_index: str = normalize_path(path)
    if "." in no_index:
        return no_index.split(".")[-1]
    return no_index


def build_metadata_indices(
    metadata: dict[str, Any],
) -> tuple[dict[str, str], dict[str, str]]:
    """field_metadata の説明索引を構築する。

    Args:
        metadata (dict[str, Any]): field_metadata.yaml の内容。

    Returns:
        tuple[dict[str, str], dict[str, str]]:
            - ``description_by_key``: ``fields.<key>.description`` の索引。
            - ``description_by_path``: ``fields.<key>.yaml_path`` の索引。
    """
    raw_fields: Any = metadata.get("fields", {})
    fields: dict[str, Any] = (
        cast(dict[str, Any], raw_fields) if isinstance(raw_fields, dict) else {}
    )

    description_by_key: dict[str, str] = {}
    description_by_path: dict[str, str] = {}

    for key, entry in fields.items():
        if not isinstance(entry, dict):
            continue
        typed_entry: dict[str, Any] = cast(dict[str, Any], entry)

        description: str = str(typed_entry.get("description", "")).strip()
        if description:
            description_by_key[key] = description

        yaml_path: str = str(typed_entry.get("yaml_path", "")).strip()
        if yaml_path and description:
            description_by_path[yaml_path] = description

    return description_by_key, description_by_path


def resolve_description(
    path: str,
    key: str,
    description_by_key: dict[str, str],
    description_by_path: dict[str, str],
) -> str:
    """YAML パスに対する説明文を解決する。

    解決順序:
    1. ``yaml_path`` 完全一致
    2. ``normalize_path(path)`` 一致
    3. ``scalars.<key>`` の ``<key>`` 一致
    4. 末尾キー名一致
    5. フォールバック

    Args:
        path (str): 項目の YAML パス。
        key (str): 出力キー名。
        description_by_key (dict[str, str]): キー名索引。
        description_by_path (dict[str, str]): YAML パス索引。

    Returns:
        str: 解決した説明文。見つからない場合は ``(description missing)``。
    """
    if path in description_by_path:
        return description_by_path[path]

    normalized: str = normalize_path(path)
    if normalized in description_by_path:
        return description_by_path[normalized]

    if path.startswith("scalars."):
        scalar_key: str = path.split(".", 1)[1]
        if scalar_key in description_by_key:
            return description_by_key[scalar_key]

    if key in description_by_key:
        return description_by_key[key]

    leaf_name: str = extract_leaf_name(path)
    if leaf_name in description_by_key:
        return description_by_key[leaf_name]

    return "(description missing)"


def wrap_comment_lines(key: str, description: str, width: int = 80) -> list[str]:
    """コメント文字列を 80 文字以内で折り返す。

    Args:
        key (str): コメントに表示するキー名。
        description (str): 説明文。
        width (int): 1行の最大文字数。

    Returns:
        list[str]: ``# `` プレフィックス付きコメント行の配列。
    """
    raw_text: str = f"{key}: {description}"
    wrapped: list[str] = textwrap.wrap(
        raw_text,
        width=max(1, width - 2),
        break_long_words=True,
        break_on_hyphens=False,
    )
    if not wrapped:
        return ["#"]
    return [f"# {line}" for line in wrapped]


def format_scalar(value: Any) -> str:
    """YAML スカラーを 1 行文字列に整形する。

    Args:
        value (Any): スカラー値。

    Returns:
        str: YAML として有効な 1 行表現。
    """
    return yaml_value_to_string(value)


def write_value(
    lines: list[str],
    value: Any,
    indent: int,
    path: str,
    display_key: str,
    description_by_key: dict[str, str],
    description_by_path: dict[str, str],
) -> None:
    """値をコメント付きで YAML 行に変換する。

    Args:
        lines (list[str]): 出力行のバッファ。
        value (Any): 出力対象値。
        indent (int): インデント幅。
        path (str): 現在値の YAML パス。
        display_key (str): コメント用キー名。
        description_by_key (dict[str, str]): キー名索引。
        description_by_path (dict[str, str]): YAML パス索引。
    """
    if isinstance(value, dict):
        description: str = resolve_description(
            path,
            display_key,
            description_by_key,
            description_by_path,
        )
        for comment_line in wrap_comment_lines(display_key, description):
            lines.append(f"{' ' * indent}{comment_line}")

        typed_dict: dict[str, Any] = cast(dict[str, Any], value)
        if not typed_dict:
            lines.append(f"{' ' * indent}{display_key}: {{}}")
            return
        lines.append(f"{' ' * indent}{display_key}:")
        for child_key, child_value in typed_dict.items():
            child_path: str = f"{path}.{child_key}"
            write_value(
                lines,
                child_value,
                indent + 2,
                child_path,
                str(child_key),
                description_by_key,
                description_by_path,
            )
        return

    if isinstance(value, list):
        description: str = resolve_description(
            path,
            display_key,
            description_by_key,
            description_by_path,
        )
        for comment_line in wrap_comment_lines(display_key, description):
            lines.append(f"{' ' * indent}{comment_line}")

        typed_list: list[Any] = cast(list[Any], value)
        if not typed_list:
            lines.append(f"{' ' * indent}{display_key}: []")
            return
        lines.append(f"{' ' * indent}{display_key}:")
        for index, item in enumerate(typed_list):
            item_path: str = f"{path}[{index}]"
            if isinstance(item, dict):
                typed_item_dict: dict[str, Any] = cast(dict[str, Any], item)
                if not typed_item_dict:
                    lines.append(f"{' ' * (indent + 2)}- {{}}")
                    continue

                first_key, first_value = next(iter(typed_item_dict.items()))
                first_key_str: str = str(first_key)
                first_path: str = f"{item_path}.{first_key_str}"

                if not isinstance(first_value, (dict, list)):
                    first_desc: str = resolve_description(
                        first_path,
                        first_key_str,
                        description_by_key,
                        description_by_path,
                    )
                    lines.append(
                        f"{' ' * (indent + 2)}- {first_key_str}: {format_scalar(first_value)}"
                        f"  # {first_desc}"
                    )

                    remaining_items: list[tuple[Any, Any]] = list(typed_item_dict.items())[1:]
                    for child_key, child_value in remaining_items:
                        child_path = f"{item_path}.{child_key}"
                        write_value(
                            lines,
                            child_value,
                            indent + 4,
                            child_path,
                            str(child_key),
                            description_by_key,
                            description_by_path,
                        )
                else:
                    lines.append(f"{' ' * (indent + 2)}-")
                    for child_key, child_value in typed_item_dict.items():
                        child_path = f"{item_path}.{child_key}"
                        write_value(
                            lines,
                            child_value,
                            indent + 4,
                            child_path,
                            str(child_key),
                            description_by_key,
                            description_by_path,
                        )
            elif isinstance(item, list):
                nested_key: str = f"{display_key}[{index}]"
                write_value(
                    lines,
                    item,
                    indent + 2,
                    item_path,
                    nested_key,
                    description_by_key,
                    description_by_path,
                )
            else:
                item_label: str = f"{display_key}[{index}]"
                item_desc: str = resolve_description(
                    item_path,
                    item_label,
                    description_by_key,
                    description_by_path,
                )
                lines.append(
                    f"{' ' * (indent + 2)}- {format_scalar(item)}"
                    f"  # {item_desc}"
                )
        return

    description: str = resolve_description(
        path,
        display_key,
        description_by_key,
        description_by_path,
    )
    lines.append(
        f"{' ' * indent}{display_key}: {format_scalar(value)}"
        f"  # {description}"
    )


def compose_host_var_data(host_entry: dict[str, Any]) -> dict[str, Any]:
    """structured host エントリを host_vars 向けに整形する。

    ``hostname`` は出力対象外。``scalars`` はトップレベルへ展開し,
    その他キーは元の順序で維持して追加する。

    Args:
        host_entry (dict[str, Any]): hosts[] の1要素。

    Returns:
        dict[str, Any]: host_vars 出力向けデータ。
    """
    result: dict[str, Any] = {}

    scalars: Any = host_entry.get("scalars", {})
    if isinstance(scalars, dict):
        typed_scalars: dict[str, Any] = cast(dict[str, Any], scalars)
        for key, value in typed_scalars.items():
            result[str(key)] = value

    for key, value in host_entry.items():
        if key in {"hostname", "scalars"}:
            continue
        result[str(key)] = value

    return result

def render_host_vars_header(host_entry: dict[str, Any]) -> list[str]:
    """host_vars ファイルのヘッダコメントを生成する。

    Args:
        host_entry (dict[str, Any]): hosts[] の1要素。

    Returns:
        list[str]: ヘッダコメント行の配列。
    """
    hostname: str = str(host_entry.get("hostname", "")).strip()
    if not hostname:
        return ["# (hostname missing)"]

    header: list[str] = [
        "#",
        f"# Host variables for {hostname}",
        f"# {hostname} のホスト固有変数定義",
        "# This file is automatically generated from host_vars_structured.yaml.",
        "# Do not edit this file directly.",
        "# これは host_vars_structured.yaml から自動生成されたファイルです。",
        "# 直接編集しないでください。",
        "#",
        "---",
        "",
    ]
    return header

def render_host_vars_content(
    host_entry: dict[str, Any],
    description_by_key: dict[str, str],
    description_by_path: dict[str, str],
) -> str:
    """1ホスト分の host_vars ファイル内容を生成する。

    Args:
        host_entry (dict[str, Any]): hosts[] の1要素。
        description_by_key (dict[str, str]): キー名索引。
        description_by_path (dict[str, str]): YAML パス索引。

    Returns:
        str: 生成された YAML テキスト。
    """
    host_data: dict[str, Any] = compose_host_var_data(host_entry)

    lines: list[str] = render_host_vars_header(host_entry)
    for key, value in host_data.items():
        path: str = f"scalars.{key}" if key in host_entry.get("scalars", {}) else key
        display_key: str = str(key)
        write_value(
            lines,
            value,
            0,
            path,
            display_key,
            description_by_key,
            description_by_path,
        )

    return "\n".join(lines) + "\n"


def generate_host_var_files(
    input_structured: Path,
    metadata_file: Path,
    output_dir: Path,
    overwrite: bool,
) -> list[dict[str, Any]]:
    """host_vars ファイル群を生成する。

    Args:
        input_structured (Path): host_vars_structured.yaml のパス。
        metadata_file (Path): field_metadata.yaml のパス。
        output_dir (Path): 生成先ディレクトリ。
        overwrite (bool): 既存ファイル上書き可否。

    Raises:
        ValueError: hosts 配列の形式不正時。
        FileExistsError: overwrite=False かつ既存ファイル衝突時。

    Returns:
        list[dict[str, Any]]: 生成対象として処理した hosts エントリ一覧。
    """
    structured: dict[str, Any] = load_yaml(input_structured)
    metadata: dict[str, Any] = load_yaml(metadata_file)

    hosts: Any = structured.get("hosts", [])
    if not isinstance(hosts, list):
        raise ValueError("'hosts' must be a list in host_vars_structured.yaml")

    description_by_key, description_by_path = build_metadata_indices(metadata)

    output_dir.mkdir(parents=True, exist_ok=True)

    generated_count: int = 0
    typed_hosts: list[Any] = cast(list[Any], hosts)
    for host_entry in typed_hosts:
        if not isinstance(host_entry, dict):
            continue
        typed_host_entry: dict[str, Any] = cast(dict[str, Any], host_entry)
        hostname: str = str(typed_host_entry.get("hostname", "")).strip()
        if not hostname:
            continue

        output_file: Path = output_dir / hostname
        if output_file.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {output_file}")

        content: str = render_host_vars_content(
            typed_host_entry,
            description_by_key,
            description_by_path,
        )
        output_file.write_text(content, encoding="utf-8")
        generated_count += 1

    print(f"Generated {generated_count} host_vars files under: {output_dir}")

    processed_hosts: list[dict[str, Any]] = []
    for host_entry in typed_hosts:
        if not isinstance(host_entry, dict):
            continue
        typed_host_entry = cast(dict[str, Any], host_entry)
        hostname = str(typed_host_entry.get("hostname", "")).strip()
        if hostname:
            processed_hosts.append(typed_host_entry)
    return processed_hosts


def validate_roundtrip(
    output_dir: Path,
    host_entries: list[dict[str, Any]],
) -> tuple[bool, list[str]]:
    """生成後の host_vars を再読込し, 元データと比較する。

    Args:
        output_dir (Path): 生成済み host_vars ディレクトリ。
        host_entries (list[dict[str, Any]]): host_vars_structured 由来の hosts。

    Returns:
        tuple[bool, list[str]]: 検証結果とエラーメッセージ一覧。
    """
    def collect_diffs(
        expected_value: Any,
        actual_value: Any,
        base_path: str,
        out: list[str],
    ) -> None:
        """expected/actual の差分をパス付きで収集する。"""
        if type(expected_value) is not type(actual_value):
            out.append(
                f"{base_path}: type mismatch "
                f"expected={type(expected_value).__name__} "
                f"actual={type(actual_value).__name__}"
            )
            return

        if isinstance(expected_value, dict):
            expected_dict: dict[str, Any] = cast(dict[str, Any], expected_value)
            actual_dict: dict[str, Any] = cast(dict[str, Any], actual_value)
            expected_keys: set[str] = set(expected_dict.keys())
            actual_keys: set[str] = set(actual_dict.keys())

            missing_keys: list[str] = sorted(expected_keys - actual_keys)
            extra_keys: list[str] = sorted(actual_keys - expected_keys)
            for key in missing_keys:
                out.append(f"{base_path}.{key}: missing key in generated file")
            for key in extra_keys:
                out.append(f"{base_path}.{key}: unexpected extra key in generated file")

            for key in sorted(expected_keys & actual_keys):
                child_path: str = f"{base_path}.{key}"
                collect_diffs(expected_dict[key], actual_dict[key], child_path, out)
            return

        if isinstance(expected_value, list):
            expected_list: list[Any] = cast(list[Any], expected_value)
            actual_list: list[Any] = cast(list[Any], actual_value)
            if len(expected_list) != len(actual_list):
                out.append(
                    f"{base_path}: list length mismatch "
                    f"expected={len(expected_list)} actual={len(actual_list)}"
                )
                return

            for index, item in enumerate(expected_list):
                child_path = f"{base_path}[{index}]"
                collect_diffs(item, actual_list[index], child_path, out)
            return

        if expected_value != actual_value:
            out.append(
                f"{base_path}: value mismatch expected={expected_value!r} "
                f"actual={actual_value!r}"
            )

    errors: list[str] = []

    for host_entry in host_entries:
        hostname: str = str(host_entry.get("hostname", "")).strip()
        if not hostname:
            continue

        expected: dict[str, Any] = compose_host_var_data(host_entry)
        output_file: Path = output_dir / hostname
        if not output_file.exists():
            errors.append(f"Missing generated file: {output_file}")
            continue

        try:
            parsed = load_yaml_file(output_file)
        except Exception as exc:
            errors.append(f"YAML parse failed ({output_file}): {exc}")
            continue

        if parsed is None:
            parsed_dict: dict[str, Any] = {}
        elif isinstance(parsed, dict):
            parsed_dict = cast(dict[str, Any], parsed)
        else:
            errors.append(f"Top-level YAML is not dict: {output_file}")
            continue

        if parsed_dict != expected:
            host_diffs: list[str] = []
            collect_diffs(expected, parsed_dict, "root", host_diffs)
            errors.append(
                f"Roundtrip mismatch: {hostname} "
                f"(diff_count={len(host_diffs)})"
            )
            for detail in host_diffs[:100]:
                errors.append(f"  {detail}")
            if len(host_diffs) > 100:
                errors.append(
                    f"  ... truncated {len(host_diffs) - 100} additional diffs"
                )

    return len(errors) == 0, errors


def parse_args() -> argparse.Namespace:
    """CLI 引数を解析する。

    Returns:
        argparse.Namespace: 解析済み引数。
    """
    parser = argparse.ArgumentParser(
        description=(
            "Generate host_vars files from host_vars_structured.yaml with "
            "metadata comments wrapped at 80 chars."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "output_dir",
        help="Output directory for generated host_vars files",
    )
    parser.add_argument(
        "-i", "--input-structured",
        default=DEFAULT_HOST_VARS_STRUCTURED,
        help="Path to host_vars_structured.yaml",
    )
    parser.add_argument(
        "-m", "--metadata",
        default=DEFAULT_FIELD_METADATA,
        help="Path to field_metadata.yaml",
    )
    parser.add_argument(
        "--schema-dir",
        default=None,
        help="Directory to search schema/config YAML files with highest priority",
    )
    parser.add_argument(
        "-w", "--overwrite",
        choices=["true", "false"],
        default="true",
        help="Whether to overwrite existing files (true/false)",
    )
    parser.add_argument(
        "-v", "--validate-roundtrip",
        choices=["true", "false"],
        default="false",
        help="Validate generated files by reloading and comparing with source data",
    )

    return parser.parse_args()


def main() -> None:
    """エントリポイント。"""
    args: argparse.Namespace = parse_args()
    metadata_file: Path = Path(args.metadata)
    if metadata_file == Path(DEFAULT_FIELD_METADATA):
        metadata_file = resolve_schema_file(DEFAULT_FIELD_METADATA, args.schema_dir)

    host_entries: list[dict[str, Any]] = generate_host_var_files(
        input_structured=Path(args.input_structured),
        metadata_file=metadata_file,
        output_dir=Path(args.output_dir),
        overwrite=(args.overwrite == "true"),
    )

    if args.validate_roundtrip == "true":
        ok: bool
        errors: list[str]
        ok, errors = validate_roundtrip(Path(args.output_dir), host_entries)
        if not ok:
            for error in errors:
                print(f"Roundtrip validation error: {error}")
            raise SystemExit(1)
        print("Roundtrip validation passed")


if __name__ == "__main__":
    main()
