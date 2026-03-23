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

"""network_topology から CSV 形式のデザインシートを生成する。"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from typing import Any, cast

from lib.cli_defaults import (
    DEFAULT_FIELD_METADATA,
    DEFAULT_NETWORK_TOPOLOGY,
    DEFAULT_NETWORK_TOPOLOGY_CSV,
    DEFAULT_NETWORK_TOPOLOGY_SCHEMA,
    resolve_schema_file,
)
from lib.yaml_io import load_yaml_mapping

CSV_HEADER: list[str] = ["item", "parameter", "description", "value"]

HOST_SCALAR_KEY_PREFIX: str = "host_scalar.scalars."
GLOBAL_SCALAR_KEY_PREFIX: str = "globals.scalars."
ROLE_KEY_PREFIX: str = "role."
HOST_SERVICE_KEY_PREFIX: str = "host_service.services."
HOST_SERVICE_CONFIG_SEGMENT: str = ".config."
HOST_SERVICE_WILDCARD: str = "*"
METADATA_KEY_PATTERNS: tuple[str, ...] = (
    "globals.scalars.<scalar_key>",
    "role.<role_name>",
    "host_scalar.scalars.<scalar_key>",
    "host_service.services.<service>.config.<path>",
    "host_service.services.*.config.<path>",
)


def _as_mapping(value: Any) -> dict[str, Any]:
    """値を `dict[str, Any]` として返す。"""
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    return {}


def _as_list(value: Any) -> list[Any]:
    """値を `list[Any]` として返す。"""
    if isinstance(value, list):
        return cast(list[Any], value)
    return []


class DescriptionResolver:
    """schema 由来の description を解決するヘルパーである。"""

    def __init__(self, schema: dict[str, Any], metadata: dict[str, Any] | None = None) -> None:
        """DescriptionResolver を初期化する。

        Args:
            schema (dict[str, Any]): network_topology.schema.yaml の内容。
            metadata (dict[str, Any] | None): field_metadata.yaml の内容。

        Returns:
            None: 戻り値はない。

        Examples:
            >>> resolver = DescriptionResolver({"properties": {}})
            >>> resolver.resolve("version")
            ''
        """
        self._schema_index: dict[str, str] = build_schema_description_index(schema)
        self._metadata_index: dict[str, str] = build_metadata_description_index(
            metadata if metadata is not None else {}
        )
        self.missing_paths: set[str] = set()

    def _to_service_wildcard_key(self, metadata_key: str) -> str | None:
        """service 依存キーを service ワイルドカードキーへ変換する。"""
        match: re.Match[str] | None = re.match(
            rf"^({HOST_SERVICE_KEY_PREFIX})[^.]+(\..+)$",
            metadata_key,
        )
        if match is None:
            return None
        return f"{match.group(1)}{HOST_SERVICE_WILDCARD}{match.group(2)}"

    def _normalize_data_path(self, data_path: str) -> str:
        """実データ path を schema path に正規化する。

        Args:
            data_path (str): 実データ側の path。

        Returns:
            str: schema 検索向け path。

        Examples:
            >>> resolver = DescriptionResolver({"properties": {}})
            >>> resolver._normalize_data_path("nodes[3].interfaces[0].netif")
            'nodes.*.interfaces.*.netif'
        """
        normalized: str = re.sub(r"^nodes\[\d+\]\.", "nodes.*.", data_path)
        normalized = re.sub(r"\.interfaces\[\d+\]\.", ".interfaces.*.", normalized)
        normalized = re.sub(r"\.vcinstances_clusterversions\[\d+\]\.", ".vcinstances_clusterversions.*.", normalized)
        normalized = re.sub(r"\.vcinstances_virtualclusters\[\d+\]\.", ".vcinstances_virtualclusters.*.", normalized)

        normalized = re.sub(
            r"^globals\.networks\.[^.]+\.",
            "globals.networks.*.",
            normalized,
        )
        normalized = re.sub(
            r"^globals\.datacenters\.[^.]+\.",
            "globals.datacenters.*.",
            normalized,
        )
        normalized = re.sub(
            r"^globals\.roles\.[^.]+$",
            "globals.roles.*",
            normalized,
        )
        normalized = re.sub(
            r"^globals\.services\.[^.]+\.",
            "globals.services.*.",
            normalized,
        )
        normalized = re.sub(
            r"^globals\.services\.[^.]+$",
            "globals.services.*",
            normalized,
        )

        normalized = re.sub(
            r"^nodes\.\*\.services\.[^.]+\.",
            "nodes.*.services.*.",
            normalized,
        )
        normalized = re.sub(
            r"^nodes\.\*\.services\.[^.]+$",
            "nodes.*.services.*",
            normalized,
        )
        normalized = re.sub(
            r"^nodes\.\*\.scalars\.[^.]+$",
            "nodes.*.scalars.*",
            normalized,
        )

        return normalized

    def resolve(self, data_path: str, metadata_key: str | None = None) -> str:
        """path に対応する description を返す。

        Args:
            data_path (str): 実データ側の path。
            metadata_key (str | None): hosts 行用のキー (例: host_scalar.scalars.frr_bgp_asn)。

        Returns:
            str: 解決できた description。未解決時は空文字。

        Examples:
            >>> schema = {
            ...     "properties": {
            ...         "version": {"type": "integer", "description": "schema version"}
            ...     }
            ... }
            >>> resolver = DescriptionResolver(schema)
            >>> resolver.resolve("version")
            'schema version'
        """
        if metadata_key:
            direct_desc: str | None = self._metadata_index.get(metadata_key)
            if direct_desc is not None:
                return direct_desc
            wildcard_key: str | None = self._to_service_wildcard_key(metadata_key)
            if wildcard_key is not None:
                wildcard_desc: str | None = self._metadata_index.get(wildcard_key)
                if wildcard_desc is not None:
                    return wildcard_desc

        normalized: str = self._normalize_data_path(data_path)

        candidate: str = normalized
        while True:
            desc: str | None = self._schema_index.get(candidate)
            if desc is not None:
                return desc
            if "." not in candidate:
                break
            candidate = candidate.rsplit(".", 1)[0]

        self.missing_paths.add(data_path)
        return ""


def parse_args() -> argparse.Namespace:
    """CLI 引数を解析する。

    Returns:
        argparse.Namespace: 解析済み引数。

    Examples:
        >>> import sys
        >>> old = sys.argv
        >>> sys.argv = ["tool.py"]
        >>> args = parse_args()
        >>> args.input
        'network_topology.yaml'
        >>> sys.argv = old
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser(
        description="Generate CSV design sheet from network_topology.yaml",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "-i",
        "--input",
        default=DEFAULT_NETWORK_TOPOLOGY,
        help="Path to input network_topology YAML",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=DEFAULT_NETWORK_TOPOLOGY_CSV,
        help="Output path hint (directory or file path). Output filenames are derived from input basename.",
    )
    parser.add_argument(
        "-m",
        "--metadata",
        default=DEFAULT_NETWORK_TOPOLOGY_SCHEMA,
        help="Path to metadata schema YAML file",
    )
    parser.add_argument(
        "--schema-dir",
        default=None,
        help="Directory to search schema/config YAML files with highest priority",
    )
    return parser.parse_args()


