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
"""prototype 生成系の回帰固定化テスト。"""

from __future__ import annotations

import sys
import csv
from pathlib import Path
from typing import Any, Callable, cast

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
SOURCE_DIR: Path = REPO_ROOT / "src"
PROTOTYPE_DIR: Path = SOURCE_DIR / "genAnsibleConf"
SAMPLE_TOPOLOGY_PATH: Path = REPO_ROOT / "config" / "sample-network_topology.yaml"
if str(SOURCE_DIR) not in sys.path:
    sys.path.insert(0, str(SOURCE_DIR))

from genAnsibleConf.cli import generate_host_vars_files as host_vars_files_module
from genAnsibleConf.cli import generate_host_vars_structured as host_vars_structured_module
from genAnsibleConf.cli import generate_hostvars_matrix as hostvars_matrix_module
from genAnsibleConf.cli import generate_terraform_tfvars as terraform_tfvars_module
from genAnsibleConf.cli import validate_hostvars_matrix as validate_matrix_module
from genAnsibleConf.lib.yaml_io import load_yaml_mapping

GenerateHostVarsStructuredType = Callable[[dict[str, Any]], dict[str, Any]]
RenderTfvarsType = Callable[[dict[str, Any], dict[str, dict[str, Any]], dict[str, list[str]]], str]
GenerateHostVarFilesType = Callable[..., list[dict[str, Any]]]
ValidateRoundtripType = Callable[..., tuple[bool, list[str]]]
GenerateCsvType = Callable[[str, str, str | None], str]
ValidateCsvType = Callable[[str, str, str], tuple[bool, list[str]]]

host_vars_structured_module_any: Any = host_vars_structured_module
terraform_tfvars_module_any: Any = terraform_tfvars_module
host_vars_files_module_any: Any = host_vars_files_module
hostvars_matrix_module_any: Any = hostvars_matrix_module
validate_matrix_module_any: Any = validate_matrix_module

generate_host_vars_structured: GenerateHostVarsStructuredType = cast(
    GenerateHostVarsStructuredType,
    host_vars_structured_module_any.generate_host_vars_structured,
)
render_tfvars: RenderTfvarsType = cast(
    RenderTfvarsType,
    terraform_tfvars_module_any.render_tfvars,
)
generate_host_var_files: GenerateHostVarFilesType = cast(
    GenerateHostVarFilesType,
    host_vars_files_module_any.generate_host_var_files,
)
validate_roundtrip: ValidateRoundtripType = cast(
    ValidateRoundtripType,
    host_vars_files_module_any.validate_roundtrip,
)
generate_csv: GenerateCsvType = cast(
    GenerateCsvType,
    hostvars_matrix_module_any.generate_csv,
)
validate_csv: ValidateCsvType = cast(
    ValidateCsvType,
    validate_matrix_module_any.validate_csv,
)


def _prototype_file(name: str) -> Path:
    """prototype 配下ファイルの絶対パスを返す。"""
    if name == "network_topology.yaml":
        return SAMPLE_TOPOLOGY_PATH
    return PROTOTYPE_DIR / name


import pytest

@pytest.fixture(scope="session")
def host_vars_structured_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """network_topology.yaml から host_vars_structured.yaml を生成して返す。

    host_vars_structured.yaml がリポジトリに存在しないため,
    テストセッション開始時に一度だけ生成する。
    """
    import yaml
    topology: dict[str, Any] = load_yaml_mapping(_prototype_file("network_topology.yaml"))
    structured: dict[str, Any] = generate_host_vars_structured(topology)
    out: Path = tmp_path_factory.mktemp("data") / "host_vars_structured.yaml"
    out.write_text(yaml.dump(structured, allow_unicode=True, default_flow_style=False), encoding="utf-8")
    return out


def test_generate_host_vars_structured_from_network_topology() -> None:
    """network_topology から host_vars_structured を生成できる。"""
    topology: dict[str, Any] = load_yaml_mapping(_prototype_file("network_topology.yaml"))

    generated: dict[str, Any] = generate_host_vars_structured(topology)

    hosts_raw: Any = generated.get("hosts")
    assert isinstance(hosts_raw, list)
    hosts: list[Any] = cast(list[Any], hosts_raw)
    assert len(hosts) > 0
    first_host: dict[str, Any] = hosts[0]
    assert isinstance(first_host.get("hostname"), str)


def test_render_tfvars_contains_expected_blocks() -> None:
    """Terraform tfvars レンダラーが主要ブロックを出力する。"""
    env_config: dict[str, Any] = {
        "xoa_url": "ws://xoa.example.local",
        "xoa_username": "admin@admin.net",
        "xoa_insecure": True,
        "xcpng_pool_name": "pool01",
        "xcpng_sr_name": "Local storage",
        "xcpng_template_ubuntu": "ubuntu-vm",
        "xcpng_template_rhel": "rhel-vm",
        "xcpng_vm_vcpus": 4,
        "xcpng_vm_mem_mb": 4096,
        "xcpng_vm_disk_gb": 25,
        "network_names": {"ext_mgmt": "External Mgmt"},
        "network_options": {},
        "vm_group_defaults": {
            "infrastructure": {
                "default_template_type": "ubuntu",
                "default_firmware": "uefi",
            }
        },
    }
    vm_groups: dict[str, dict[str, Any]] = {}
    network_roles: dict[str, list[str]] = {
        "external_control_plane_network": ["ext_mgmt"],
    }

    rendered: str = render_tfvars(env_config, vm_groups, network_roles)

    assert "network_names = {" in rendered
    assert "network_roles = {" in rendered
    assert "vm_groups = {" in rendered


