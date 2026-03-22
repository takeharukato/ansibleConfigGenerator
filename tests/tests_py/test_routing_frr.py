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
"""routing_frr の単体テスト。"""

from __future__ import annotations

from typing import Any

from src.genAnsibleConf.lib.routing_frr import (
    apply_worker_frr_autocalculated_fields,
    build_default_k8s_worker_frr,
    build_frr_ebgp_neighbors,
    build_frr_ibgp_neighbors,
    build_frr_networks,
    prepare_frr_runtime_flags,
)


def test_build_frr_ebgp_neighbors_adds_remote_dc_rr() -> None:
    """route reflector で eBGP 自動メッシュ有効時に他 DC RR を収集することを検証する。"""
    node: dict[str, Any] = {"name": "rr-a", "datacenter": "dc-a"}
    datacenters: dict[str, dict[str, Any]] = {
        "dc-a": {"asn": 65001, "route_reflector": "rr-a"},
        "dc-b": {"asn": 65002, "route_reflector": "rr-b"},
    }
    rr_b: dict[str, Any] = {
        "name": "rr-b",
        "interfaces": [{"network": "tr1", "static_ipv4_addr": "172.16.0.2"}],
    }
    node_map: dict[str, dict[str, Any]] = {"rr-b": rr_b}
    networks: dict[str, dict[str, Any]] = {"tr1": {"role": "bgp_transport_network"}}

    ebgp_v4, ebgp_v6 = build_frr_ebgp_neighbors(
        node,
        datacenters,
        node_map,
        networks,
        auto_meshed_ebgp_transport_enabled=True,
    )

    assert len(ebgp_v4) == 1
    assert ebgp_v4[0]["addr"] == "172.16.0.2"
    assert ebgp_v4[0]["asn"] == 65002
    assert ebgp_v6 == []


def test_build_frr_ibgp_neighbors_for_worker_points_to_dc_rr() -> None:
    """worker ノードで同一 DC/cluster の RR を iBGP neighbor として取得することを検証する。"""
    worker: dict[str, Any] = {
        "name": "wk1",
        "hostname_fqdn": "wk1.local",
        "roles": ["k8s_worker"],
        "datacenter": "dc1",
        "cluster": "c1",
    }
    rr_node: dict[str, Any] = {
        "name": "rr1",
        "hostname_fqdn": "rr1.local",
        "interfaces": [
            {
                "network": "dp1",
                "static_ipv4_addr": "10.10.0.1",
                "static_ipv6_addr": "fd10::1",
            }
        ],
    }
    datacenters: dict[str, dict[str, Any]] = {
        "dc1": {"asn": 65100, "route_reflector": "rr1"}
    }
    node_map: dict[str, dict[str, Any]] = {"rr1": rr_node, "wk1": worker}
    networks: dict[str, dict[str, Any]] = {
        "dp1": {"role": "data_plane_network", "datacenter": "dc1", "cluster": "c1"}
    }

    ibgp_v4, ibgp_v6 = build_frr_ibgp_neighbors(
        worker,
        datacenters,
        cluster_membership={},
        node_map=node_map,
        networks=networks,
    )

    assert ibgp_v4[0]["addr"] == "10.10.0.1"
    assert ibgp_v4[0]["asn"] == 65100
    assert "rr1.local" in ibgp_v4[0]["desc"]
    assert ibgp_v6[0]["addr"] == "fd10::1"


def test_build_frr_ibgp_neighbors_uses_injected_cluster_routing_capability() -> None:
    """route reflector 側で注入した ClusterRoutingCapability が使われることを検証する。"""

    class DummyClusterRoutingCapability:
        """テスト用の固定 iBGP ネイバー追加実装である。"""

        def add_cluster_ibgp_neighbors(
            self,
            target_node: dict[str, Any],
            networks: dict[str, dict[str, Any]],
            asn: int,
            cluster_id: str,
            cluster_name: str,
            ibgp_v4: list[dict[str, Any]],
            ibgp_v6: list[dict[str, Any]],
            role_desc: str,
        ) -> None:
            del target_node, networks, cluster_id, cluster_name
            ibgp_v4.append({
                "addr": "198.51.100.10",
                "asn": asn,
                "desc": f"dummy-{role_desc}",
            })
            ibgp_v6.append({
                "addr": "2001:db8::10",
                "asn": asn,
                "desc": f"dummy-{role_desc}",
            })

    rr_node: dict[str, Any] = {"name": "rr1", "datacenter": "dc1"}
    cp_node: dict[str, Any] = {
        "name": "cp1",
        "hostname_fqdn": "cp1.local",
        "datacenter": "dc1",
        "scalars": {"k8s_cilium_cm_cluster_name": "cluster1"},
    }
    datacenters: dict[str, dict[str, Any]] = {"dc1": {"asn": 65100, "route_reflector": "rr1"}}
    cluster_membership: dict[str, dict[str, Any]] = {
        "c1": {"control_plane": "cp1", "workers": [], "datacenter": "dc1"}
    }
    node_map: dict[str, dict[str, Any]] = {"rr1": rr_node, "cp1": cp_node}

    ibgp_v4, ibgp_v6 = build_frr_ibgp_neighbors(
        rr_node,
        datacenters,
        cluster_membership,
        node_map,
        networks={},
        cluster_routing_capability=DummyClusterRoutingCapability(),
    )

    assert ibgp_v4 == [{"addr": "198.51.100.10", "asn": 65100, "desc": "dummy-control-plane"}]
    assert ibgp_v6 == [{"addr": "2001:db8::10", "asn": 65100, "desc": "dummy-control-plane"}]