def build_schema_description_index(schema: dict[str, Any]) -> dict[str, str]:
    """schema から description 索引を構築する。

    Args:
        schema (dict[str, Any]): スキーマ辞書。

    Returns:
        dict[str, str]: path -> description の対応辞書。

    Examples:
        >>> index = build_schema_description_index({"properties": {"version": {"description": "v"}}})
        >>> index["version"]
        'v'
    """
    index: dict[str, str] = {}
    properties: dict[str, Any] = _as_mapping(schema.get("properties", {}))
    if not properties:
        return index

    def add_if_description(path: str, node: Any) -> None:
        node_map: dict[str, Any] = _as_mapping(node)
        if not node_map:
            return
        desc: Any = node_map.get("description")
        if isinstance(desc, str):
            index[path] = desc

    def get_def(schema_def_name: str) -> dict[str, Any]:
        defs_raw: dict[str, Any] = _as_mapping(schema.get("$defs", {}))
        raw: dict[str, Any] = _as_mapping(defs_raw.get(schema_def_name, {}))
        return raw

    # root
    add_if_description("version", properties.get("version", {}))
    add_if_description("globals", properties.get("globals", {}))
    add_if_description("nodes", properties.get("nodes", {}))

    globals_node: dict[str, Any] = _as_mapping(properties.get("globals", {}))
    globals_props: dict[str, Any] = _as_mapping(globals_node.get("properties", {}))
    for key, schema_node in globals_props.items():
        add_if_description(f"globals.{key}", schema_node)

    network_def: dict[str, Any] = get_def("network")
    network_props: dict[str, Any] = _as_mapping(network_def.get("properties", {}))
    for key, schema_node in network_props.items():
        add_if_description(f"globals.networks.*.{key}", schema_node)

    datacenter_def: dict[str, Any] = get_def("datacenter")
    datacenter_props: dict[str, Any] = _as_mapping(datacenter_def.get("properties", {}))
    for key, schema_node in datacenter_props.items():
        add_if_description(f"globals.datacenters.*.{key}", schema_node)

    add_if_description("globals.roles.*", globals_props.get("roles", {}))

    service_entry_def: dict[str, Any] = get_def("service_entry")
    service_entry_props: dict[str, Any] = _as_mapping(service_entry_def.get("properties", {}))
    for key, schema_node in service_entry_props.items():
        add_if_description(f"globals.services.*.{key}", schema_node)
        add_if_description(f"nodes.*.services.*.{key}", schema_node)

    node_def: dict[str, Any] = get_def("node")
    node_props: dict[str, Any] = _as_mapping(node_def.get("properties", {}))
    for key, schema_node in node_props.items():
        add_if_description(f"nodes.*.{key}", schema_node)

    interface_def: dict[str, Any] = get_def("interface")
    interface_props: dict[str, Any] = _as_mapping(interface_def.get("properties", {}))
    for key, schema_node in interface_props.items():
        add_if_description(f"nodes.*.interfaces.*.{key}", schema_node)

    scalars_node: dict[str, Any] = _as_mapping(node_props.get("scalars", {}))
    scalars_props: dict[str, Any] = _as_mapping(scalars_node.get("properties", {}))
    for key, schema_node in scalars_props.items():
        add_if_description(f"nodes.*.scalars.{key}", schema_node)

    return index


