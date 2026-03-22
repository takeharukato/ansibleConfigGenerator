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
"""netif_builder の単体テスト。"""

from __future__ import annotations

from typing import Any

import pytest

from src.genAnsibleConf.lib.netif_builder import build_netif_list, derive_nic_variables


def test_derive_nic_variables_assigns_reserved_dual_management_pair() -> None:
    """外部/内部管理 NIC の2本構成で予約ペア検証が通ることを検証する。"""
    node: dict[str, Any] = {
        "name": "node01",
        "roles": ["k8s_worker"],
        "datacenter": "dc1",
        "cluster": "c1",
        "interfaces": [
            {"netif": "eth0", "network": "mgmt_ext"},
            {"netif": "eth1", "network": "mgmt_int"},
            {"netif": "eth2", "network": "dp1"},
        ],
    }
    networks: dict[str, dict[str, Any]] = {
        "mgmt_ext": {"role": "external_control_plane_network"},
        "mgmt_int": {"role": "private_control_plane_network"},
        "dp1": {"role": "data_plane_network", "datacenter": "dc1", "cluster": "c1"},
    }

    actual: dict[str, str] = derive_nic_variables(
        node,
        networks,
        reserved_pairs=[("eth0", "eth1")],
        internal_mgmt_role="private_control_plane_network",
        external_mgmt_role="external_control_plane_network",
        data_plane_roles={"data_plane_network"},
    )

    assert actual["mgmt_nic"] == "eth0"
    assert actual["gpm_mgmt_nic"] == "eth1"
    assert actual["k8s_nic"] == "eth2"
    assert actual["k8s_kubelet_nic"] == "eth0"


def test_derive_nic_variables_rejects_non_reserved_management_nic() -> None:
    """予約セット外の管理 NIC 名を拒否することを検証する。"""
    node: dict[str, Any] = {
        "name": "node02",
        "interfaces": [{"netif": "ens192", "network": "mgmt_int"}],
    }
    networks: dict[str, dict[str, Any]] = {
        "mgmt_int": {"role": "private_control_plane_network"}
    }

    with pytest.raises(ValueError):
        derive_nic_variables(
            node,
            networks,
            reserved_pairs=[("eth0", "eth1")],
            internal_mgmt_role="private_control_plane_network",
            external_mgmt_role="external_control_plane_network",
            data_plane_roles={"data_plane_network"},
        )


def test_build_netif_list_uses_gateway_node_for_private_network() -> None:
    """外部管理網がない場合に gateway_node から private gateway を解決することを検証する。"""
    node: dict[str, Any] = {
        "name": "wk1",
        "interfaces": [
            {
                "netif": "eth1",
                "network": "mgmt_int",
                "static_ipv4_addr": "192.168.10.20",
            }
        ],
    }
    gateway_node: dict[str, Any] = {
        "name": "gw1",
        "interfaces": [
            {
                "netif": "eth1",
                "network": "mgmt_int",
                "static_ipv4_addr": "192.168.10.1",
            }
        ],
    }
    node_map: dict[str, dict[str, Any]] = {"gw1": gateway_node}
    networks: dict[str, dict[str, Any]] = {
        "mgmt_int": {
            "role": "private_control_plane_network",
            "ipv4_cidr": "192.168.10.0/24",
            "gateway_node": "gw1",
            "name_servers_ipv4": ["192.168.10.53"],
        }
    }

    netif_list: list[dict[str, Any]] = build_netif_list(node, networks, node_map)

    assert len(netif_list) == 1
    assert netif_list[0]["gateway4"] == "192.168.10.1"
    assert netif_list[0]["network_ipv4_prefix_len"] == 24
    assert netif_list[0]["name_server_ipv4_1"] == "192.168.10.53"