def test_generate_host_var_files_roundtrip_with_prototype_data(
    tmp_path: Path, host_vars_structured_file: Path
) -> None:
    """host_vars ファイル生成後に roundtrip 検証が通る。"""
    output_dir: Path = tmp_path / "host_vars"

    host_entries: list[dict[str, Any]] = generate_host_var_files(
        input_structured=host_vars_structured_file,
        metadata_file=_prototype_file("field_metadata.yaml"),
        output_dir=output_dir,
        overwrite=True,
    )
    ok: bool
    errors: list[str]
    ok, errors = validate_roundtrip(output_dir, host_entries)

    assert len(host_entries) > 0
    assert ok is True
    assert errors == []


def test_generate_and_validate_hostvars_matrix_csv(
    tmp_path: Path, host_vars_structured_file: Path
) -> None:
    """matrix CSV 生成結果が validator で整合する。"""
    output_csv: Path = tmp_path / "host_vars_scalars_matrix.csv"

    _ = generate_csv(
        str(host_vars_structured_file),
        str(_prototype_file("field_metadata.yaml")),
        str(output_csv),
    )

    is_valid: bool
    errors: list[str]
    is_valid, errors = validate_csv(
        str(output_csv),
        str(_prototype_file("field_metadata.yaml")),
        str(host_vars_structured_file),
    )

    assert output_csv.exists()
    assert is_valid is True
    assert errors == []


def test_generate_csv_includes_top_level_list_fields(
    tmp_path: Path, host_vars_structured_file: Path
) -> None:
    """generate_csv がトップレベルリストフィールドを出力する。

    frr_networks_v4 はスカラー以外のトップレベルリストであり,
    2段階ルックアップにより空欄にならないことを確認する。
    """
    output_csv: Path = tmp_path / "test_matrix.csv"
    _ = generate_csv(
        str(host_vars_structured_file),
        str(_prototype_file("field_metadata.yaml")),
        str(output_csv),
    )
    content: str = output_csv.read_text(encoding="utf-8")
    rows: list[list[str]] = list(csv.reader(content.splitlines()))

    frr_row: list[str] | None = next(
        (row for row in rows if row and row[0] == "frr_networks_v4"),
        None,
    )
    assert frr_row is not None, "frr_networks_v4 row must exist"
    host_values: list[str] = frr_row[4:]
    assert any(
        v != "" for v in host_values
    ), "frr_networks_v4 must have non-empty values for at least one host"


def test_generate_csv_uses_stringify_for_scalar_lists(
    tmp_path: Path, host_vars_structured_file: Path
) -> None:
    """generate_csv がスカラー内リストをセミコロン区切りで直列化する。

    users_list はスカラー内のリストであり, Python repr ではなく
    セミコロン区切り文字列として出力されることを確認する。
    """
    output_csv: Path = tmp_path / "test_matrix.csv"
    _ = generate_csv(
        str(host_vars_structured_file),
        str(_prototype_file("field_metadata.yaml")),
        str(output_csv),
    )
    content: str = output_csv.read_text(encoding="utf-8")
    rows: list[list[str]] = list(csv.reader(content.splitlines()))

    users_row: list[str] | None = next(
        (row for row in rows if row and row[0] == "users_list"),
        None,
    )
    assert users_row is not None, "users_list row must exist"
    host_values: list[str] = users_row[4:]
    non_empty: list[str] = [v for v in host_values if v != ""]
    assert len(non_empty) > 0, "users_list must have non-empty values for at least one host"
    # Python repr ('[{...}]') ではなく JSON/セミコロン区切りになっていること
    for val in non_empty:
        assert not val.startswith("[{"), (
            f"users_list value should not be Python repr, got: {val!r}"
        )


def test_generate_csv_includes_netif_rows(
    tmp_path: Path, host_vars_structured_file: Path
) -> None:
    """generate_csv が netif_list 展開行を出力する。

    netif_list[{IF名}].static_ipv4_addr 形式の行が存在し,
    少なくとも1ホストで非空値を持つことを確認する。
    """
    output_csv: Path = tmp_path / "test_matrix.csv"
    _ = generate_csv(
        str(host_vars_structured_file),
        str(_prototype_file("field_metadata.yaml")),
        str(output_csv),
    )
    content: str = output_csv.read_text(encoding="utf-8")
    rows: list[list[str]] = list(csv.reader(content.splitlines()))
    field_names: list[str] = [row[0] for row in rows[1:] if row]

    assert any(
        f.startswith("netif_list[") and f.endswith("].static_ipv4_addr")
        for f in field_names
    ), "netif_list expansion rows for static_ipv4_addr must exist"

    netif_ip_row: list[str] | None = next(
        (row for row in rows[1:] if row and row[0].endswith("].static_ipv4_addr")),
        None,
    )
    assert netif_ip_row is not None
    host_values: list[str] = netif_ip_row[4:]
    assert any(
        v != "" for v in host_values
    ), "netif expansion row must have IP value for at least one host"