def build_metadata_description_index(metadata: dict[str, Any]) -> dict[str, str]:
    """field_metadata から design sheet 向け description 索引を構築する。"""
    index: dict[str, str] = {}

    root: dict[str, Any] = _as_mapping(metadata.get("design_sheet_descriptions", {}))

    role_map: dict[str, Any] = _as_mapping(root.get("role", {}))
    for role_name, role_desc in role_map.items():
        if isinstance(role_desc, str):
            index[f"{ROLE_KEY_PREFIX}{role_name}"] = role_desc

    host_scalar_map: dict[str, Any] = _as_mapping(root.get("host_scalar", {}))
    for scalar_key, scalar_desc in host_scalar_map.items():
        if isinstance(scalar_desc, str):
            index[f"{HOST_SCALAR_KEY_PREFIX}{scalar_key}"] = scalar_desc

    host_service_map: dict[str, Any] = _as_mapping(root.get("host_service", {}))
    for service_name, service_value in host_service_map.items():
        if isinstance(service_value, str):
            index[f"{HOST_SERVICE_KEY_PREFIX}{service_name}"] = service_value
            continue
        service_value_map: dict[str, Any] = _as_mapping(service_value)
        if not service_value_map:
            continue
        for sub_path, sub_value in _flatten_mapping(
            service_value_map,
            f"{HOST_SERVICE_KEY_PREFIX}{service_name}",
        ):
            if isinstance(sub_value, str):
                index[sub_path] = sub_value
                wildcard_key: str = re.sub(
                    rf"^{HOST_SERVICE_KEY_PREFIX}[^.]+\.",
                    f"{HOST_SERVICE_KEY_PREFIX}{HOST_SERVICE_WILDCARD}.",
                    sub_path,
                )
                index.setdefault(wildcard_key, sub_value)

    fields_map: dict[str, Any] = _as_mapping(metadata.get("fields", {}))
    for field_name, field_value in fields_map.items():
        field_map: dict[str, Any] = _as_mapping(field_value)
        description: Any = field_map.get("description")
        if not isinstance(description, str):
            continue
        index.setdefault(f"{GLOBAL_SCALAR_KEY_PREFIX}{field_name}", description)
        index.setdefault(f"{HOST_SCALAR_KEY_PREFIX}{field_name}", description)
        index.setdefault(
            f"{HOST_SERVICE_KEY_PREFIX}{HOST_SERVICE_WILDCARD}{HOST_SERVICE_CONFIG_SEGMENT}{field_name}",
            description,
        )

    return index


