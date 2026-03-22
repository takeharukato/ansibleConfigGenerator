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
"""ネットワーク基礎計算を提供するモジュールである。"""

from __future__ import annotations

import ipaddress


def calculate_prefix_len(cidr: str) -> int:
    """CIDR 文字列からプレフィックス長を算出する。

    Args:
        cidr (str): CIDR 表記のネットワーク文字列である。

    Returns:
        int: プレフィックス長である。

    Raises:
        ValueError: CIDR 文字列が不正な場合に送出する。

    Examples:
        >>> calculate_prefix_len("192.168.20.0/24")
        24
        >>> calculate_prefix_len("fd69:6684:61a:1::/64")
        64
    """
    network: ipaddress.IPv4Network | ipaddress.IPv6Network = ipaddress.ip_network(cidr, strict=False)
    return network.prefixlen
