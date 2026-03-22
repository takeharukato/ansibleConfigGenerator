# ansibleConfigGenerator

## 概要

ansibleConfigGenerator は、計算ノードの機能やネットワークトポロジの定義から、[ansible-linux-setup](https://github.com/takeharukato/ansible-linux-setup) 用の Ansible ホスト変数ファイルおよび関連アーティファクトを生成するツールキットです。

本プロジェクトは次の 5 つのコマンドラインツールを提供します。

- generate_host_vars_structured.py
- generate_host_vars_files.py
- generate_hostvars_matrix.py
- generate_network_topology_design_sheet.py
- generate_terraform_tfvars.py

スキーマ/設定ファイルの探索順は, 次の 5 段階で固定です。

1. CLI オプション: --schema-dir
2. ユーザー設定: ~/.genAnsibleConf.yaml
3. システム設定: /etc/genAnsibleConf/config.yaml
4. datadir: ${datadir}/genAnsibleConf/schema
5. スクリプト配置ディレクトリ

## 前提パッケージ

- Python 3.9 以降
- PyYAML
- jsonschema
- gettext 0.21 以降
- autoconf 2.69 以降
- automake 1.16 以降
- docker (make rpm, make deb 実行時のみ)

## ディレクトリ構成

```text
.
├── autogen.sh
├── configure.ac
├── Makefile.am
├── requirements.txt
├── src/
│   └── genAnsibleConf/
│       ├── generate_host_vars_structured.py
│       ├── generate_host_vars_files.py
│       ├── generate_hostvars_matrix.py
│       ├── generate_network_topology_design_sheet.py
│       ├── generate_terraform_tfvars.py
│       ├── field_metadata.yaml
│       ├── network_topology.schema.yaml
│       ├── type_schema.yaml
│       ├── convert-rule-config.yaml
│       └── lib/
├── config/
│   ├── genAnsibleConf.system-config.yaml
│   └── genAnsibleConf.user-config.yaml
├── tests/
├── debian/
├── rpm/
└── Dockerfiles/
```

## インストール

```shell
./autogen.sh
./configure
make
make install
```

任意のプレフィクスへ導入する場合は次を使用してください。

```shell
./configure --prefix=/tmp/test
make
make install
```

## make ターゲット

- make: プロジェクト成果物のビルド
- make install: 実行スクリプト, Python モジュール, schema を導入
- make check: テストスイート実行
- make clean: 生成物削除
- make dist: 配布 tarball 生成
- make cloc: 行数集計 (cloc が必要)
- make coverage: カバレッジ測定
- make docs: Sphinx ドキュメント生成
- make rpm: Docker 経由で RPM パッケージ生成
- make deb: Docker 経由で Debian パッケージ生成

パッケージ成果物は dist/ に出力されます。

## 設定ファイル

設定ファイルは以下の順序で探索されます。

1. ユーザー設定: `~/.genAnsibleConf.yaml`
2. システム設定: `/etc/genAnsibleConf/config.yaml`

両ファイルとも省略可能です。存在する場合, `schema_search_paths` セクションからスキーマファイルの場所を読み取ります。
どちらのファイルも存在しない場合は, Overview に記載した 5 段階探索の残りのステップ (Datadir -> スクリプトディレクトリへのフォールバック) でスキーマファイルを探索します。

設定ファイル形式は以下です。

`schema_search_paths` の各キー:

| キー名 | 設定する内容 | 設定例 |
|---|---|---|
| `field_metadata` | フィールドメタデータ YAML ファイルのパス | `~/.genAnsibleConf/field_metadata.yaml` |
| `network_topology` | ネットワークトポロジー JSON Schema ファイルのパス | `~/.genAnsibleConf/network_topology.schema.yaml` |
| `type_schema` | 型スキーマ YAML ファイルのパス | `~/.genAnsibleConf/type_schema.yaml` |
| `convert_rule_config` | 変換ルール設定 YAML ファイルのパス | `~/.genAnsibleConf/convert-rule-config.yaml` |
| `default_dir` | 各キーの個別パスが未設定の場合に使用するデフォルトディレクトリ | `~/.genAnsibleConf` |

設定ファイルの例:

```yaml
schema_search_paths:
  field_metadata: ~/.genAnsibleConf/field_metadata.yaml
  network_topology: ~/.genAnsibleConf/network_topology.schema.yaml
  type_schema: ~/.genAnsibleConf/type_schema.yaml
  convert_rule_config: ~/.genAnsibleConf/convert-rule-config.yaml
  default_dir: ~/.genAnsibleConf
```

設定サンプルは以下です。

- config/genAnsibleConf.user-config.yaml
- config/genAnsibleConf.system-config.yaml

## 使用例

network_topology.yaml から host_vars_structured.yaml を生成:

```shell
generate_host_vars_structured.py -i network_topology.yaml -o host_vars_structured.yaml
```

host_vars ファイル群を生成:

```shell
generate_host_vars_files.py host_vars.gen -i host_vars_structured.yaml -m field_metadata.yaml
```

マトリクス CSV を生成:

```shell
generate_hostvars_matrix.py -H host_vars_structured.yaml -m field_metadata.yaml -o host_vars_scalars_matrix.csv
```

設計シート CSV を生成:

```shell
generate_network_topology_design_sheet.py -i network_topology.yaml -o .
```

terraform.tfvars を生成:

```shell
generate_terraform_tfvars.py -t network_topology.yaml -o terraform.tfvars
```

schema 探索先を明示する場合:

```shell
generate_hostvars_matrix.py --schema-dir /path/to/schema -H host_vars_structured.yaml
```

## テスト

```shell
make check
```

または

```shell
PYTHONPATH=.:tests python3 -m pytest tests/tests_py -q
```

## 著作権表記

Copyright 2025 Takeharu KATO.

本プロジェクトは BSD 2-Clause License の下で配布されています。
詳細は LICENSE ファイルを参照してください。