def stringify_value(value: Any) -> str:
    """値を パラメタデザインシート 用文字列へ変換する。

    Args:
        value (Any): 変換対象値。

    Returns:
        str: パラメタデザインシート へ書き込む文字列表現。

    Examples:
        >>> stringify_value(True)
        'true'
        >>> stringify_value(["a", "b"])
        'a;b'
    """
    if value is None:
        return ""
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, list):
        return ";".join(stringify_value(item) for item in _as_list(value))
    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return str(value)


def _flatten_mapping(mapping: dict[str, Any], base_path: str) -> list[tuple[str, Any]]:
    """辞書を dot path へ平坦化する。

    Args:
        mapping (dict[str, Any]): 平坦化対象辞書。
        base_path (str): path 先頭。

    Returns:
        list[tuple[str, Any]]: (dot path, value) の一覧。

    Examples:
        >>> _flatten_mapping({"a": {"b": 1}}, "x")
        [('x.a.b', 1)]
    """
    rows: list[tuple[str, Any]] = []
    for key, value in mapping.items():
        current_path: str = f"{base_path}.{key}"
        if isinstance(value, dict):
            value_map: dict[str, Any] = _as_mapping(value)
            if not value_map:
                rows.append((current_path, {}))
                continue
            rows.extend(_flatten_mapping(value_map, current_path))
            continue
        rows.append((current_path, value))
    return rows


def build_globals_rows(topology: dict[str, Any], resolver: DescriptionResolver) -> list[list[str]]:
    """globals セクション行を生成する。

    Args:
        topology (dict[str, Any]): トポロジー辞書。
        resolver (DescriptionResolver): description 解決器。

    Returns:
        list[list[str]]: パラメタデザインシート 行一覧。

    Examples:
        >>> rows = build_globals_rows({"globals": {"scalars": {"tz": "Asia/Tokyo"}}}, DescriptionResolver({"properties": {}}))
        >>> rows[0][0]
        'globals'
    """
    rows: list[list[str]] = []
    globals_data: dict[str, Any] = _as_mapping(topology.get("globals", {}))
    if not globals_data:
        return rows

    for key, value in globals_data.items():
        if key in {"roles", "services"}:
            continue

        value_map: dict[str, Any] = _as_mapping(value)

        if key in {"networks", "datacenters"} and value_map:
            for item_key, item_value in value_map.items():
                item_value_map: dict[str, Any] = _as_mapping(item_value)
                if item_value_map:
                    for path, flat_value in _flatten_mapping(item_value_map, f"globals.{key}.{item_key}"):
                        rows.append([
                            item_key,
                            path,
                            resolver.resolve(path),
                            stringify_value(flat_value),
                        ])
                else:
                    path = f"globals.{key}.{item_key}"
                    rows.append([
                        item_key,
                        path,
                        resolver.resolve(path),
                        stringify_value(item_value),
                    ])
            continue

        if key == "scalars" and value_map:
            for path, flat_value in _flatten_mapping(value_map, "globals.scalars"):
                item_name: str = path.split(".")[-1]
                metadata_key: str = f"{GLOBAL_SCALAR_KEY_PREFIX}{item_name}"
                rows.append([
                    item_name,
                    path,
                    resolver.resolve(path, metadata_key),
                    stringify_value(flat_value),
                ])
            continue

        path = f"globals.{key}"
        rows.append([
            key,
            path,
            resolver.resolve(path),
            stringify_value(value),
        ])

    return rows


def build_role_rows(topology: dict[str, Any], resolver: DescriptionResolver) -> list[list[str]]:
    """roles セクション行を生成する。

    Args:
        topology (dict[str, Any]): トポロジー辞書。
        resolver (DescriptionResolver): description 解決器。

    Returns:
        list[list[str]]: パラメタデザインシート 行一覧。

    Examples:
        >>> t = {"globals": {"roles": {"r1": ["svc1", "svc2"]}}}
        >>> rows = build_role_rows(t, DescriptionResolver({"properties": {"globals": {"properties": {"roles": {"description": "roles"}}}}}))
        >>> rows[0][2]
        'r1'
    """
    rows: list[list[str]] = []
    globals_data: dict[str, Any] = _as_mapping(topology.get("globals", {}))
    roles: dict[str, Any] = _as_mapping(globals_data.get("roles", {}))
    if not roles:
        return rows

    for role_name, services in roles.items():
        data_path: str = f"globals.roles.{role_name}"
        metadata_key: str = f"{ROLE_KEY_PREFIX}{role_name}"
        rows.append([
            str(role_name),
            "service_list",
            resolver.resolve(data_path, metadata_key),
            stringify_value(services),
        ])

    return rows


