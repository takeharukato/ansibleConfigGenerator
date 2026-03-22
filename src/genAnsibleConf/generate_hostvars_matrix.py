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
ホスト変数マトリックスCSV生成ツール。

host_vars_structured.yamlとfield_metadata.yamlを読み込み,
ホスト別の設定値とメタデータを組み合わせたCSVを生成する。

CSV形式：
  - setting_name: 設定項目名
  - type: データ型
  - allowed_range: 指定可能値の範囲（簡潔な表記）
  - description: 説明文
  - <host1>, <host2>, ...: 各ホストの設定値
"""

import csv
import json
import sys
from pathlib import Path
from typing import Any, Optional, cast

from lib.cli_defaults import (
    DEFAULT_FIELD_METADATA,
    DEFAULT_HOST_VARS_STRUCTURED,
    resolve_schema_file,
)
from lib.yaml_io import load_yaml_file

# netif_list と hostname, scalars はトップレベルルックアップから除外する
_TOP_LEVEL_EXCLUDE: frozenset[str] = frozenset({"hostname", "netif_list", "scalars"})


def load_yaml(file_path: str) -> dict[str, Any]:
    """YAMLファイルを読み込む。

    Args:
        file_path (str): YAMLファイルパス。

    Returns:
        dict[str, Any]: 解析されたYAML内容。

    Raises:
        FileNotFoundError: ファイルが見つからない場合。
        yaml.YAMLError: YAML解析エラー。
    """
    data: Any = load_yaml_file(file_path)
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"Top-level YAML must be object: {file_path}")
    return cast(dict[str, Any], data)


def serialize_allowed_range(range_spec: Optional[dict[str, Any]]) -> str:
    """allowed_rangeをCSV用の簡潔な文字列に直列化する。

    kind別に以下の形式に変換：
      - numeric: "numeric[1:100]"
      - enum: "enum[val1|val2]"
      - pattern: "pattern[regex]"
      - semantic: "semantic[name]"

    Args:
        range_spec (Optional[dict[str, Any]]): allowed_rangeディクショナリ。

    Returns:
        str: 直列化された文字列。Noneの場合は空文字列を返す。
    """
    if range_spec is None:
        return ""

    kind_raw: Any = range_spec.get("kind", "")
    kind: str = kind_raw if isinstance(kind_raw, str) else ""

    if kind == "numeric":
        min_val: Optional[int | float] = range_spec.get("min")
        max_val: Optional[int | float] = range_spec.get("max")
        return f"numeric[{min_val}:{max_val}]"

    elif kind == "enum":
        values_raw: Any = range_spec.get("values", [])
        values: list[Any] = cast(list[Any], values_raw) if isinstance(values_raw, list) else []
        return "enum[" + "|".join(str(v) for v in values) + "]"

    elif kind == "pattern":
        regex_raw: Any = range_spec.get("regex", "")
        regex: str = regex_raw if isinstance(regex_raw, str) else ""
        return f"pattern[{regex}]"

    elif kind == "semantic":
        name_raw: Any = range_spec.get("name", "")
        name: str = name_raw if isinstance(name_raw, str) else ""
        return f"semantic[{name}]"

    return ""


def stringify_value(value: Any) -> str:
    """値をCSV用文字列へ変換する。

    bool値はtrue/false文字列へ変換する。
    リストはセミコロン区切り文字列へ直列化する(再帰適用)。
    辞書はJSONコンパクト表現へ直列化する。
    Noneは空文字列として扱う。

    Args:
        value (Any): 変換対象値。

    Returns:
        str: CSV へ書き込む文字列表現。

    Examples:
        >>> stringify_value(True)
        'true'
        >>> stringify_value(None)
        ''
        >>> stringify_value(["a", "b"])
        'a;b'
        >>> stringify_value({"k": "v"})
        '{"k":"v"}'
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ";".join(stringify_value(item) for item in cast(list[Any], value))
    if isinstance(value, dict):
        return json.dumps(
            cast(dict[str, Any], value),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    return str(value)


def get_host_values(
    hosts_data: list[dict[str, Any]], field_name: str
) -> dict[str, Any]:
    """全ホストから指定フィールドの値を取得する。

    scalars を第1優先として参照し, 見つからない場合はトップレベルを参照する。
    ただし hostname, netif_list, scalars はトップレベルルックアップから除外する。

    Args:
        hosts_data (list[dict[str, Any]]): host_vars_structured.yamlのhostsリスト。
        field_name (str): フィールド名。

    Returns:
        dict[str, Any]: {hostname: value, ...}形式のディクショナリ。
            フィールドを持たないホストは除外（キーなし）。

    Examples:
        >>> get_host_values([{"hostname": "h1", "scalars": {"k": "v"}}], "k")
        {'h1': 'v'}
        >>> get_host_values([{"hostname": "h1", "frr_networks_v4": ["x"]}], "frr_networks_v4")
        {'h1': ['x']}
    """
    values: dict[str, Any] = {}
    for host in hosts_data:
        hostname: str = host.get("hostname", "")
        if not hostname:
            continue
        scalars: dict[str, Any] = host.get("scalars", {})
        if field_name in scalars:
            values[hostname] = scalars[field_name]
        elif field_name not in _TOP_LEVEL_EXCLUDE and field_name in host:
            values[hostname] = host[field_name]
    return values


def build_netif_rows(
    hosts: list[dict[str, Any]],
    fields: dict[str, dict[str, Any]],
    hostname_list: list[str],
) -> list[list[str]]:
    """netif_listをIF展開行として生成する。

    各インターフェースを ``netif_list[{netif_name}].{sub_field}`` 形式の行として出力する。
    全ホスト横断でIF名とサブフィールドの和集合を取り,
    存在しないセルは空欄とする。

    Args:
        hosts (list[dict[str, Any]]): host_vars_structured.yaml の hosts リスト。
        fields (dict[str, dict[str, Any]]): field_metadata.yaml の fields ディクショナリ。
        hostname_list (list[str]): ヘッダー列のホスト名順リスト。

    Returns:
        list[list[str]]: netif展開行のリスト。
            各行はヘッダーと同じ列構造(setting_name, type, allowed_range, description, [hosts...])を持つ。

    Examples:
        >>> rows = build_netif_rows(
        ...     [{"hostname": "h1", "netif_list": [{"netif": "eth0", "mac": "aa:bb"}]}],
        ...     {},
        ...     ["h1"],
        ... )
        >>> rows[0][0]
        'netif_list[eth0].netif'
    """
    # 全ホストのnetif_listからIF名とサブフィールドを挿入順で収集
    seen_ifs: list[str] = []
    seen_ifs_set: set[str] = set()
    seen_subfields: list[str] = []
    seen_subfields_set: set[str] = set()
    # (hostname, if_name) -> iface_dict のルックアップテーブル
    iface_lookup: dict[tuple[str, str], dict[str, Any]] = {}

    for host in hosts:
        h_name: str = host.get("hostname", "")
        if not h_name:
            continue
        netif_list_raw: Any = host.get("netif_list", [])
        if not isinstance(netif_list_raw, list):
            continue
        for iface_dict in cast(list[Any], netif_list_raw):
            if not isinstance(iface_dict, dict):
                continue
            typed_iface: dict[str, Any] = cast(dict[str, Any], iface_dict)
            if_name: str = str(typed_iface.get("netif", ""))
            if not if_name:
                continue
            if if_name not in seen_ifs_set:
                seen_ifs.append(if_name)
                seen_ifs_set.add(if_name)
            iface_lookup[(h_name, if_name)] = typed_iface
            for subfield in typed_iface.keys():
                if subfield not in seen_subfields_set:
                    seen_subfields.append(subfield)
                    seen_subfields_set.add(subfield)

    rows: list[list[str]] = []

    for if_name in seen_ifs:
        for subfield in seen_subfields:
            row_key: str = f"netif_list[{if_name}].{subfield}"
            field_meta: dict[str, Any] = fields.get(subfield, {})
            field_type: str = str(field_meta.get("type", ""))
            desc: str = str(field_meta.get("description", ""))
            range_spec: Optional[dict[str, Any]] = field_meta.get("allowed_range")
            allowed_range_str: str = serialize_allowed_range(range_spec)

            row: list[str] = [row_key, field_type, allowed_range_str, desc]

            for hostname in hostname_list:
                netif_entry: Optional[dict[str, Any]] = iface_lookup.get(
                    (hostname, if_name)
                )
                if netif_entry is not None:
                    cell_value: Any = netif_entry.get(subfield, "")
                    row.append(stringify_value(cell_value))
                else:
                    row.append("")

            rows.append(row)

    return rows


def generate_csv(
    host_vars_file: str,
    metadata_file: str,
    output_file: Optional[str] = None,
) -> str:
    """ホスト変数マトリックスCSVを生成する。

    Args:
        host_vars_file (str): host_vars_structured.yamlのパス。
        metadata_file (str): field_metadata.yamlのパス。
        output_file (Optional[str]): 出力CSVファイルパス。
            Noneの場合はスタンダード出力に出力。

    Returns:
        str: 生成されたCSV内容（文字列）。

    Raises:
        FileNotFoundError: 入力ファイルが見つからない場合。
        KeyError: 必須キーが見つからない場合。
    """
    # ファイル読み込み
    host_vars: dict[str, Any] = load_yaml(host_vars_file)
    metadata: dict[str, Any] = load_yaml(metadata_file)

    hosts: list[dict[str, Any]] = host_vars.get("hosts", [])
    fields: dict[str, dict[str, Any]] = metadata.get("fields", {})

    if not hosts:
        raise ValueError("No hosts found in host_vars file")
    if not fields:
        raise ValueError("No fields found in metadata file")

    # ホスト名リスト取得（順序保証）
    hostname_list: list[str] = [
        h.get("hostname", "") for h in hosts if h.get("hostname")
    ]
    hostname_list = [h for h in hostname_list if h]

    # CSV行生成
    csv_rows: list[list[str]] = []

    # ヘッダー行
    header: list[str] = ["setting_name", "type", "allowed_range", "description"]
    header.extend(hostname_list)
    csv_rows.append(header)

    # データ行
    for field_name in sorted(fields.keys()):
        field_meta: dict[str, Any] = fields[field_name]
        field_type: str = field_meta.get("type", "")
        description: str = field_meta.get("description", "")

        # allowed_range直列化
        range_spec: Optional[dict[str, Any]] = field_meta.get("allowed_range")
        allowed_range_str: str = serialize_allowed_range(range_spec)

        # 各ホストの値取得
        host_values: dict[str, Any] = get_host_values(hosts, field_name)

        # CSV行構築
        row: list[str] = [
            field_name,
            field_type,
            allowed_range_str,
            description,
        ]

        # ホスト別の値を追加
        for hostname in hostname_list:
            value: Any = host_values.get(hostname, "")
            row.append(stringify_value(value))

        csv_rows.append(row)

    # netif展開行を末尾に追加
    netif_rows: list[list[str]] = build_netif_rows(hosts, fields, hostname_list)
    csv_rows.extend(netif_rows)

    # CSV文字列生成（csv.writerを使用）
    import io

    csv_buffer: io.StringIO = io.StringIO()
    writer = csv.writer(csv_buffer, lineterminator="\n")
    writer.writerows(csv_rows)
    csv_output: str = csv_buffer.getvalue()

    # ファイル出力（指定された場合）
    if output_file:
        out_path: Path = Path(output_file)
        out_path.write_text(csv_output, encoding="utf-8")
        print(f"CSV generated: {output_file}", file=sys.stderr)

    return csv_output


def main() -> None:
    """メイン処理。"""
    import argparse

    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Generate host variables matrix CSV",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-H", "--host-vars",
        default=DEFAULT_HOST_VARS_STRUCTURED,
        help="Path to host_vars_structured.yaml",
    )
    parser.add_argument(
        "-m", "--metadata",
        default=DEFAULT_FIELD_METADATA,
        help="Path to field_metadata.yaml",
    )
    parser.add_argument(
        "-o", "--output",
        help="Output CSV file path (defaults to stdout)",
    )
    parser.add_argument(
        "--schema-dir",
        default=None,
        help="Directory to search schema/config YAML files with highest priority",
    )

    args: argparse.Namespace = parser.parse_args()
    metadata_file: str = args.metadata
    if Path(metadata_file) == Path(DEFAULT_FIELD_METADATA):
        metadata_file = str(resolve_schema_file(DEFAULT_FIELD_METADATA, args.schema_dir))

    try:
        csv_content: str = generate_csv(
            args.host_vars, metadata_file, args.output
        )
        if not args.output:
            print(csv_content)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
