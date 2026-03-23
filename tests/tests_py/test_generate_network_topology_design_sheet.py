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
"""generate_network_topology_design_sheet のテスト。"""

from __future__ import annotations

import argparse
import csv
import io
import sys
from pathlib import Path
from typing import Any, Callable, cast

import pytest

REPO_ROOT: Path = Path(__file__).resolve().parents[2]
PROTOTYPE_DIR: Path = REPO_ROOT / "src" / "genAnsibleConf"
SAMPLE_TOPOLOGY_PATH: Path = REPO_ROOT / "config" / "sample-network_topology.yaml"
if str(PROTOTYPE_DIR) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_DIR))

import generate_network_topology_design_sheet as sheet_module  # type: ignore[import-not-found]

sheet_module_any: Any = sheet_module

ParseArgsType = Callable[[], argparse.Namespace]
GenerateCsvType = Callable[[str, str, str | None], list[str]]

parse_args_typed: ParseArgsType = cast(ParseArgsType, sheet_module_any.parse_args)
generate_csv_typed: GenerateCsvType = cast(GenerateCsvType, sheet_module_any.generate_design_sheet_csv)


def _prototype_file(name: str) -> Path:
    """prototype 配下ファイルの絶対パスを返す。"""
    if name == "network_topology.yaml":
        return SAMPLE_TOPOLOGY_PATH
    return PROTOTYPE_DIR / name


def _expected_sheet_path(base_dir: Path, topology_path: Path, section: str) -> Path:
    """入力トポロジーの stem から期待される出力 CSV パスを返す。"""
    return base_dir / f"{topology_path.stem}-{section}.csv"


def test_parse_args_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    """引数未指定時のデフォルト値を検証する。"""
    monkeypatch.setattr(sys, "argv", ["generate_network_topology_design_sheet.py"])

    args_any: Any = parse_args_typed()

    assert cast(str, args_any.input) == "network_topology.yaml"
    assert cast(str, args_any.output) == "network_topology.csv"
    assert cast(str, args_any.metadata) == "network_topology.schema.yaml"


def test_generate_csv_has_all_sections(tmp_path: Path) -> None:
    """CSV出力として4つのセクション別ファイルが生成される。"""
    output_base: str = str(tmp_path / "design_sheet")
    topology_path: Path = _prototype_file("network_topology.yaml")

    missing_paths: list[str]
    missing_paths = generate_csv_typed(
        str(topology_path),
        str(_prototype_file("network_topology.schema.yaml")),
        output_base,
    )

    assert _expected_sheet_path(tmp_path, topology_path, "globals").exists()
    assert _expected_sheet_path(tmp_path, topology_path, "roles").exists()
    assert _expected_sheet_path(tmp_path, topology_path, "services").exists()
    assert _expected_sheet_path(tmp_path, topology_path, "hosts").exists()
    assert isinstance(missing_paths, list)


def test_services_section_outputs_empty_config_row(tmp_path: Path) -> None:
    """config空オブジェクトのサービス行を出力する。"""
    output_base: str = str(tmp_path / "design_sheet")
    topology_path: Path = _prototype_file("network_topology.yaml")

    missing_paths: list[str]
    missing_paths = generate_csv_typed(
        str(topology_path),
        str(_prototype_file("network_topology.schema.yaml")),
        output_base,
    )

    services_csv = _expected_sheet_path(tmp_path, topology_path, "services")
    assert services_csv.exists()

    csv_text = services_csv.read_text(encoding="utf-8")
    reader = csv.reader(io.StringIO(csv_text))
    target_rows = [row for row in reader if len(row) >= 2 and row[0] == "hubble_cli" and row[1] == "config"]

    assert target_rows
    assert any(row[1] == "config" and row[3] == "" for row in target_rows)
    assert isinstance(missing_paths, list)


def test_services_section_uses_individual_description_from_field_metadata(tmp_path: Path) -> None:
    """servicesセクションで個別descriptionを出力する。"""
    output_base: str = str(tmp_path / "design_sheet")
    topology_path: Path = _prototype_file("network_topology.yaml")

    _ = generate_csv_typed(
        str(topology_path),
        str(_prototype_file("network_topology.schema.yaml")),
        output_base,
    )

    services_csv = _expected_sheet_path(tmp_path, topology_path, "services")
    assert services_csv.exists()

    rows: list[list[str]] = list(csv.reader(io.StringIO(services_csv.read_text(encoding="utf-8"))))
    data_rows: list[list[str]] = [row for row in rows[1:] if len(row) >= 4]

    gitlab_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "gitlab" and row[1] == "config.gitlab_backup_rotation"),
        None,
    )
    assert gitlab_row is not None
    assert gitlab_row[2] == "GitLabバックアップ世代数"

    dns_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "dns-server" and row[1] == "config.dns_domain"),
        None,
    )
    assert dns_row is not None
    assert dns_row[2] == "管理ドメイン名"