def build_service_rows(topology: dict[str, Any], resolver: DescriptionResolver) -> list[list[str]]:
    """services セクション行を生成する。

    Args:
        topology (dict[str, Any]): トポロジー辞書。
        resolver (DescriptionResolver): description 解決器。

    Returns:
        list[list[str]]: パラメタデザインシート 行一覧。

    Examples:
        >>> t = {"globals": {"services": {"svc": {"config": {}}}}}
        >>> rows = build_service_rows(t, DescriptionResolver({"properties": {}}))
        >>> rows[0][3]
        'config'
    """
    rows: list[list[str]] = []
    globals_data: dict[str, Any] = _as_mapping(topology.get("globals", {}))
    services: dict[str, Any] = _as_mapping(globals_data.get("services", {}))
    if not services:
        return rows

    for service_name, service_entry in services.items():
        base_path: str = f"globals.services.{service_name}"
        if not isinstance(service_entry, dict):
            metadata_key: str = f"{HOST_SERVICE_KEY_PREFIX}{service_name}"
            rows.append([
                str(service_name),
                "value",
                resolver.resolve(base_path, metadata_key),
                stringify_value(service_entry),
            ])
            continue

        service_entry_map: dict[str, Any] = _as_mapping(service_entry)
        if not service_entry_map:
            data_path = f"{base_path}.config"
            metadata_key = f"{HOST_SERVICE_KEY_PREFIX}{service_name}.config"
            rows.append([
                str(service_name),
                "config",
                resolver.resolve(data_path, metadata_key),
                "",
            ])
            continue

        if "enabled" in service_entry_map:
            data_path = f"{base_path}.enabled"
            metadata_key = f"{HOST_SERVICE_KEY_PREFIX}{service_name}.enabled"
            rows.append([
                str(service_name),
                "enabled",
                resolver.resolve(data_path, metadata_key),
                stringify_value(service_entry_map.get("enabled")),
            ])

        config_value: Any = service_entry_map.get("config", {})
        if isinstance(config_value, dict):
            config_map: dict[str, Any] = _as_mapping(config_value)
            if not config_map:
                data_path = f"{base_path}.config"
                metadata_key = f"{HOST_SERVICE_KEY_PREFIX}{service_name}.config"
                rows.append([
                    str(service_name),
                    "config",
                    resolver.resolve(data_path, metadata_key),
                    "",
                ])
            else:
                for path, flat_value in _flatten_mapping(config_map, f"{base_path}.config"):
                    parameter: str = path.replace(f"{base_path}.", "", 1)
                    metadata_key = f"{HOST_SERVICE_KEY_PREFIX}{service_name}.{parameter}"
                    rows.append([
                        str(service_name),
                        parameter,
                        resolver.resolve(path, metadata_key),
                        stringify_value(flat_value),
                    ])
        elif "config" in service_entry_map:
            data_path = f"{base_path}.config"
            metadata_key = f"{HOST_SERVICE_KEY_PREFIX}{service_name}.config"
            rows.append([
                str(service_name),
                "config",
                resolver.resolve(data_path, metadata_key),
                stringify_value(config_value),
            ])

    return rows


