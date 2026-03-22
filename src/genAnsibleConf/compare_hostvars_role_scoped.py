#!/usr/bin/env python3
"""host_vars の差分比較スクリプト。

ansible の vars/all-config.yml と host_vars/*.local を読み込み,
Jinja2 変数を即値展開した後, /tmp/hvtest_final/ の生成結果と比較する。

比較ノイズを抑えるため, 次の条件を満たすキーだけを比較対象にする。
1) roles/playbooks/templates で実際に参照されるキー
2) network_topology の role から見て, 対象ホストに適用されるサービススコープのキー
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, cast

from lib.yaml_io import load_yaml_mapping
from lib.service_rules import get_service_disabled_cleanup_keys, load_service_transform_rules_from_section


def parse_args() -> argparse.Namespace:
    """CLI 引数を解析する。

    Returns:
        argparse.Namespace: 解析結果
    """
    parser = argparse.ArgumentParser(
        description="ansible host_vars と生成host_varsの差分を比較する",
    )
    parser.add_argument(
        "--ansible-base",
        type=Path,
        default=Path("ansible"),
        help="ansible ルートディレクトリ (vars/all-config.yml と host_vars/ を含む)",
    )
    parser.add_argument(
        "--generated-dir",
        type=Path,
        default=Path("hvtest_final"),
        help="生成済み host_vars ディレクトリ",
    )
    parser.add_argument(
        "--topology",
        type=Path,
        default=Path("network_topology.yaml"),
        help="network_topology.yaml のパス",
    )
    parser.add_argument(
        "--prototype-root",
        type=Path,
        default=Path(__file__).resolve().parent,
        help="prototype ルートディレクトリ (topology 相対解決用)",
    )
    return parser.parse_args()


# -----------------------------------------------------------------
# Jinja2 変数の即値展開
# -----------------------------------------------------------------

def _build_literal_vars(raw: dict[str, Any]) -> dict[str, str]:
    """スカラー値のみを文字列マップとして返す (ネスト不展開)。"""
    out: dict[str, str] = {}
    for k, v in raw.items():
        if isinstance(v, (str, int, float, bool)):
            out[k] = str(v)
    return out


def _expand(value: Any, var_map: dict[str, str], depth: int = 0) -> Any:
    """Jinja2 {{ }} 参照を再帰的に文字列置換する。"""
    if depth > 20:
        return value
    if isinstance(value, str):
        prev = None
        while prev != value:
            prev = value
            for k, v in var_map.items():
                value = value.replace("{{ " + k + " }}", v)
                value = value.replace("{{" + k + "}}", v)
        return value
    if isinstance(value, list):
        list_value: list[Any] = cast(list[Any], value)
        return [_expand(item, var_map, depth + 1) for item in list_value]
    if isinstance(value, dict):
        dict_value: dict[Any, Any] = cast(dict[Any, Any], value)
        return {
            str(dk): _expand(dv, var_map, depth + 1)
            for dk, dv in dict_value.items()
        }
    return value


def expand_all(data: dict[str, Any]) -> dict[str, Any]:
    """辞書全体の Jinja2 参照を展開する (複数パス)。"""
    var_map: dict[str, str] = {}
    for _ in range(5):
        var_map = _build_literal_vars(data)
        data = {k: _expand(v, var_map) for k, v in data.items()}
    return data


# -----------------------------------------------------------------
# YAML 読み込みと正規化
# -----------------------------------------------------------------

def load_yaml(path: Path) -> dict[str, Any]:
    """YAML を辞書として読み込む。"""
    return load_yaml_mapping(path)


# -----------------------------------------------------------------
# 比較ロジック
# -----------------------------------------------------------------

def normalize_value(v: Any) -> Any:
    """比較のための正規化 (bool/数値文字列/None など)。"""
    if isinstance(v, bool):
        return v
    if isinstance(v, str):
        s = v.strip()
        if s.lower() == "true":
            return True
        if s.lower() == "false":
            return False
        if re.fullmatch(r"-?\d+", s):
            try:
                return int(s)
            except ValueError:
                pass
    if isinstance(v, list):
        list_value: list[Any] = cast(list[Any], v)
        return [normalize_value(i) for i in list_value]
    if isinstance(v, dict):
        dict_value: dict[Any, Any] = cast(dict[Any, Any], v)
        return {str(k): normalize_value(dv) for k, dv in dict_value.items()}
    return v


def _normalize_frr_neighbor_list_without_desc(value: Any) -> Any:
    """FRR neighbor リストを desc 無視・順序非依存で正規化する。"""
    if not isinstance(value, list):
        return normalize_value(value)

    normalized_entries: list[tuple[str, Any]] = []
    entries: list[Any] = cast(list[Any], value)
    for entry in entries:
        if isinstance(entry, dict):
            normalized_map: dict[str, Any] = {}
            for key, raw_val in cast(dict[Any, Any], entry).items():
                key_str: str = str(key)
                if key_str == 'desc':
                    continue
                normalized_map[key_str] = normalize_value(raw_val)
            normalized_entries.append((repr(sorted(normalized_map.items())), normalized_map))
        else:
            normalized_scalar: Any = normalize_value(entry)
            normalized_entries.append((repr(normalized_scalar), normalized_scalar))

    normalized_entries.sort(key=lambda item: item[0])
    return [item[1] for item in normalized_entries]


def _normalize_value_for_key(key: str, value: Any) -> Any:
    """キーごとの比較ポリシーを適用して値を正規化する。"""
    if key in {'frr_networks_v4', 'frr_networks_v6'}:
        if isinstance(value, list):
            normalized_list: list[Any] = [normalize_value(item) for item in cast(list[Any], value)]
            return sorted(normalized_list, key=lambda item: repr(item))
        return normalize_value(value)

    if key in {'frr_ibgp_neighbors', 'frr_ibgp_neighbors_v6'}:
        return _normalize_frr_neighbor_list_without_desc(value)

    return normalize_value(value)


# 既知差分: 照合スキップするキー (ノード名 => キーセット。"*" は全ノード共通)
KNOWN_DIFFS: dict[str, set[str]] = {
    "*": {
        # 意図差分として許容するキー
        "netgauge_enabled",
        "netif_list",
    },
    "k8sctrlplane01.local": {
        # k8s_cilium_cm_cluster_id が数値vs文字列の型差異 (既知)
        "k8s_cilium_cm_cluster_id",
        # hubble_ui_enabled キー名の差異 (既知)
        "hubble_ui_enabled",
        "k8s_hubble_ui_enabled",
    },
    "k8sctrlplane02.local": {
        "k8s_cilium_cm_cluster_id",
        "hubble_ui_enabled",
        "k8s_hubble_ui_enabled",
    },
}


def _build_host_enabled_services(topology: dict[str, Any]) -> dict[str, set[str]]:
    """network_topology からホストごとの有効サービス集合を作る。"""
    globals_def: dict[str, Any] = cast(dict[str, Any], topology.get("globals", {}))
    roles_map_raw: Any = globals_def.get("roles", {})
    roles_map: dict[str, list[str]] = {}
    if isinstance(roles_map_raw, dict):
        roles_map_dict: dict[Any, Any] = cast(dict[Any, Any], roles_map_raw)
        for role_name_raw, svc_list_raw in roles_map_dict.items():
            role_name: str = str(role_name_raw)
            if isinstance(svc_list_raw, list):
                svc_list: list[Any] = cast(list[Any], svc_list_raw)
                roles_map[role_name] = [str(s) for s in svc_list]

    host_services: dict[str, set[str]] = {}
    for node in topology.get("nodes", []):
        if not isinstance(node, dict):
            continue
        node_dict: dict[str, Any] = cast(dict[str, Any], node)
        name: str = str(node_dict.get("name", "")).strip()
        if not name:
            continue
        roles_raw: Any = node_dict.get("roles", [])
        roles_list: list[Any] = cast(list[Any], roles_raw) if isinstance(roles_raw, list) else []
        roles: list[str] = [str(r) for r in roles_list if isinstance(r, str)]
        enabled: set[str] = set()
        for role_name in roles:
            for service_name in roles_map.get(role_name, []):
                enabled.add(str(service_name))
        # 生成host_varsは *.local で比較しているため別名も持つ
        host_services[name] = enabled
        host_services[f"{name}.local"] = enabled
    return host_services


def _build_used_keys_index(ansible_base: Path) -> set[str]:
    """roles/playbook/templates で実際に参照されるキー候補を抽出する。"""
    text_paths: list[Path] = []

    for p in (ansible_base / "roles").rglob("*"):
        if p.is_file() and p.suffix.lower() in {".yml", ".yaml", ".j2", ".py", ".sh"}:
            text_paths.append(p)

    for p in ansible_base.glob("*.yml"):
        if p.is_file():
            text_paths.append(p)

    token_re: re.Pattern[str] = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
    used_tokens: set[str] = set()
    for path in text_paths:
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        for token in token_re.findall(text):
            # 変数名らしいもののみ保持
            if "_" in token:
                used_tokens.add(token)

    return used_tokens


def _build_key_to_service_map() -> dict[str, set[str]]:
    """service_settings YAML ルールからキー→サービスの逆引き辞書を構築する。"""
    rule_config_path: Path = Path(__file__).parent / 'convert-rule-config.yaml'
    rules: dict[str, Any] = load_service_transform_rules_from_section(
        rule_config_path,
        section_key='service_settings',
    )

    key_to_services: dict[str, set[str]] = defaultdict(set)

    # disabled_service_cleanup_keys の各キーを該当サービスに紐付ける。
    scoped: dict[str, set[str]] = get_service_disabled_cleanup_keys(rules)
    service_name: str
    svc_keys: set[str]
    for service_name, svc_keys in scoped.items():
        for key in svc_keys:
            key_to_services[key].add(service_name)

    # key_map の変換後キー（出力側）と enabled_flag を該当サービスに紐付ける。
    services_map: dict[str, Any] = rules.get('services', {})
    service_rule: dict[str, Any]
    for service_name, service_rule in services_map.items():
        key_map: dict[str, str] = service_rule.get('key_map', {})
        out_key: str
        for out_key in key_map.values():
            key_to_services[out_key].add(service_name)
        enabled_flag: str | None = service_rule.get('enabled_flag')
        if enabled_flag:
            key_to_services[enabled_flag].add(service_name)

    # 比較用途の補足マップ: YAML 未収載だが実運用サービス依存のキー。
    explicit_overrides: dict[str, set[str]] = {
        "internal_network_list": {"dns-server"},
        "gpm_mgmt_nic": {"kea-dhcp"},
    }
    override_key: str
    override_services: set[str]
    for override_key, override_services in explicit_overrides.items():
        key_to_services[override_key] |= override_services

    return key_to_services


def _is_key_applicable_for_host(
    key: str,
    host: str,
    key_to_services: dict[str, set[str]],
    host_enabled_services: dict[str, set[str]],
) -> bool:
    """キーがホストに適用されるサービススコープか判定する。"""
    required_services: set[str] | None = key_to_services.get(key)
    if not required_services:
        return True
    enabled: set[str] = host_enabled_services.get(host, set())
    return len(required_services & enabled) > 0


def compare_node(
    node: str,
    ansible_merged: dict[str, Any],
    generated: dict[str, Any],
    used_keys: set[str],
    key_to_services: dict[str, set[str]],
    host_enabled_services: dict[str, set[str]],
    generate_internal_network_list: bool,
) -> list[str]:
    """1ノード分の差分を文字列リストで返す。"""
    diffs: list[str] = []
    skip_keys: set[str] = KNOWN_DIFFS.get("*", set()) | KNOWN_DIFFS.get(node, set())

    # ansible 側に存在するキーで generated 側と異なるものを検出
    for key, ans_val in ansible_merged.items():
        if key == 'internal_network_list' and not generate_internal_network_list:
            continue
        if key in skip_keys:
            continue
        if key not in used_keys:
            continue
        if not _is_key_applicable_for_host(key, node, key_to_services, host_enabled_services):
            continue
        if key not in generated:
            diffs.append(f"  MISSING_IN_GEN  {key}: {ans_val!r}")
            continue
        gen_val = generated[key]
        if _normalize_value_for_key(key, ans_val) != _normalize_value_for_key(key, gen_val):
            diffs.append(
                f"  VALUE_DIFF      {key}:\n"
                f"    ansible: {ans_val!r}\n"
                f"    generated: {gen_val!r}"
            )

    # generated 側にのみ存在するキー
    for key, gen_val in generated.items():
        if key == 'internal_network_list' and not generate_internal_network_list:
            continue
        if key in skip_keys:
            continue
        if key not in used_keys:
            continue
        if not _is_key_applicable_for_host(key, node, key_to_services, host_enabled_services):
            continue
        if key not in ansible_merged:
            diffs.append(f"  EXTRA_IN_GEN    {key}: {gen_val!r}")

    return diffs


# -----------------------------------------------------------------
# メイン
# -----------------------------------------------------------------

def main() -> int:
    args: argparse.Namespace = parse_args()

    ansible_base: Path = args.ansible_base
    generated_dir: Path = args.generated_dir
    prototype_root: Path = args.prototype_root
    topology_path: Path = args.topology
    if not topology_path.is_absolute():
        topology_path = prototype_root / topology_path

    all_config_path: Path = ansible_base / "vars" / "all-config.yml"
    host_vars_dir: Path = ansible_base / "host_vars"

    topology: dict[str, Any] = load_yaml(topology_path)
    globals_def: dict[str, Any] = cast(dict[str, Any], topology.get('globals', {}))
    generate_internal_network_list: bool = bool(globals_def.get('generate_internal_network_list', True))
    host_enabled_services: dict[str, set[str]] = _build_host_enabled_services(topology)
    used_keys: set[str] = _build_used_keys_index(ansible_base)
    key_to_services: dict[str, set[str]] = _build_key_to_service_map()

    # all-config.yml 読み込み・展開
    all_config_raw: dict[str, Any] = load_yaml(all_config_path)
    all_config: dict[str, Any] = expand_all(all_config_raw)

    nodes: list[str] = sorted(p.name for p in host_vars_dir.glob("*.local"))

    total_diffs: int = 0
    for node in nodes:
        ansible_hv_path: Path = host_vars_dir / node
        generated_path: Path = generated_dir / node

        if not generated_path.exists():
            print(f"[SKIP] {node}: 生成ファイルなし")
            continue

        # ansible: all-config + host_vars (host_vars 優先)
        ansible_hv_raw: dict[str, Any] = load_yaml(ansible_hv_path)
        ansible_hv: dict[str, Any] = expand_all(ansible_hv_raw)
        ansible_merged: dict[str, Any] = {**all_config, **ansible_hv}
        ansible_final: dict[str, Any] = expand_all(ansible_merged)

        # generated
        generated_raw: dict[str, Any] = load_yaml(generated_path)
        generated: dict[str, Any] = expand_all(generated_raw)

        diffs: list[str] = compare_node(
            node,
            ansible_final,
            generated,
            used_keys,
            key_to_services,
            host_enabled_services,
            generate_internal_network_list,
        )

        if diffs:
            print(f"\n{'='*60}")
            print(f"[DIFF] {node}  ({len(diffs)} 件)")
            print(f"{'='*60}")
            for d in diffs:
                print(d)
            total_diffs += len(diffs)
        else:
            print(f"[OK]   {node}")

    print(f"\n--- 合計差分件数: {total_diffs} ---")
    return 0 if total_diffs == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
