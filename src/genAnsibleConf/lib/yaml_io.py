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
"""prototype 用の YAML 入出力ユーティリティを提供するモジュールである。

このモジュールは, 既存スクリプト群に散在している YAML 読み書き処理を
共通化し, 変換契約を一箇所に固定することを目的とする。
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

import yaml


def load_yaml_file(path: str | Path) -> Any:
    """YAML ファイルを読み込み, 解析結果を返す。

    Args:
        path (str | Path): 読み込み対象ファイルである。

    Returns:
        Any: `yaml.safe_load` の戻り値である。空ファイルは `None` である。

    Raises:
        FileNotFoundError: 指定ファイルが存在しない場合に送出する。
        OSError: ファイルを開けない場合に送出する。
        yaml.YAMLError: YAML 構文が不正な場合に送出する。

    Examples:
        >>> from pathlib import Path
        >>> p = Path("/tmp/example.yaml")
        >>> _ = p.write_text("key: value\n", encoding="utf-8")
        >>> load_yaml_file(p)["key"]
        'value'
    """
    resolved_path: Path = Path(path)
    if not resolved_path.exists():
        raise FileNotFoundError(f"YAML file not found: {resolved_path}")

    with resolved_path.open("r", encoding="utf-8") as input_file:
        loaded_data: Any = yaml.safe_load(input_file)

    return loaded_data


def load_yaml_mapping(path: str | Path) -> dict[str, Any]:
    """YAML ファイルを辞書として読み込む。

    Args:
        path (str | Path): 読み込み対象ファイルである。

    Returns:
        dict[str, Any]: top-level が辞書の YAML データである。

    Raises:
        FileNotFoundError: 指定ファイルが存在しない場合に送出する。
        ValueError: top-level が辞書以外の場合に送出する。
        OSError: ファイルを開けない場合に送出する。
        yaml.YAMLError: YAML 構文が不正な場合に送出する。

    Examples:
        >>> from pathlib import Path
        >>> p = Path("/tmp/mapping.yaml")
        >>> _ = p.write_text("a: 1\n", encoding="utf-8")
        >>> load_yaml_mapping(p)["a"]
        1
    """
    loaded_data: Any = load_yaml_file(path)
    if not isinstance(loaded_data, dict):
        raise ValueError(
            "YAML top-level must be a mapping (dict), "
            f"got {type(loaded_data).__name__}"
        )

    return cast(dict[str, Any], loaded_data)


def write_yaml_file(
    path: str | Path,
    data: Any,
    *,
    sort_keys: bool = False,
    allow_unicode: bool = True,
) -> None:
    """データを YAML としてファイルへ書き込む。

    Args:
        path (str | Path): 出力先ファイルである。
        data (Any): 出力対象データである。
        sort_keys (bool): YAML 出力時にキーをソートするかを示す。
        allow_unicode (bool): Unicode をそのまま出力するかを示す。

    Raises:
        OSError: ファイルを開けない場合に送出する。
        yaml.YAMLError: YAML 出力に失敗した場合に送出する。

    Examples:
        >>> from pathlib import Path
        >>> p = Path("/tmp/out.yaml")
        >>> write_yaml_file(p, {"b": 2, "a": 1}, sort_keys=False)
        >>> p.exists()
        True
    """
    resolved_path: Path = Path(path)
    parent_dir: Path = resolved_path.parent
    parent_dir.mkdir(parents=True, exist_ok=True)

    with resolved_path.open("w", encoding="utf-8") as output_file:
        yaml.safe_dump(
            data,
            output_file,
            default_flow_style=False,
            allow_unicode=allow_unicode,
            sort_keys=sort_keys,
        )


def yaml_value_to_string(
    value: Any,
    *,
    flow_style: bool = True,
    width: int = 4096,
) -> str:
    """値を 1 行の YAML 表現へ変換する。

    `generate_host_vars_files` の `format_scalar` と同等契約を提供する。

    Args:
        value (Any): 文字列化対象値である。
        flow_style (bool): フロー形式を使うかを示す。
        width (int): `yaml.safe_dump` の折り返し幅である。

    Returns:
        str: 1 行 YAML 表現である。

    Raises:
        yaml.YAMLError: YAML ダンプに失敗した場合に送出する。

    Examples:
        >>> yaml_value_to_string("abc")
        '"abc"'
        >>> yaml_value_to_string(None)
        'null'
    """
    dump_kwargs: dict[str, Any] = {
        "default_flow_style": flow_style,
        "allow_unicode": True,
        "sort_keys": False,
        "width": width,
    }

    if isinstance(value, str):
        dump_kwargs["default_style"] = '"'

    dumped_text: str = cast(str, yaml.safe_dump(value, **dump_kwargs))
    stripped_text: str = dumped_text.strip()
    lines: list[str] = [line for line in stripped_text.splitlines() if line.strip() != "..."]

    if not lines:
        return "''"
    if len(lines) == 1:
        return lines[0]

    return " ".join(lines)