def build_host_rows(
    topology: dict[str, Any],
    resolver: DescriptionResolver,
) -> tuple[dict[str, dict[str, str]], dict[str, str], list[str]]:
    """hosts セクション行を生成する（列形式）。

    各フィールドについて、複数ホストの値を保持する構造を生成する。

    Args:
        topology (dict[str, Any]): トポロジー辞書。
        resolver (DescriptionResolver): description 解決器。

    Returns:
        tuple[host_data, host_descriptions, host_names]: ホスト別データと説明とホスト名順序。
        - host_data (dict[str, dict[str, str]]): {row_kind.parameter: {host_name: value}}
        - host_descriptions (dict[str, str]): {row_kind.parameter: description}
        - host_names (list[str]): ホスト名順序

    Examples:
        >>> t = {"nodes": [{"name": "n1", "hostname_fqdn": "n1.local", "roles": ["r"], "interfaces": [{"netif": "eth0"}]}]}
        >>> data, desc, names = build_host_rows(t, DescriptionResolver({"properties": {}}))
        >>> "host_node.name" in data
        True
    """
    host_data: dict[str, dict[str, str]] = {}
    host_descriptions: dict[str, str] = {}
    host_names_order: list[str] = []

    nodes: list[Any] = _as_list(topology.get("nodes", []))
    if not nodes:
        return host_data, host_descriptions, host_names_order

    # ホスト名順序を確定
    for node_index, node in enumerate(nodes):
        node_map: dict[str, Any] = _as_mapping(node)
        host_name_raw: Any = node_map.get("name", f"node{node_index}")
        host_name: str = str(host_name_raw)
        host_names_order.append(host_name)

    base_fields: tuple[str, ...] = (
        "name",
        "hostname_fqdn",
        "roles",
        "datacenter",
        "cluster",
        "control_plane",
    )

    for node_index, node in enumerate(nodes):
        node_map: dict[str, Any] = _as_mapping(node)
        if not node_map:
            continue

        host_name: str = str(node_map.get("name", f"node{node_index}"))

        # Base fields (host_node)
        for field_name in base_fields:
            if field_name not in node_map:
                continue
            data_path: str = f"nodes[{node_index}].{field_name}"
            key: str = f"host_node.{field_name}"

            if key not in host_data:
                host_data[key] = {}
                host_descriptions[key] = resolver.resolve(data_path, key)

            host_data[key][host_name] = stringify_value(node_map.get(field_name))

        # Interfaces (host_interface)
        interfaces: list[Any] = _as_list(node_map.get("interfaces", []))
        for if_index, interface in enumerate(interfaces):
            interface_map: dict[str, Any] = _as_mapping(interface)
            if not interface_map:
                continue

            for if_key, if_value in interface_map.items():
                data_path: str = f"nodes[{node_index}].interfaces[{if_index}].{if_key}"
                parameter: str = f"interfaces[{if_index}].{if_key}"
                key: str = f"host_interface.{parameter}"

                if key not in host_data:
                    host_data[key] = {}
                    host_descriptions[key] = resolver.resolve(data_path, key)

                host_data[key][host_name] = stringify_value(if_value)

        # Scalars (host_scalar)
        scalars: dict[str, Any] = _as_mapping(node_map.get("scalars", {}))
        for scalar_path, scalar_value in _flatten_mapping(scalars, f"nodes[{node_index}].scalars"):
            parameter: str = scalar_path.replace(f"nodes[{node_index}].", "", 1)
            key: str = f"host_scalar.{parameter}"

            if key not in host_data:
                host_data[key] = {}
                host_descriptions[key] = resolver.resolve(scalar_path, key)

            host_data[key][host_name] = stringify_value(scalar_value)

        # Services (host_service)
        services: dict[str, Any] = _as_mapping(node_map.get("services", {}))
        for service_name, service_entry in services.items():
            service_base: str = f"nodes[{node_index}].services.{service_name}"
            service_entry_map: dict[str, Any] = _as_mapping(service_entry)

            if not service_entry_map:
                if service_entry in ({}, None):
                    continue
                key: str = f"host_service.services.{service_name}"
                if key not in host_data:
                    host_data[key] = {}
                    host_descriptions[key] = resolver.resolve(service_base, key)
                host_data[key][host_name] = stringify_value(service_entry)
                continue

            for sub_path, sub_value in _flatten_mapping(service_entry_map, service_base):
                parameter: str = sub_path.replace(f"nodes[{node_index}].", "", 1)
                key: str = f"host_service.{parameter}"

                if key not in host_data:
                    host_data[key] = {}
                    host_descriptions[key] = resolver.resolve(sub_path, key)

                value: str = "" if (isinstance(sub_value, dict) and not sub_value) else stringify_value(sub_value)
                host_data[key][host_name] = value

    return host_data, host_descriptions, host_names_order


def _write_section_csv(output_path: str, rows: list[list[str]]) -> None:
    """セクションデータを パラメタデザインシート 用ファイルへ書き込む。

    グローバル, ロール, サービスセクション向け（行ベース形式）。

    Args:
        output_path (str): 出力ファイルパス。
        rows (list[list[str]]): パラメタデザインシート 行一覧。

    Returns:
        None: 戻り値はない。

    Examples:
        >>> import tempfile
        >>> fd, path = tempfile.mkstemp(suffix='.csv')
        >>> import os; os.close(fd)
        >>> _write_section_csv(path, [["a", "b"], ["1", "2"]])
        >>> Path(path).read_text()[:5]
        'a,b\\n'
        >>> Path(path).unlink()
    """
    csv_buffer: io.StringIO = io.StringIO()
    writer = csv.writer(csv_buffer, lineterminator="\n")
    writer.writerow(CSV_HEADER)
    writer.writerows(rows)
    content: str = csv_buffer.getvalue()
    Path(output_path).write_text(content, encoding="utf-8")


