# ansibleConfigGenerator マニュアル

## このマニュアル群の読み方

ansibleConfigGenerator は, ネットワークトポロジー定義ファイル (`network_topology.yaml`) から
[ansible-linux-setup](https://github.com/takeharukato/ansible-linux-setup) 用の Ansible ホスト変数ファイルや Terraform 設定ファイルを生成するツールキットです。

このマニュアル群は対象読者ごとに分離されています。下の「対象読者と読み進め方」から自分の目的に合った導線を選んでください。

## 対象読者

| 読者 | 目的 |
|---|---|
| ansible-linux-setup 利用者 | `network_topology.yaml` を作成し, `host_vars` ファイルや `terraform.tfvars` を生成する |
| Ansible ロール作成者 | ansible-linux-setup 向けロールを開発し, 本ツールに変数定義や変換ルールを追加する |
| 定義ファイル参照利用者 | `field_metadata.yaml`, `convert-rule-config.yaml`, スキーマファイルの仕様を確認する |

## 利用者向けの読み進め方

本ツールを使って設定ファイルを生成する場合は, 次の順で読み進めてください。

1. [ツールチェイン概要](toolchain-overview.md): ツール全体像と各 CLI の役割を把握する
2. [利用者向け操作ガイド](user-guide-linux-ansible-setup.md): `network_topology.yaml` から最終成果物までの手順

## Ansible ロール作成者向けの読み進め方

ansible-linux-setup のロールを新規開発したり, 既存ロールに変数を追加する場合は, 次の順で読み進めてください。

1. [ツールチェイン概要](toolchain-overview.md): ツール全体の構成を把握する
2. [ロール作成者向けガイド](ansible-role-author-guide.md): 変数追加, サービス定義, ノードロール追加の作業手順
3. [スキーマファイル参照](schema-files-reference.md): フォーマット定義の詳細確認
4. [変換ルール設定参照](convert-rule-config-reference.md): `convert-rule-config.yaml` の仕様確認
5. [フィールドメタデータ参照](field-metadata-reference.md): `field_metadata.yaml` の仕様確認

## 定義ファイルの仕様確認が必要な場合

特定の設定ファイルの仕様だけを確認したい場合は, 該当の参照ドキュメントを直接参照してください。

| ファイル | 説明 |
|---|---|
| [スキーマファイル参照](schema-files-reference.md) | `network_topology.schema.yaml`, `host_vars_structured.schema.yaml`, `field_metadata.schema.yaml`, `type_schema.yaml` の仕様 |
| [変換ルール設定参照](convert-rule-config-reference.md) | `convert-rule-config.yaml` の `service_settings`, `service_transform`, `network_role` セクションの仕様 |
| [フィールドメタデータ参照](field-metadata-reference.md) | `field_metadata.yaml` の各エントリのキーと制約の仕様 |

## 問題が発生した場合

[トラブルシューティング](troubleshooting.md): よくある失敗パターンと対処方法

## マニュアル一覧

| ファイル | 内容 | 対象読者 |
|---|---|---|
| [toolchain-overview.md](toolchain-overview.md) | ツール全体像, 各 CLI の役割, スキーマ探索順 | 全員 |
| [user-guide-linux-ansible-setup.md](user-guide-linux-ansible-setup.md) | host_vars/terraform.tfvars 生成の操作手順 | ansible-linux-setup 利用者 |
| [ansible-role-author-guide.md](ansible-role-author-guide.md) | 変数/サービス/ロール追加の作業手順 | Ansible ロール作成者 |
| [schema-files-reference.md](schema-files-reference.md) | 各スキーマファイルの仕様 | ロール作成者, 定義参照 |
| [convert-rule-config-reference.md](convert-rule-config-reference.md) | 変換ルール設定ファイルの仕様 | ロール作成者, 定義参照 |
| [field-metadata-reference.md](field-metadata-reference.md) | フィールドメタデータファイルの仕様 | ロール作成者, 定義参照 |
| [troubleshooting.md](troubleshooting.md) | よくある問題と対処方法 | 全員 |