def test_build_frr_networks_collects_only_advertise_roles_in_same_dc() -> None:
    """同一 DC 内で広告対象 role のネットワークのみを収集することを検証する。"""
    rr_node: dict[str, Any] = {"name": "rr1", "datacenter": "dc1"}
    datacenters: dict[str, dict[str, Any]] = {
        "dc1": {"asn": 65100, "route_reflector": "rr1"}
    }
    nodes: list[dict[str, Any]] = [
        {
            "name": "wk1",
            "datacenter": "dc1",
            "interfaces": [{"network": "dp1"}, {"network": "bgp1"}],
        },
        {
            "name": "ext1",
            "datacenter": "dc2",
            "interfaces": [{"network": "dp2"}],
        },
    ]
    networks: dict[str, dict[str, Any]] = {
        "dp1": {"role": "data_plane_network", "ipv4_cidr": "10.10.0.0/24"},
        "bgp1": {"role": "bgp_transport_network", "ipv4_cidr": "172.16.0.0/24"},
        "dp2": {"role": "data_plane_network", "ipv4_cidr": "10.20.0.0/24"},
    }

    nets_v4, nets_v6 = build_frr_networks(
        rr_node,
        datacenters,
        networks,
        nodes,
        frr_advertise_roles={"data_plane_network", "bgp_transport_network"},
    )

    assert nets_v4 == ["172.16.0.0/24", "10.10.0.0/24"]
    assert nets_v6 == []


def test_build_default_k8s_worker_frr_includes_rr_and_host_routes() -> None:
    """worker の既定 FRR 生成で RR と host route が補完されることを検証する。"""
    worker: dict[str, Any] = {
        "name": "wk1",
        "hostname_fqdn": "wk1.local",
        "roles": ["k8s_worker"],
        "cluster": "c1",
        "datacenter": "dc1",
        "interfaces": [
            {
                "network": "dp1",
                "static_ipv4_addr": "10.0.0.10",
                "static_ipv6_addr": "fd00::10",
            }
        ],
        "scalars": {
            "k8s_cilium_cm_cluster_name": "cluster1",
            "k8s_pod_ipv4_network_cidr": "10.244.0.0/16",
            "k8s_pod_ipv4_service_subnet": "10.96.0.0/16",
        },
    }
    route_reflector: dict[str, Any] = {
        "name": "rr1",
        "hostname_fqdn": "rr1.local",
        "interfaces": [
            {
                "network": "dp1",
                "static_ipv4_addr": "10.0.0.1",
                "static_ipv6_addr": "fd00::1",
            }
        ],
    }
    datacenters: dict[str, dict[str, Any]] = {"dc1": {"asn": 65010, "route_reflector": "rr1"}}
    node_map: dict[str, dict[str, Any]] = {"rr1": route_reflector, "wk1": worker}
    networks: dict[str, dict[str, Any]] = {
        "dp1": {"role": "data_plane_network", "datacenter": "dc1", "cluster": "c1"}
    }

    actual: dict[str, Any] = build_default_k8s_worker_frr(worker, datacenters, node_map, networks)

    assert actual["local_asn"] == 65010
    assert actual["dc_frr_addresses"] == {"rr1.local": "10.0.0.1"}
    assert actual["advertise_host_route_ipv4"] == "10.0.0.10/32"
    assert actual["cluster_name"] == "cluster1"


def test_apply_worker_frr_autocalculated_fields_does_not_overwrite_existing() -> None:
    """既存フィールドを上書きしないことを検証する。"""
    worker: dict[str, Any] = {
        "name": "wk1",
        "hostname_fqdn": "wk1.local",
        "datacenter": "dc1",
        "cluster": "c1",
        "interfaces": [{"network": "dp1", "static_ipv4_addr": "10.0.0.10"}],
        "scalars": {},
    }
    route_reflector: dict[str, Any] = {
        "name": "rr1",
        "hostname_fqdn": "rr1.local",
        "interfaces": [{"network": "dp1", "static_ipv4_addr": "10.0.0.1"}],
    }
    datacenters: dict[str, dict[str, Any]] = {"dc1": {"asn": 65010, "route_reflector": "rr1"}}
    node_map: dict[str, dict[str, Any]] = {"rr1": route_reflector, "wk1": worker}
    networks: dict[str, dict[str, Any]] = {
        "dp1": {"role": "data_plane_network", "datacenter": "dc1", "cluster": "c1"}
    }

    existing_frr: dict[str, Any] = {"dc_frr_addresses": {"existing.rr": "192.168.1.1"}}
    result: dict[str, Any] = apply_worker_frr_autocalculated_fields(
        worker, existing_frr, datacenters, node_map, networks
    )

    assert result["dc_frr_addresses"] == {"existing.rr": "192.168.1.1"}
    assert result["advertise_host_route_ipv4"] == "10.0.0.10/32"


def test_prepare_frr_runtime_flags_returns_datacenters_and_flag() -> None:
    """`prepare_frr_runtime_flags` が datacenters と eBGP フラグを返すことを検証する。"""
    globals_def: dict[str, Any] = {
        "datacenters": {"dc1": {"asn": 65001}},
        "auto_meshed_ebgp_transport_enabled": False,
    }

    datacenters, flag = prepare_frr_runtime_flags(globals_def)

    assert datacenters == {"dc1": {"asn": 65001}}
    assert flag is False