def _write_section_csv_hosts(
    output_path: str,
    host_data: dict[str, dict[str, str]],
    host_descriptions: dict[str, str],
    host_names: list[str],
) -> None:
    """hosts セクション をホスト別列形式で書き込む。

    Args:
        output_path (str): 出力ファイルパス。
        host_data (dict[str, dict[str, str]]): {row_kind.parameter: {host_name: value}}
        host_descriptions (dict[str, str]): {row_kind.parameter: description}
        host_names (list[str]): ホスト名順序。

    Returns:
        None: 戻り値はない。

    Examples:
        >>> import tempfile, os
        >>> fd, path = tempfile.mkstemp(suffix='.csv')
        >>> os.close(fd)
        >>> host_data = {"host_node.name": {"h1": "h1", "h2": "h2"}}
        >>> host_desc = {"host_node.name": "name"}
        >>> _write_section_csv_hosts(path, host_data, host_desc, ["h1", "h2"])
        >>> Path(path).read_text().split('\\n')[0]
        'parameter,description,h1,h2'
        >>> Path(path).unlink()
    """
    csv_buffer: io.StringIO = io.StringIO()
    writer = csv.writer(csv_buffer, lineterminator="\n")

    # ヘッダー
    header: list[str] = ["parameter", "description"] + host_names
    writer.writerow(header)

    # データ行
    for key in sorted(host_data.keys()):
        description: str = host_descriptions.get(key, "")
        host_values: list[str] = [
            host_data[key].get(host_name, "")
            for host_name in host_names
        ]
        row: list[str] = [key, description] + host_values
        writer.writerow(row)

    content: str = csv_buffer.getvalue()
    Path(output_path).write_text(content, encoding="utf-8")


def _resolve_output_dir(input_file: str, output_hint: str | None) -> Path:
    """出力ディレクトリを解決する。

    出力ファイル名は入力ファイル名から生成するため, ここでは出力先ディレクトリのみを決定する。
    `output_hint` がディレクトリならそのディレクトリを使用し, それ以外は親ディレクトリを使用する。

    Args:
        input_file (str): 入力ファイルパス。
        output_hint (str | None): 出力ヒント。

    Returns:
        Path: 出力ディレクトリ。

    Examples:
        >>> _resolve_output_dir("/tmp/network_topology.yaml", None)
        PosixPath('/tmp')
    """
    input_path: Path = Path(input_file).resolve()
    if output_hint is None:
        return input_path.parent

    hint_path: Path = Path(output_hint)
    if output_hint.endswith(("/", "\\")):
        return hint_path.resolve()
    if hint_path.exists() and hint_path.is_dir():
        return hint_path.resolve()
    return hint_path.resolve().parent


def _generate_output_filenames(input_file: str, output_hint: str | None) -> dict[str, str]:
    """出力ファイルパスを生成する。

    Args:
        input_file (str): 入力ファイルパス。
        output_hint (str | None): 出力ヒント。

    Returns:
        dict[str, str]: セクション名から出力ファイルパスへのマッピング。

    Examples:
        >>> paths = _generate_output_filenames("network_topology.yaml", ".")
        >>> "globals" in paths
        True
        >>> "network_topology-globals.csv" in paths["globals"]
        True
    """
    output_dir: Path = _resolve_output_dir(input_file, output_hint)
    base: str = Path(input_file).stem
    return {
        "globals": str(output_dir / f"{base}-globals.csv"),
        "roles": str(output_dir / f"{base}-roles.csv"),
        "services": str(output_dir / f"{base}-services.csv"),
        "hosts": str(output_dir / f"{base}-hosts.csv"),
    }


def _validate_topology(topology: dict[str, Any]) -> None:
    """トポロジー必須要件を検証する。

    Args:
        topology (dict[str, Any]): トポロジー辞書。

    Returns:
        None: 戻り値はない。

    Raises:
        ValueError: 必須キー欠落または型不一致の場合。

    Examples:
        >>> _validate_topology({"version": 2, "globals": {}, "nodes": []})
    """
    required_keys: tuple[str, ...] = ("version", "globals", "nodes")
    for key in required_keys:
        if key not in topology:
            raise ValueError(f"Missing required top-level key: {key}")

    if not isinstance(topology.get("globals"), dict):
        raise ValueError("Top-level 'globals' must be object")
    if not isinstance(topology.get("nodes"), list):
        raise ValueError("Top-level 'nodes' must be array")


