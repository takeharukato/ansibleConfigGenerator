# -*- mode: python; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 TAKEHARU KATO
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。
"""cli_defaults の schema 参照優先順位を検証する。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml

from src.genAnsibleConf.lib import cli_defaults


def _write_config(path: Path, payload: dict[str, Any]) -> None:
    """テスト用 YAML 設定を書き込む。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")


def test_resolve_schema_file_prefers_cli_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """CLI 指定ディレクトリが最優先で選択される。"""
    filename: str = "resolver-priority.schema.yaml"

    cli_dir: Path = tmp_path / "cli"
    user_dir: Path = tmp_path / "user"
    system_dir: Path = tmp_path / "system"
    datadir_dir: Path = tmp_path / "datadir"

    cli_file: Path = cli_dir / filename
    user_file: Path = user_dir / filename
    system_file: Path = system_dir / filename
    datadir_file: Path = datadir_dir / filename

    for file_path in (cli_file, user_file, system_file, datadir_file):
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text("key: value\n", encoding="utf-8")

    user_config: Path = tmp_path / "home" / ".genAnsibleConf.yaml"
    system_config: Path = tmp_path / "etc" / "genAnsibleConf" / "config.yaml"
    _write_config(user_config, {"schema_search_paths": {"default_dir": str(user_dir)}})
    _write_config(system_config, {"schema_search_paths": {"default_dir": str(system_dir)}})

    monkeypatch.setattr(cli_defaults, "DEFAULT_USER_CONFIG_PATH", str(user_config))
    monkeypatch.setattr(cli_defaults, "DEFAULT_SYSTEM_CONFIG_PATH", str(system_config))
    monkeypatch.setenv("GENANSIBLECONF_SCHEMADIR", str(datadir_dir))

    resolved: Path = cli_defaults.resolve_schema_file(filename, str(cli_dir))

    assert resolved == cli_file.resolve()


def test_resolve_schema_file_uses_user_config_when_cli_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CLI 未指定時はユーザー設定の参照先を利用する。"""
    filename: str = "field_metadata.yaml"

    per_file_dir: Path = tmp_path / "user-specific"
    per_file_dir.mkdir(parents=True, exist_ok=True)
    expected_file: Path = per_file_dir / filename
    expected_file.write_text("fields: {}\n", encoding="utf-8")

    user_config: Path = tmp_path / "home" / ".genAnsibleConf.yaml"
    _write_config(
        user_config,
        {
            "schema_search_paths": {
                "field_metadata": str(expected_file),
                "default_dir": str(tmp_path / "unused-default"),
            }
        },
    )

    system_config: Path = tmp_path / "etc" / "genAnsibleConf" / "config.yaml"
    _write_config(system_config, {"schema_search_paths": {"default_dir": str(tmp_path / "system")}})

    monkeypatch.setattr(cli_defaults, "DEFAULT_USER_CONFIG_PATH", str(user_config))
    monkeypatch.setattr(cli_defaults, "DEFAULT_SYSTEM_CONFIG_PATH", str(system_config))
    monkeypatch.delenv("GENANSIBLECONF_SCHEMADIR", raising=False)
    monkeypatch.setattr(cli_defaults, "GENANSIBLECONF_SCHEMADIR", "@GENANSIBLECONF_SCHEMADIR@")

    resolved: Path = cli_defaults.resolve_schema_file(filename)

    assert resolved == expected_file.resolve()


def test_resolve_schema_file_uses_system_config_when_user_is_missing(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """ユーザー設定が無い場合はシステム設定を利用する。"""
    filename: str = "network_topology.schema.yaml"

    system_dir: Path = tmp_path / "system-schema"
    system_dir.mkdir(parents=True, exist_ok=True)
    expected_file: Path = system_dir / filename
    expected_file.write_text("type: object\n", encoding="utf-8")

    user_config: Path = tmp_path / "home" / ".genAnsibleConf.yaml"
    system_config: Path = tmp_path / "etc" / "genAnsibleConf" / "config.yaml"
    _write_config(system_config, {"schema_search_paths": {"default_dir": str(system_dir)}})

    monkeypatch.setattr(cli_defaults, "DEFAULT_USER_CONFIG_PATH", str(user_config))
    monkeypatch.setattr(cli_defaults, "DEFAULT_SYSTEM_CONFIG_PATH", str(system_config))
    monkeypatch.delenv("GENANSIBLECONF_SCHEMADIR", raising=False)
    monkeypatch.setattr(cli_defaults, "GENANSIBLECONF_SCHEMADIR", "@GENANSIBLECONF_SCHEMADIR@")

    resolved: Path = cli_defaults.resolve_schema_file(filename)

    assert resolved == expected_file.resolve()


def test_resolve_schema_file_uses_datadir_before_script_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """datadir にファイルがある場合は script-dir より先に選択される。"""
    filename: str = "resolver-datadir-priority.schema.yaml"

    datadir_dir: Path = tmp_path / "datadir"
    datadir_dir.mkdir(parents=True, exist_ok=True)
    expected_file: Path = datadir_dir / filename
    expected_file.write_text("kind: datadir\n", encoding="utf-8")

    user_config: Path = tmp_path / "home" / ".genAnsibleConf.yaml"
    system_config: Path = tmp_path / "etc" / "genAnsibleConf" / "config.yaml"

    monkeypatch.setattr(cli_defaults, "DEFAULT_USER_CONFIG_PATH", str(user_config))
    monkeypatch.setattr(cli_defaults, "DEFAULT_SYSTEM_CONFIG_PATH", str(system_config))
    monkeypatch.setenv("GENANSIBLECONF_SCHEMADIR", str(datadir_dir))
    monkeypatch.setattr(cli_defaults, "GENANSIBLECONF_SCHEMADIR", "@GENANSIBLECONF_SCHEMADIR@")

    resolved: Path = cli_defaults.resolve_schema_file(filename)

    assert resolved == expected_file.resolve()


def test_resolve_schema_file_falls_back_to_script_dir(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """上位候補が無い場合は script-dir のファイルへフォールバックする。"""
    filename: str = "resolver-script-dir-fallback.schema.yaml"

    script_dir: Path = Path(cli_defaults.__file__).resolve().parent.parent
    fallback_file: Path = script_dir / filename

    user_config: Path = tmp_path / "home" / ".genAnsibleConf.yaml"
    system_config: Path = tmp_path / "etc" / "genAnsibleConf" / "config.yaml"

    monkeypatch.setattr(cli_defaults, "DEFAULT_USER_CONFIG_PATH", str(user_config))
    monkeypatch.setattr(cli_defaults, "DEFAULT_SYSTEM_CONFIG_PATH", str(system_config))
    monkeypatch.delenv("GENANSIBLECONF_SCHEMADIR", raising=False)
    monkeypatch.setattr(cli_defaults, "GENANSIBLECONF_SCHEMADIR", "@GENANSIBLECONF_SCHEMADIR@")

    try:
        fallback_file.write_text("kind: script\n", encoding="utf-8")
        resolved: Path = cli_defaults.resolve_schema_file(filename)
        assert resolved == fallback_file.resolve()
    finally:
        if fallback_file.exists():
            fallback_file.unlink()
