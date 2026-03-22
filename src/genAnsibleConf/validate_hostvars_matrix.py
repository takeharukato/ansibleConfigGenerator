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

"""
ホスト変数マトリックスCSV検証ツール。

host_vars_scalars_matrix.csvのフォーマット、一貫性、
スキーマ準拠性を検証する。
"""

import csv
import re
import sys
from typing import Any, cast

from lib.cli_defaults import (
    DEFAULT_FIELD_METADATA,
    DEFAULT_HOST_VARS_MATRIX,
    DEFAULT_HOST_VARS_STRUCTURED,
)
from lib.yaml_io import load_yaml_file

# netif_list[{IF名}].{フィールド名} 形式の展開行にマッチするパターン
_NETIF_ROW_PATTERN: re.Pattern[str] = re.compile(r"netif_list\[[^\]]+\]\..+")


def _count_expected_netif_rows(host_vars: dict[str, Any]) -> int:
    """host_varsからnetif展開行の期待数を算出する。

    全ホストのnetif_listを走査して, 一意なIF名数 × 一意なサブフィールド数を返す。

    Args:
        host_vars (dict[str, Any]): host_vars_structured.yaml の解析結果。

    Returns:
        int: netif展開行の期待数。netif_listが存在しない場合は0。

    Examples:
        >>> _count_expected_netif_rows({"hosts": []})
        0
    """
    hosts: list[Any] = host_vars.get("hosts", [])
    seen_ifs: set[str] = set()
    seen_subfields: set[str] = set()
    for host in hosts:
        if not host.get("hostname"):
            continue
        netif_list_raw: Any = host.get("netif_list", [])
        if not isinstance(netif_list_raw, list):
            continue
        netif_list: list[Any] = cast(list[Any], netif_list_raw)
        for iface in netif_list:
            if not isinstance(iface, dict):
                continue
            iface_dict: dict[str, Any] = cast(dict[str, Any], iface)
            if_name: str = str(iface_dict.get("netif", ""))
            if not if_name:
                continue
            seen_ifs.add(if_name)
            seen_subfields.update(iface_dict.keys())
    return len(seen_ifs) * len(seen_subfields)


def load_yaml(file_path: str) -> dict[str, Any]:
    """YAMLファイルを読み込む。

    Args:
        file_path (str): YAMLファイルパス。

    Returns:
        dict[str, Any]: 解析されたYAML内容。

    Raises:
        FileNotFoundError: ファイルが見つからない場合。
    """
    data: Any = load_yaml_file(file_path)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Top-level YAML must be object: {file_path}")
    return cast(dict[str, Any], data)