def generate_design_sheet_csv(
    input_file: str,
    metadata_file: str,
    output_base: str | None = None,
    schema_dir: str | None = None,
) -> list[str]:
    """パラメタデザインシートを生成する。

    4 つの独立した CSV ファイルを生成する (ファイル名は入力ファイルのベース名から自動決定される):
    - {input_stem}-globals.csv
    - {input_stem}-roles.csv
    - {input_stem}-services.csv
    - {input_stem}-hosts.csv

    Args:
        input_file (str): 入力トポロジー YAML パス。
        metadata_file (str): 入力スキーマ YAML パス。
        output_base (str | None): 出力ファイルの基礎パス。未指定時はファイル生成しない。

    Returns:
        list[str]: description 欠落 path の昇順一覧。

    Raises:
        FileNotFoundError: 入力ファイルが存在しない場合。
        ValueError: 必須キー欠落や型不一致の場合。

    Examples:
        >>> import tempfile, os
        >>> from pathlib import Path
        >>> topo_fd, topo_path = tempfile.mkstemp(suffix='.yaml')
        >>> sch_fd, sch_path = tempfile.mkstemp(suffix='.yaml')
        >>> base_fd, base_path = tempfile.mkstemp(suffix='')
        >>> os.close(base_fd)
        >>> _ = os.write(topo_fd, b"version: 2\nglobals: {networks: {}, datacenters: {}}\nnodes: []\n")
        >>> _ = os.write(sch_fd, b"type: object\nproperties: {}\n")
        >>> os.close(topo_fd); os.close(sch_fd)
        >>> missing = generate_design_sheet_csv(topo_path, sch_path, base_path)
        >>> topo_stem = Path(topo_path).stem
        >>> out_dir = Path(base_path).resolve().parent
        >>> (out_dir / f"{topo_stem}-globals.csv").exists()
        True
        >>> Path(topo_path).unlink(); Path(sch_path).unlink()
        >>> for f in out_dir.glob(f"{topo_stem}-*.csv"):
        ...     f.unlink()
    """
    topology: dict[str, Any] = load_yaml_mapping(input_file)
    schema: dict[str, Any] = load_yaml_mapping(metadata_file)
    _validate_topology(topology)

    field_metadata_file: Path = resolve_schema_file(DEFAULT_FIELD_METADATA, schema_dir)
    field_metadata: dict[str, Any] = load_yaml_mapping(str(field_metadata_file))

    resolver: DescriptionResolver = DescriptionResolver(schema, field_metadata)

    section_data: dict[str, list[list[str]]] = {
        "globals": build_globals_rows(topology, resolver),
        "roles": build_role_rows(topology, resolver),
        "services": build_service_rows(topology, resolver),
    }

    # hosts セクションは別処理（列ベース形式）
    host_data: dict[str, dict[str, str]]
    host_descriptions: dict[str, str]
    host_names: list[str]
    host_data, host_descriptions, host_names = build_host_rows(topology, resolver)

    if output_base:
        output_files: dict[str, str] = _generate_output_filenames(input_file, output_base)
        for section_name, rows in section_data.items():
            output_path: str = output_files[section_name]
            _write_section_csv(output_path, rows)
        # hosts セクションを別フォーマットで出力
        _write_section_csv_hosts(
            output_files["hosts"],
            host_data,
            host_descriptions,
            host_names,
        )

    return sorted(resolver.missing_paths)


def main() -> None:
    """メイン処理を実行する。"""
    args: argparse.Namespace = parse_args()
    metadata_file: str = args.metadata
    if Path(metadata_file) == Path(DEFAULT_NETWORK_TOPOLOGY_SCHEMA):
        metadata_file = str(resolve_schema_file(DEFAULT_NETWORK_TOPOLOGY_SCHEMA, args.schema_dir))

    try:
        missing_paths: list[str] = generate_design_sheet_csv(
            args.input,
            metadata_file,
            args.output,
            args.schema_dir,
        )
        for path in missing_paths:
            print(f"Warning: missing description for {path}", file=sys.stderr)

        output_files: dict[str, str] = _generate_output_filenames(args.input, args.output)
        for output_file in output_files.values():
            print(f"CSV generated: {output_file}", file=sys.stderr)
    except Exception as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
