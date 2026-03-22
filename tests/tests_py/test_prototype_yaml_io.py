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
"""yaml_io の単体テスト。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest

from src.genAnsibleConf.lib.yaml_io import (
    load_yaml_file,
    load_yaml_mapping,
    write_yaml_file,
    yaml_value_to_string,
)


def test_load_yaml_file_returns_mapping(tmp_path: Path) -> None:
    """辞書 YAML を辞書として返すことを検証する。"""
    yaml_path: Path = tmp_path / "data.yaml"
    yaml_path.write_text("key: value\n", encoding="utf-8")

    loaded_data: Any = load_yaml_file(yaml_path)

    assert isinstance(loaded_data, dict)
    assert loaded_data == {"key": "value"}


def test_load_yaml_file_returns_none_for_empty_file(tmp_path: Path) -> None:
    """空 YAML を読み込んだ場合は None を返すことを検証する。"""
    yaml_path: Path = tmp_path / "empty.yaml"
    yaml_path.write_text("", encoding="utf-8")

    loaded_data: Any = load_yaml_file(yaml_path)

    assert loaded_data is None


def test_load_yaml_file_raises_for_missing_file(tmp_path: Path) -> None:
    """不存在ファイルで FileNotFoundError を送出することを検証する。"""
    missing_path: Path = tmp_path / "missing.yaml"

    with pytest.raises(FileNotFoundError):
        load_yaml_file(missing_path)


def test_load_yaml_mapping_returns_mapping(tmp_path: Path) -> None:
    """mapping 読み込みが辞書を返すことを検証する。"""
    yaml_path: Path = tmp_path / "mapping.yaml"
    yaml_path.write_text("a: 1\n", encoding="utf-8")

    loaded_mapping: dict[str, Any] = load_yaml_mapping(yaml_path)

    assert loaded_mapping == {"a": 1}


def test_load_yaml_mapping_rejects_list_top_level(tmp_path: Path) -> None:
    """top-level が list の YAML を拒否することを検証する。"""
    yaml_path: Path = tmp_path / "list.yaml"
    yaml_path.write_text("- a\n- b\n", encoding="utf-8")

    with pytest.raises(ValueError):
        load_yaml_mapping(yaml_path)


def test_write_yaml_file_roundtrip_unicode(tmp_path: Path) -> None:
    """Unicode を含むデータが round-trip 可能であることを検証する。"""
    yaml_path: Path = tmp_path / "unicode.yaml"
    source_data: dict[str, Any] = {"message": "こんにちは"}

    write_yaml_file(yaml_path, source_data)
    loaded_mapping: dict[str, Any] = load_yaml_mapping(yaml_path)

    assert loaded_mapping == source_data


def test_write_yaml_file_preserves_key_order(tmp_path: Path) -> None:
    """sort_keys=False でキー順を保持することを検証する。"""
    yaml_path: Path = tmp_path / "ordered.yaml"
    source_data: dict[str, Any] = {"z": 1, "a": 2}

    write_yaml_file(yaml_path, source_data, sort_keys=False)
    file_text: str = yaml_path.read_text(encoding="utf-8")

    assert file_text.find("z:") < file_text.find("a:")


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("abc", '"abc"'),
        (["a", "b"], "[a, b]"),
        ({"a": 1}, "{a: 1}"),
        (True, "true"),
        (10, "10"),
        (None, "null"),
    ],
)
def test_yaml_value_to_string_formats_expected(value: Any, expected: str) -> None:
    """値ごとの 1 行 YAML 文字列表現を検証する。"""
    actual_text: str = yaml_value_to_string(value)

    assert actual_text == expected
