# ansibleConfigGenerator

## 概要

ansibleConfigGenerator は、計算ノードの機能やネットワークトポロジの定義から、[ansible-linux-setup](https://github.com/takeharukato/ansible-linux-setup) 用の Ansible ホスト変数ファイルおよび関連アーティファクトを生成するツールキットです。

本プロジェクトは次の 6 つのコマンドラインツールを提供します。

- generate_host_vars_structured.py
- generate_host_vars_files.py
- generate_hostvars_matrix.py
- validate_hostvars_matrix.py
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
├── Readme.md
├── ReadmeEN.md
├── requirements.txt
├── src/
│   └── genAnsibleConf/
│       ├── generate_host_vars_structured.py
│       ├── generate_host_vars_files.py
│       ├── generate_hostvars_matrix.py
│       ├── generate_network_topology_design_sheet.py
│       ├── generate_terraform_tfvars.py
│       ├── validate_hostvars_matrix.py
│       ├── field_metadata.yaml
│       ├── field_metadata.schema.yaml
│       ├── network_topology.schema.yaml
│       ├── host_vars_structured.schema.yaml
│       ├── type_schema.yaml
│       ├── convert-rule-config.yaml
│       └── lib/
├── config/
│   ├── sample-network_topology.yaml
│   ├── genAnsibleConf.system-config.yaml
│   └── genAnsibleConf.user-config.yaml
├── docs/
│   ├── SPECIFICATION.md
│   ├── commands-specJP.md
│   ├── manual/
│   ├── sphinx/
│   └── debug/
├── tests/
├── debian/
├── rpm/
└── Dockerfiles/
```

各ディレクトリ内の内容物の概要は以下の通りです:

| ディレクトリ | 主な用途 | 主な内容 |
|---|---|---|
| `src/genAnsibleConf/` | 本体スクリプトとスキーマ定義 | ホスト変数生成スクリプト, YAML/JSON Schema, 共通ライブラリ |
| `config/` | 設定サンプルと設定ファイル | ユーザー設定, システム設定, サンプルネットワークトポロジ |
| `docs/` | 日本語仕様書と利用者向け文書 | 仕様書, コマンド仕様, 手引き, Sphinx ソース |
| `tests/` | 自動テスト | pytest ベースのテスト群, テスト補助ファイル |
| `debian/` | Debian パッケージ定義 | control, rules, copyright など |
| `rpm/` | RPM パッケージ定義 | spec ファイル |
| `Dockerfiles/` | パッケージ生成用コンテナ定義 | RPM/Deb ビルド用 Dockerfile, 補助スクリプト |

### src/genAnsibleConf/ の主なファイル

| ファイル/ディレクトリ | 補足説明 |
|---|---|
| `generate_host_vars_structured.py` | ネットワークトポロジ定義から構造化 host_vars を生成します。 |
| `generate_host_vars_files.py` | 構造化 host_vars からノードごとの host_vars ファイル群を生成します。 |
| `generate_hostvars_matrix.py` | ノード設定を一覧化した CSV マトリクスを生成します。 |
| `generate_network_topology_design_sheet.py` | ネットワーク設計シート向け CSV を生成します。 |
| `generate_terraform_tfvars.py` | トポロジ定義から terraform.tfvars を生成します。 |
| `validate_hostvars_matrix.py` | 生成されたマトリクスや構造データの検証を行います。 |
| `field_metadata.yaml` | host_vars の各フィールド定義と説明を保持します。 |
| `field_metadata.schema.yaml` | field_metadata.yaml のスキーマを定義します。 |
| `network_topology.schema.yaml` | ネットワークトポロジ定義ファイルのスキーマを定義します。 |
| `host_vars_structured.schema.yaml` | 構造化 host_vars 出力のスキーマを定義します。 |
| `type_schema.yaml` | 型定義に関する共通スキーマを保持します。 |
| `convert-rule-config.yaml` | フィールド変換やサービス変換のルールを定義します。 |
| `lib/` | 各生成処理で共有する Python ライブラリ群です。 |

### config/ のファイル

| ファイル | 補足説明 |
|---|---|
| `sample-network_topology.yaml` | ネットワークトポロジ定義の包括的なサンプルです。 |
| `genAnsibleConf.system-config.yaml` | システム全体で使用する設定ファイルの例です。 |
| `genAnsibleConf.user-config.yaml` | ユーザー単位で使用する設定ファイルの例です。 |

### docs/ の主な内容

| ファイル/ディレクトリ | 補足説明 |
|---|---|
| `SPECIFICATION.md` | データ形式と振る舞いの全体仕様です。 |
| `commands-specJP.md` | 各コマンドの入出力仕様を日本語で説明します。 |
| `manual/` | 利用者向け手引き, リファレンス, トラブルシューティングを格納します。 |
| `sphinx/` | Sphinx で HTML 文書を生成するためのソース一式です。 |
| `debug/` | デバッグや開発補助向けの文書や設定を格納します。 |

### Dockerfiles/ のファイル

| ファイル | 補足説明 |
|---|---|
| `deb.ubuntu24.04.Dockerfile` | Debian パッケージ生成用の Ubuntu 24.04 ベースコンテナ定義です。 |
| `rpm.almalinux9.Dockerfile` | RPM パッケージ生成用の AlmaLinux 9 ベースコンテナ定義です。 |
| `entrypoint-deb.sh` | Debian パッケージ生成コンテナの起動処理です。 |
| `entrypoint-rpm.sh` | RPM パッケージ生成コンテナの起動処理です。 |

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

ノード設定 マトリクス CSV を生成:

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

使用法の詳細は, [ansibleConfigGenerator マニュアル](docs/manual/index.md)を参照してください。

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