def validate_csv(
    csv_file: str,
    metadata_file: str,
    host_vars_file: str,
) -> tuple[bool, list[str]]:
    """ホスト変数マトリックスCSVを検証する。

    Args:
        csv_file (str): 検証対象のCSVファイルパス。
        metadata_file (str): field_metadata.yamlのパス。
        host_vars_file (str): host_vars_structured.yamlのパス。

    Returns:
        tuple[bool, list[str]]: (検証結果, エラーメッセージリスト)。
            検証成功時は (True, [])。
            検証失敗時は (False, [メッセージ])。
    """
    errors: list[str] = []

    # ファイル読み込み
    try:
        with open(csv_file, "r", encoding="utf-8") as f:
            csv_reader = csv.reader(f)
            csv_rows: list[list[str]] = list(csv_reader)
    except Exception as e:
        return False, [f"Failed to read CSV: {e}"]

    try:
        metadata: dict[str, Any] = load_yaml(metadata_file)
        host_vars: dict[str, Any] = load_yaml(host_vars_file)
    except Exception as e:
        return False, [f"Failed to load YAML files: {e}"]

    # 基本的なフォーマット確認
    if len(csv_rows) < 2:
        errors.append("CSV must have at least 1 header + 1 data row")
        return False, errors

    header: list[str] = csv_rows[0]
    if len(header) < 4:
        errors.append("CSV must have at least 4 columns (setting_name, type, allowed_range, description)")
        return False, errors

    expected_fixed_cols: list[str] = ["setting_name", "type", "allowed_range", "description"]
    if header[:4] != expected_fixed_cols:
        errors.append(f"CSV header mismatch. Expected {expected_fixed_cols}, got {header[:4]}")

    # メタデータから予期されるフィール数と値を取得
    expected_fields: set[str] = set(metadata.get("fields", {}).keys())
    expected_hosts: set[str] = set(
        h.get("hostname", "")
        for h in host_vars.get("hosts", [])
        if h.get("hostname")
    )

    csv_fields: set[str] = {row[0] for row in csv_rows[1:]}
    csv_hosts: set[str] = set(header[4:])

    # フィール数確認
    expected_netif_rows: int = _count_expected_netif_rows(host_vars)
    expected_row_count: int = len(expected_fields) + expected_netif_rows
    if len(csv_rows) - 1 != expected_row_count:
        errors.append(
            f"Field count mismatch: CSV has {len(csv_rows)-1} rows, "
            f"expected {expected_row_count} "
            f"({len(expected_fields)} fields + {expected_netif_rows} netif rows)"
        )

    # フィール名確認
    missing_fields: set[str] = expected_fields - csv_fields
    # netif展開行 (netif_list[*].*) は追加フィールドとして除外する
    extra_fields: set[str] = {
        f for f in csv_fields - expected_fields
        if not _NETIF_ROW_PATTERN.fullmatch(f)
    }
    if missing_fields:
        errors.append(f"Missing fields in CSV: {sorted(missing_fields)}")
    if extra_fields:
        errors.append(f"Extra fields in CSV: {sorted(extra_fields)}")

    # ホスト確認
    missing_hosts: set[str] = expected_hosts - csv_hosts
    extra_hosts: set[str] = csv_hosts - expected_hosts
    if missing_hosts:
        errors.append(f"Missing hosts in CSV: {sorted(missing_hosts)}")
    if extra_hosts:
        errors.append(f"Extra hosts in CSV: {sorted(extra_hosts)}")

    # allowed_range形式確認
    for i, row in enumerate(csv_rows[1:], 1):
        field_name: str = row[0]
        csv_range: str = row[2]

        # allowed_rangeの形式確認（直列化形式）
        if csv_range and not csv_range.startswith(
            ("numeric[", "enum[", "pattern[", "semantic[")
        ):
            errors.append(
                f"Row {i+1} ({field_name}): Invalid allowed_range format: {csv_range}"
            )

    # 列数確認
    expected_cols: int = 4 + len(expected_hosts)
    actual_cols: int = len(header)
    if actual_cols != expected_cols:
        errors.append(
            f"Column count mismatch: CSV has {actual_cols} columns, "
            f"expected {expected_cols} (4 fixed + {len(expected_hosts)} hosts)"
        )

    # すべての行が同じ列数か確認
    for i, row in enumerate(csv_rows, 1):
        if len(row) != len(header):
            errors.append(
                f"Row {i}: Column count mismatch (expected {len(header)}, got {len(row)})"
            )

    return len(errors) == 0, errors


def main() -> None:
    """メイン処理。"""
    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Validate host variables matrix CSV",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-c", "--csv",
        default=DEFAULT_HOST_VARS_MATRIX,
        help="Path to host_vars_scalars_matrix.csv",
    )
    parser.add_argument(
        "-m", "--metadata",
        default=DEFAULT_FIELD_METADATA,
        help="Path to field_metadata.yaml",
    )
    parser.add_argument(
        "-H", "--host-vars",
        default=DEFAULT_HOST_VARS_STRUCTURED,
        help="Path to host_vars_structured.yaml",
    )

    args: argparse.Namespace = parser.parse_args()

    try:
        is_valid: bool
        errors: list[str]
        is_valid, errors = validate_csv(args.csv, args.metadata, args.host_vars)

        if is_valid:
            print("✓ CSV validation passed", file=sys.stderr)
            sys.exit(0)
        else:
            print("✗ CSV validation failed:", file=sys.stderr)
            for error in errors:
                print(f"  - {error}", file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
