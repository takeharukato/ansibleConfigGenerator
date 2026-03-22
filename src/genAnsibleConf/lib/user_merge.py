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
"""users_list と users_authorized_keys の統合処理を提供するモジュールである。"""

from __future__ import annotations

import json
from typing import Any, cast


def dedupe_preserve_order(values: list[Any]) -> list[Any]:
    """リストの重複を順序維持で除去する。

    Args:
        values (list[Any]): 重複除去対象の値配列である。

    Returns:
        list[Any]: 先頭出現順を維持した重複除去後の配列である。

    Examples:
        >>> dedupe_preserve_order([1, 2, 1, 3])
        [1, 2, 3]
    """
    seen: set[str] = set()
    out: list[Any] = []
    for value in values:
        marker: str = json.dumps(value, sort_keys=True, ensure_ascii=False)
        if marker in seen:
            continue
        seen.add(marker)
        out.append(value)
    return out


def merge_users_list(
    global_users: Any,
    node_users: Any,
) -> list[dict[str, Any]]:
    """`users_list` をグローバル定義とノード定義でマージする。

    Args:
        global_users (Any): グローバルの users_list 値である。
        node_users (Any): ノードの users_list 値である。

    Returns:
        list[dict[str, Any]]: `name` キーで統合した users_list である。

    Examples:
        >>> merge_users_list([{"name": "alice", "uid": 1000}], [{"name": "alice", "shell": "/bin/bash"}])[0]["shell"]
        '/bin/bash'
    """
    merged: dict[str, dict[str, Any]] = {}
    order: list[str] = []

    for source in (global_users, node_users):
        if not isinstance(source, list):
            continue
        source_list: list[Any] = cast(list[Any], source)
        for entry_raw in source_list:
            if not isinstance(entry_raw, dict):
                continue
            entry_map: dict[Any, Any] = cast(dict[Any, Any], entry_raw)
            entry: dict[str, Any] = dict(entry_map)
            name: Any = entry.get('name')
            if not isinstance(name, str) or not name:
                continue
            if name not in merged:
                order.append(name)
                merged[name] = entry
            else:
                merged[name].update(entry)

    return [merged[name] for name in order]


def merge_users_authorized_keys(
    global_keys: Any,
    node_keys: Any,
) -> dict[str, list[str]]:
    """`users_authorized_keys` をマージして鍵文字列を重複除去する。

    Args:
        global_keys (Any): グローバルの公開鍵辞書である。
        node_keys (Any): ノードの公開鍵辞書である。

    Returns:
        dict[str, list[str]]: ユーザーごとの統合済み公開鍵辞書である。

    Examples:
        >>> merge_users_authorized_keys({"alice": ["k1"]}, {"alice": ["k1", "k2"]})["alice"]
        ['k1', 'k2']
    """
    out: dict[str, list[str]] = {}

    for source in (global_keys, node_keys):
        if not isinstance(source, dict):
            continue
        source_map: dict[Any, Any] = cast(dict[Any, Any], source)
        for user_raw, keys_raw in source_map.items():
            if not isinstance(user_raw, str):
                continue
            if not isinstance(keys_raw, list):
                continue
            keys_input: list[Any] = cast(list[Any], keys_raw)
            keys: list[str] = [key for key in keys_input if isinstance(key, str)]
            if user_raw not in out:
                out[user_raw] = []
            out[user_raw] = cast(list[str], dedupe_preserve_order(out[user_raw] + keys))

    return out