def test_globals_scalars_uses_individual_description_from_field_metadata(tmp_path: Path) -> None:
    """globals.scalars は field_metadata の個別descriptionを出力する。"""
    output_base: str = str(tmp_path / "design_sheet")
    topology_path: Path = _prototype_file("network_topology.yaml")

    _ = generate_csv_typed(
        str(topology_path),
        str(_prototype_file("network_topology.schema.yaml")),
        output_base,
    )

    globals_csv = _expected_sheet_path(tmp_path, topology_path, "globals")
    assert globals_csv.exists()

    rows: list[list[str]] = list(csv.reader(io.StringIO(globals_csv.read_text(encoding="utf-8"))))
    data_rows: list[list[str]] = [row for row in rows[1:] if len(row) >= 4]

    timezone_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "common_timezone" and row[1] == "globals.scalars.common_timezone"),
        None,
    )
    assert timezone_row is not None
    assert timezone_row[2] == "システムタイムゾーン"


def test_roles_section_uses_individual_description_from_field_metadata(tmp_path: Path) -> None:
    """rolesセクションで role ごとの個別descriptionを出力する。"""
    output_base: str = str(tmp_path / "design_sheet")
    topology_path: Path = _prototype_file("network_topology.yaml")

    _ = generate_csv_typed(
        str(topology_path),
        str(_prototype_file("network_topology.schema.yaml")),
        output_base,
    )

    roles_csv = _expected_sheet_path(tmp_path, topology_path, "roles")
    assert roles_csv.exists()

    rows: list[list[str]] = list(csv.reader(io.StringIO(roles_csv.read_text(encoding="utf-8"))))
    data_rows: list[list[str]] = [row for row in rows[1:] if len(row) >= 4]

    k8s_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "k8s_control_plane" and row[1] == "service_list"),
        None,
    )
    assert k8s_row is not None
    assert k8s_row[2] == "Kubernetesコントロールプレーンノード向けサービス一覧"

    infra_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "infra_server" and row[1] == "service_list"),
        None,
    )
    assert infra_row is not None
    assert infra_row[2] == "インフラサーバ向けサービス一覧"


def test_missing_description_is_reported_and_csv_description_is_blank(tmp_path: Path) -> None:
    """description欠落時は警告対象として収集し, CSV descriptionは空欄になる。"""
    topology_path: Path = tmp_path / "topo.yaml"
    schema_path: Path = tmp_path / "schema.yaml"
    output_base: str = str(tmp_path / "design_sheet")

    topology_path.write_text(
        """
version: 2
globals:
  networks: {}
  datacenters: {}
  scalars:
    custom_key: custom_value
nodes:
  - name: n1
    hostname_fqdn: n1.local
    roles: [base]
    interfaces:
      - netif: eth0
""".strip()
        + "\n",
        encoding="utf-8",
    )

    schema_path.write_text(
        """
type: object
properties:
  version:
    type: integer
""".strip()
        + "\n",
        encoding="utf-8",
    )

    missing_paths: list[str]
    missing_paths = generate_csv_typed(
        str(topology_path),
        str(schema_path),
        output_base,
    )

    assert "globals.scalars.custom_key" in missing_paths

    globals_csv = tmp_path / "topo-globals.csv"
    assert globals_csv.exists()

    csv_text = globals_csv.read_text(encoding="utf-8")
    reader = csv.reader(io.StringIO(csv_text))
    scalar_rows = [
        row for row in reader
        if len(row) >= 4 and row[0] == "custom_key" and row[1] == "globals.scalars.custom_key"
    ]
    assert scalar_rows
    assert scalar_rows[0][2] == ""


