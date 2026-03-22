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
"""compare_hostvars_role_scoped の CLI 契約テスト。"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Callable, cast

import pytest

# compare_hostvars_role_scoped.py は `src/genAnsibleConf` 直下実行を前提に
# `from lib...` import を行うため, テストでも同じ import 解決順を与える。
PROTOTYPE_DIR: Path = Path(__file__).resolve().parents[2] / "src" / "genAnsibleConf"
if str(PROTOTYPE_DIR) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_DIR))

import compare_hostvars_role_scoped as compare_module  # type: ignore[import-not-found]
compare_module_any: Any = compare_module

ParseArgsType = Callable[[], argparse.Namespace]
parse_args_typed: ParseArgsType = cast(ParseArgsType, compare_module_any.parse_args)


def test_parse_args_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """引数未指定時のデフォルト値を検証する。"""
    monkeypatch.setattr(sys, "argv", ["compare_hostvars_role_scoped.py"])

    args_any: Any = parse_args_typed()

    assert cast(Path, args_any.ansible_base) == Path("ansible")
    assert cast(Path, args_any.generated_dir) == Path("hvtest_final")
    assert cast(Path, args_any.topology) == Path("network_topology.yaml")
    assert cast(Path, args_any.prototype_root) == PROTOTYPE_DIR


def test_parse_args_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    """明示指定した引数がデフォルトより優先されることを検証する。"""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "compare_hostvars_role_scoped.py",
            "--ansible-base", "a-base",
            "--generated-dir", "g-dir",
            "--topology", "topo.yaml",
            "--prototype-root", "proto-root",
        ],
    )

    args_any: Any = parse_args_typed()

    assert cast(Path, args_any.ansible_base) == Path("a-base")
    assert cast(Path, args_any.generated_dir) == Path("g-dir")
    assert cast(Path, args_any.topology) == Path("topo.yaml")
    assert cast(Path, args_any.prototype_root) == Path("proto-root")


def test_compare_script_source_has_no_sys_path_mutation() -> None:
    """スクリプト本体が sys.path 変更に依存しないことを検証する。"""
    source_path: Path = PROTOTYPE_DIR / "compare_hostvars_role_scoped.py"
    source_text: str = source_path.read_text(encoding="utf-8")

    assert "sys.path.insert" not in source_text
    assert "sys.path.append" not in source_text
