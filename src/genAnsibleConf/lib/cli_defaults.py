# -*- mode: python; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
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
"""genAnsibleConf CLI で利用する既定ファイル名定数を定義するモジュールである。

Attributes:
    DEFAULT_NETWORK_TOPOLOGY (str): トポロジー入力 YAML の既定ファイル名である。
    DEFAULT_NETWORK_TOPOLOGY_SCHEMA (str): トポロジー用スキーマ YAML の既定ファイル名である。
    DEFAULT_HOST_VARS_STRUCTURED (str): host_vars_structured 出力 YAML の既定ファイル名である。
    DEFAULT_FIELD_METADATA (str): フィールドメタデータ YAML の既定ファイル名である。
    DEFAULT_TERRAFORM_TFVARS (str): Terraform 変数ファイルの既定ファイル名である。
    DEFAULT_HOST_VARS_MATRIX (str): host_vars ノード設定パラメタデザインシート CSV の既定ファイル名である。
    DEFAULT_NETWORK_TOPOLOGY_CSV (str): パラメタデザインシート CSV の既定ファイル名である。
"""

from __future__ import annotations

import os
from pathlib import Path
import sys
from typing import Any, cast

import yaml

DEFAULT_NETWORK_TOPOLOGY: str = "network_topology.yaml"
DEFAULT_NETWORK_TOPOLOGY_SCHEMA: str = "network_topology.schema.yaml"
DEFAULT_HOST_VARS_STRUCTURED: str = "host_vars_structured.yaml"
DEFAULT_FIELD_METADATA: str = "field_metadata.yaml"
DEFAULT_TERRAFORM_TFVARS: str = "terraform.tfvars"
DEFAULT_HOST_VARS_MATRIX: str = "host_vars_scalars_matrix.csv"
DEFAULT_NETWORK_TOPOLOGY_CSV: str = "network_topology.csv"

DEFAULT_TYPE_SCHEMA: str = "type_schema.yaml"
DEFAULT_CONVERT_RULE_CONFIG: str = "convert-rule-config.yaml"

DEFAULT_USER_CONFIG_PATH: str = "~/.genAnsibleConf.yaml"
DEFAULT_SYSTEM_CONFIG_PATH: str = "/etc/genAnsibleConf/config.yaml"

# configure 時に置換される。未置換環境ではランタイムで安全に無効化する。
GENANSIBLECONF_SCHEMADIR: str = "@GENANSIBLECONF_SCHEMADIR@"

SCHEMA_CONFIG_KEY_MAP: dict[str, str] = {
    DEFAULT_FIELD_METADATA: "field_metadata",
    DEFAULT_NETWORK_TOPOLOGY_SCHEMA: "network_topology",
    DEFAULT_TYPE_SCHEMA: "type_schema",
    DEFAULT_CONVERT_RULE_CONFIG: "convert_rule_config",
}


def _as_mapping(value: Any) -> dict[str, Any]:
    """辞書であればそのまま返し, それ以外は空辞書を返す。"""
    if isinstance(value, dict):
        return cast(dict[str, Any], value)
    return {}


def _resolve_candidate(value: str, filename: str) -> Path:
    """設定値をファイルパスへ解決する。"""
    expanded: Path = Path(os.path.expandvars(value)).expanduser()
    if expanded.suffix:
        return expanded
    return expanded / filename


def _candidates_from_config(config_path: Path, filename: str) -> list[Path]:
    """構成ファイルから filename 用の候補パスを抽出する。"""
    if not config_path.exists():
        return []

    with config_path.open("r", encoding="utf-8") as stream:
        loaded: Any = yaml.safe_load(stream)

    config: dict[str, Any] = _as_mapping(loaded)
    search_paths: dict[str, Any] = _as_mapping(config.get("schema_search_paths"))
    if not search_paths:
        return []

    result: list[Path] = []
    config_key: str | None = SCHEMA_CONFIG_KEY_MAP.get(filename)

    if config_key is not None:
        configured_value: Any = search_paths.get(config_key)
        if isinstance(configured_value, str) and configured_value.strip():
            result.append(_resolve_candidate(configured_value.strip(), filename))

    default_dir_value: Any = search_paths.get("default_dir")
    if isinstance(default_dir_value, str) and default_dir_value.strip():
        result.append(_resolve_candidate(default_dir_value.strip(), filename))

    return result


def _infer_install_prefix(module_file: Path) -> Path | None:
    """インストール先モジュールパスから prefix を推定する。"""
    module_parts: tuple[str, ...] = module_file.resolve().parts
    for package_dir in ("site-packages", "dist-packages"):
        if package_dir not in module_parts:
            continue
        package_idx: int = module_parts.index(package_dir)
        if package_idx < 2:
            continue
        if module_parts[package_idx - 2] != "lib":
            continue
        python_dir: str = module_parts[package_idx - 1]
        if not python_dir.startswith("python"):
            continue
        return Path(*module_parts[: package_idx - 2])
    return None


def resolve_schema_file(filename: str, cli_dir: str | None = None) -> Path:
    """スキーマ/設定 YAML ファイルを優先順に探索して返す。

    優先順は以下の通りである。
    1. CLI で指定されたディレクトリ (`--schema-dir`)
    2. ユーザー設定 (`~/.genAnsibleConf.yaml`)
    3. システム設定 (`/etc/genAnsibleConf/config.yaml`)
    4. datadir (`$GENANSIBLECONF_SCHEMADIR`)
    5. generate_*.py と同一ディレクトリ
    """
    candidates: list[Path] = []

    if cli_dir:
        candidates.append(Path(cli_dir).expanduser() / filename)

    user_config: Path = Path(DEFAULT_USER_CONFIG_PATH).expanduser()
    candidates.extend(_candidates_from_config(user_config, filename))

    system_config: Path = Path(DEFAULT_SYSTEM_CONFIG_PATH)
    candidates.extend(_candidates_from_config(system_config, filename))

    runtime_datadir: str | None = os.environ.get("GENANSIBLECONF_SCHEMADIR")
    if runtime_datadir:
        candidates.append(Path(runtime_datadir).expanduser() / filename)

    if not GENANSIBLECONF_SCHEMADIR.startswith("@"):
        candidates.append(Path(GENANSIBLECONF_SCHEMADIR) / filename)

    candidates.append(Path(sys.prefix) / "share" / "genAnsibleConf" / "schema" / filename)

    inferred_prefix: Path | None = _infer_install_prefix(Path(__file__))
    if inferred_prefix is not None:
        candidates.append(inferred_prefix / "share" / "genAnsibleConf" / "schema" / filename)

    candidates.append(Path("/usr/local/share/genAnsibleConf/schema") / filename)
    candidates.append(Path("/usr/share/genAnsibleConf/schema") / filename)

    script_dir: Path = Path(__file__).resolve().parent.parent
    candidates.append(script_dir / filename)

    for candidate in candidates:
        resolved: Path = candidate.resolve()
        if resolved.exists():
            return resolved

    searched_paths: str = ", ".join(str(path) for path in candidates)
    raise FileNotFoundError(
        f"Could not resolve '{filename}'. searched: {searched_paths}"
    )
