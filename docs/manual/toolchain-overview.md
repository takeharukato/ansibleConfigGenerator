# ツールチェイン概要

## 本ツール群の目的

ansibleConfigGenerator は, ネットワークトポロジー定義ファイル (`network_topology.yaml`) を入口として, [ansible-linux-setup](https://github.com/takeharukato/ansible-linux-setup) で使用する Ansible ホスト変数ファイル群と, インフラ構築に必要な Terraform 設定ファイルを自動生成するツールキットです。

手作業でホスト変数を管理する代わりに, トポロジー定義を一元管理し, そこから各出力ファイルを再生成する運用を実現します。

## ツールチェイン全体像

本ツール群には 3 本の処理経路があります。

```
network_topology.yaml
      |
      +-- [Ansible パス] --------------------------------+
      |    generate_host_vars_structured.py              |
      |          -> host_vars_structured.yaml             |
      |               |                                  |
      |               +-- generate_hostvars_matrix.py    |
      |               |        -> host_vars_scalars_matrix.csv (レビュー用)
      |               |                                  |
      |               +-- validate_hostvars_matrix.py    |
      |               |        -> 整合性確認              |
      |               |                                  |
      |               +-- generate_host_vars_files.py    |
      |                        -> host_vars/*.local (最終成果物)
      |
      +-- [Terraform パス] --独立実行-----------------------
      |    generate_terraform_tfvars.py
      |        -> terraform.tfvars
      |
      +-- [設計シートパス] --独立実行-----------------------
           generate_network_topology_design_sheet.py
               -> network_topology-{globals,roles,services,hosts}.csv
```

Ansible パスは 4 ステップが順序依存です。Terraform パスと設計シートパスは任意のタイミングで独立実行できます。

## 各 CLI ツールの役割

| ツール名 | 役割 | 独立実行 |
|---|---|---|
| `generate_host_vars_structured.py` | `network_topology.yaml` を検証し, 構造化 host_vars を生成する (Ansible パスの起点) | 不可 (入力が必要) |
| `generate_hostvars_matrix.py` | 構造化 host_vars から設定値一覧 CSV を生成する (レビュー用) | 不可 (前ステップ必要) |
| `validate_hostvars_matrix.py` | CSV の整合性を検証する | CSV があれば可 |
| `generate_host_vars_files.py` | 構造化 host_vars をホスト別の YAML ファイルに展開する | 不可 (前ステップ必要) |
| `generate_terraform_tfvars.py` | `network_topology.yaml` から `terraform.tfvars` を生成する | 可 |
| `generate_network_topology_design_sheet.py` | `network_topology.yaml` から 4 種類の設計シート CSV を生成する | 可 |

## 各 CLI の入力と出力

### generate_host_vars_structured.py

| 項目 | 内容 |
|---|---|
| 主入力 | `network_topology.yaml`, `convert-rule-config.yaml` |
| 主出力 | `host_vars_structured.yaml` |
| スキーマ検証 | `network_topology.schema.yaml` |
| 主なオプション | `-i/--input`, `-o/--output`, `--schema-dir` |

```shell
generate_host_vars_structured.py -i network_topology.yaml -o host_vars_structured.yaml
```

### generate_hostvars_matrix.py

| 項目 | 内容 |
|---|---|
| 主入力 | `host_vars_structured.yaml`, `field_metadata.yaml` |
| 主出力 | `host_vars_scalars_matrix.csv` |
| 主なオプション | `-H/--host-vars`, `-m/--metadata`, `-o/--output`, `--schema-dir` |

```shell
generate_hostvars_matrix.py -H host_vars_structured.yaml -m field_metadata.yaml \
  -o host_vars_scalars_matrix.csv
```

### validate_hostvars_matrix.py

| 項目 | 内容 |
|---|---|
| 主入力 | `host_vars_scalars_matrix.csv`, `field_metadata.yaml`, `host_vars_structured.yaml` |
| 主出力 | 検証結果 (終了コード 0 = 成功) |
| 主なオプション | 位置引数で `csv_file`, `metadata_file`, `host_vars_file` を受け取る |

### generate_host_vars_files.py

| 項目 | 内容 |
|---|---|
| 主入力 | `host_vars_structured.yaml`, `field_metadata.yaml` |
| 主出力 | `{output_dir}/{hostname}.local`, `{output_dir}/main.yml` |
| 主なオプション | `output_dir` (位置引数), `-i/--input-structured`, `-m/--metadata`, `-w/--overwrite`, `-v/--validate-roundtrip` |

### generate_terraform_tfvars.py

| 項目 | 内容 |
|---|---|
| 主入力 | `network_topology.yaml` |
| 主出力 | `terraform.tfvars` (HCL 形式) |
| 前提 | topology に `terraform_orchestration` ロールが定義されていること |
| 主なオプション | `-t/--topology`, `-o/--output`, `-n/--dry-run`, `-s/--strict` |

### generate_network_topology_design_sheet.py

| 項目 | 内容 |
|---|---|
| 主入力 | `network_topology.yaml`, `field_metadata.yaml` |
| 主出力 | `network_topology-globals.csv`, `network_topology-roles.csv`, `network_topology-services.csv`, `network_topology-hosts.csv` |
| 主なオプション | `-i/--input`, `-o/--output`, `--schema-dir` |

## 標準処理フロー

Ansible パスの標準的な実行順序は次のとおりです。

| ステップ | コマンド | 入力 | 出力 |
|---|---|---|---|
| 1 | `generate_host_vars_structured.py` | `network_topology.yaml` | `host_vars_structured.yaml` |
| 2 | `generate_hostvars_matrix.py` | `host_vars_structured.yaml` | `host_vars_scalars_matrix.csv` |
| 3 | `validate_hostvars_matrix.py` | CSV + `field_metadata.yaml` | 検証結果 |
| 4 | `generate_host_vars_files.py` | `host_vars_structured.yaml` | `host_vars/*.local` |

ステップ 1 の出力がステップ 2 以降の入力となるため, この順序を守ってください。

## Terraform 出力の位置付け

`generate_terraform_tfvars.py` は XCP-ng 環境向けの Terraform 変数ファイルを生成します。Ansible パスとは独立しており, `network_topology.yaml` を入力とします。

topology 内に `terraform_orchestration` ロールを持つノードが定義されている場合に, そのノードの環境設定から `terraform.tfvars` を生成します。

## 設計シート出力の位置付け

`generate_network_topology_design_sheet.py` は topology の構造を 4 種類の CSV ファイルに展開します。設計レビューや仕様書作成の補助を目的としており, Ansible パスとは独立して使用します。

| 出力ファイル | 内容 |
|---|---|
| `network_topology-globals.csv` | グローバル設定 (ネットワーク, スカラー既定値) |
| `network_topology-roles.csv` | ロールとそれに対応するサービスの一覧 |
| `network_topology-services.csv` | サービス定義と設定値の一覧 |
| `network_topology-hosts.csv` | ホスト別の設定一覧 |

## 入力ファイルと出力ファイル

### 入力ファイル

| ファイル名 | 役割 | 形式 |
|---|---|---|
| `network_topology.yaml` | ネットワーク, ロール, ノードの定義 (主入力) | YAML |
| `field_metadata.yaml` | スカラーフィールドの名称, 型, 制約 | YAML |
| `convert-rule-config.yaml` | サービス設定からスカラーへの変換ルール, ネットワークロールポリシー | YAML |
| `network_topology.schema.yaml` | `network_topology.yaml` の JSON Schema 定義 | YAML |
| `type_schema.yaml` | 出力変数の Python 型マッピング | YAML |

### 出力ファイル

| ファイル名 | 役割 | 形式 |
|---|---|---|
| `host_vars_structured.yaml` | 全ホスト分の構造化 host_vars (中間生成物) | YAML |
| `host_vars_scalars_matrix.csv` | スカラー設定値の一覧表 (レビュー用) | CSV |
| `{output_dir}/{hostname}.local` | ホスト別 Ansible ホスト変数ファイル (最終成果物) | YAML |
| `terraform.tfvars` | XCP-ng 向け Terraform 変数ファイル (最終成果物) | HCL |
| `network_topology-*.csv` | 設計シート (補助資料) | CSV |

## スキーマと設定ファイルの探索順

各 CLI ツールは, 起動時にスキーマファイルと設定ファイルを次の優先順で探索します。最初に見つかったファイルを使用します。

| 優先順位 | 探索先 | 概要 |
|---|---|---|
| 1 | `--schema-dir` オプション | CLI 実行時に `-s/--schema-dir` で指定したディレクトリ |
| 2 | ユーザー設定 | `~/.genAnsibleConf.yaml` の `schema_search_paths` セクション |
| 3 | システム設定 | `/etc/genAnsibleConf/config.yaml` の `schema_search_paths` セクション |
| 4 | datadir | 環境変数 `$GENANSIBLECONF_SCHEMADIR` または `make install` 時に設定された配置先 |
| 5 | スクリプト配置ディレクトリ | 実行スクリプトと同じディレクトリ (ソースツリーからの直接実行時) |

スキーマ探索先を明示的に指定する場合:

```shell
generate_hostvars_matrix.py --schema-dir /path/to/schema \
  -H host_vars_structured.yaml -m field_metadata.yaml
```

設定ファイル (`~/.genAnsibleConf.yaml`) の `schema_search_paths` に特定のファイルパスを指定することで, ファイルごとに個別のパスを設定できます。詳細は [利用者向け操作ガイド](user-guide-linux-ansible-setup.md) の「スキーマ探索先を変更する場合」を参照してください。

## 関連ファイル一覧

| ファイル | リポジトリでの配置 |
|---|---|
| `network_topology.yaml` (サンプル) | `src/genAnsibleConf/network_topology.yaml` |
| `field_metadata.yaml` | `src/genAnsibleConf/field_metadata.yaml` |
| `convert-rule-config.yaml` | `src/genAnsibleConf/convert-rule-config.yaml` |
| `network_topology.schema.yaml` | `src/genAnsibleConf/network_topology.schema.yaml` |
| `host_vars_structured.schema.yaml` | `src/genAnsibleConf/host_vars_structured.schema.yaml` |
| `field_metadata.schema.yaml` | `src/genAnsibleConf/field_metadata.schema.yaml` |
| `type_schema.yaml` | `src/genAnsibleConf/type_schema.yaml` |
| ユーザー設定サンプル | `config/genAnsibleConf.user-config.yaml` |
| システム設定サンプル | `config/genAnsibleConf.system-config.yaml` |

## 関連文書

- [利用者向け操作ガイド](user-guide-linux-ansible-setup.md)
- [ロール作成者向けガイド](ansible-role-author-guide.md)
- [スキーマファイル参照](schema-files-reference.md)
- [変換ルール設定参照](convert-rule-config-reference.md)
- [フィールドメタデータ参照](field-metadata-reference.md)
- [docs/commands-specJP.md](../commands-specJP.md) (各コマンドの詳細仕様書)