def test_hosts_section_uses_joined_parameter_name(tmp_path: Path) -> None:
    """hostsセクションは row_kind.parameter を parameter 列として出力する。"""
    output_base: str = str(tmp_path / "design_sheet")
    topology_path: Path = _prototype_file("network_topology.yaml")

    _ = generate_csv_typed(
        str(topology_path),
        str(_prototype_file("network_topology.schema.yaml")),
        output_base,
    )

    hosts_csv = _expected_sheet_path(tmp_path, topology_path, "hosts")
    assert hosts_csv.exists()

    csv_text = hosts_csv.read_text(encoding="utf-8")
    reader = csv.reader(io.StringIO(csv_text))
    rows: list[list[str]] = list(reader)

    assert rows
    assert rows[0][0:2] == ["parameter", "description"]

    data_rows: list[list[str]] = [row for row in rows[1:] if len(row) >= 2]
    assert data_rows
    assert any(row[0] == "host_node.name" for row in data_rows)


def test_hosts_section_uses_individual_description_from_field_metadata(tmp_path: Path) -> None:
    """hostsセクションは field_metadata の個別descriptionを優先して出力する。"""
    output_base: str = str(tmp_path / "design_sheet")
    topology_path: Path = _prototype_file("network_topology.yaml")

    _ = generate_csv_typed(
        str(topology_path),
        str(_prototype_file("network_topology.schema.yaml")),
        output_base,
    )

    hosts_csv: Path = _expected_sheet_path(tmp_path, topology_path, "hosts")
    rows: list[list[str]] = list(csv.reader(io.StringIO(hosts_csv.read_text(encoding="utf-8"))))
    data_rows: list[list[str]] = [row for row in rows[1:] if len(row) >= 2]

    scalar_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "host_scalar.scalars.frr_bgp_asn"),
        None,
    )
    assert scalar_row is not None
    assert scalar_row[1] == "FRR BGP 自律システム番号"

    service_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "host_service.services.gitlab.config.hostname"),
        None,
    )
    assert service_row is not None
    assert service_row[1] == "GitLabサービスの公開ホスト名"


def test_hosts_section_falls_back_to_parent_description_when_metadata_missing(tmp_path: Path) -> None:
    """metadata未定義キーは親descriptionへフォールバックする。"""
    topology_path: Path = tmp_path / "topo.yaml"
    output_base: str = str(tmp_path / "design_sheet")

    topology_path.write_text(
        "version: 2\n"
        "globals:\n"
        "  networks: {}\n"
        "  datacenters: {}\n"
        "  services: {}\n"
        "nodes:\n"
        "  - name: n1\n"
        "    hostname_fqdn: n1.local\n"
        "    roles: [base]\n"
        "    interfaces:\n"
        "      - netif: eth0\n"
        "    scalars:\n"
        "      unknown_scalar_key: custom\n"
        "    services:\n"
        "      unknown_service:\n"
        "        config:\n"
        "          unknown_config_key: value\n",
        encoding="utf-8",
    )

    _ = generate_csv_typed(
        str(topology_path),
        str(_prototype_file("network_topology.schema.yaml")),
        output_base,
    )

    hosts_csv: Path = tmp_path / "topo-hosts.csv"
    rows: list[list[str]] = list(csv.reader(io.StringIO(hosts_csv.read_text(encoding="utf-8"))))
    data_rows: list[list[str]] = [row for row in rows[1:] if len(row) >= 2]

    fallback_scalar_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "host_scalar.scalars.unknown_scalar_key"),
        None,
    )
    assert fallback_scalar_row is not None
    assert fallback_scalar_row[1] == "ホスト固有のスカラー変数"

    fallback_service_row: list[str] | None = next(
        (row for row in data_rows if row[0] == "host_service.services.unknown_service.config.unknown_config_key"),
        None,
    )
    assert fallback_service_row is not None
    assert fallback_service_row[1] == "サービス固有の設定"


def test_invalid_topology_raises_value_error(tmp_path: Path) -> None:
    """必須トップレベルキー欠落時に ValueError を送出する。"""
    topology_path: Path = tmp_path / "invalid_topo.yaml"
    schema_path: Path = tmp_path / "schema.yaml"

    topology_path.write_text(
        """
version: 2
globals: {}
""".strip()
        + "\n",
        encoding="utf-8",
    )
    schema_path.write_text("type: object\nproperties: {}\n", encoding="utf-8")

    with pytest.raises(ValueError):
        _ = generate_csv_typed(
            str(topology_path),
            str(schema_path),
            None,
        )
