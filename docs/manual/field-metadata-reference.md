# フィールドメタデータリファレンスマニュアル (field_metadata.yaml)

`field_metadata.yaml` はスカラー変数の名称,型,説明,値の制約を定義するファイルです。`generate_hostvars_matrix.py` が参照し, Comma-Separated Values (以下 CSV と略す) 形式のホスト変数比較シートの列ヘッダや値の検証条件を決定します。

## 目次

- [フィールドメタデータリファレンスマニュアル (field\_metadata.yaml)](#フィールドメタデータリファレンスマニュアル-field_metadatayaml)
  - [目次](#目次)
  - [ファイルの構成](#ファイルの構成)
  - [field\_entry (フィールド定義)](#field_entry-フィールド定義)
    - [キー一覧](#キー一覧)
    - [type の許容値](#type-の許容値)
    - [category の許容値](#category-の許容値)
  - [allowed\_range の種別](#allowed_range-の種別)
    - [numeric (数値範囲)](#numeric-数値範囲)
    - [enum (列挙)](#enum-列挙)
    - [pattern (正規表現)](#pattern-正規表現)
    - [semantic (意味的制約)](#semantic-意味的制約)
  - [allowed\_values の使い方](#allowed_values-の使い方)
  - [登録済みフィールドの一覧 (主要抜粋)](#登録済みフィールドの一覧-主要抜粋)
    - [network\_interface カテゴリ](#network_interface-カテゴリ)
    - [routing\_bgp カテゴリ](#routing_bgp-カテゴリ)
    - [infrastructure カテゴリ (主要)](#infrastructure-カテゴリ-主要)
    - [k8s\_features カテゴリ (主要)](#k8s_features-カテゴリ-主要)
    - [k8s\_network カテゴリ](#k8s_network-カテゴリ)
    - [k8s\_control\_plane カテゴリ](#k8s_control_plane-カテゴリ)
  - [ノード設定パラメタデザインシート 出力での利用](#ノード設定パラメタデザインシート-出力での利用)
  - [関連資料](#関連資料)


## ファイルの構成

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `version` | 必須 | integer | スキーマバージョン。現在は `1` を指定する |
| `description` | 任意 | string | このファイル全体の説明文 |
| `fields` | 必須 | object | スカラー変数名をキーとするフィールド定義辞書 |

```yaml
version: 1
description: ホスト変数スカラー設定のメタデータ定義ファイル。
fields:
  # フィールド定義をここに記述する
```

---

## field_entry (フィールド定義)

`fields` の各エントリは以下のキーで構成します。

### キー一覧

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `type` | 必須 | string | 変数の型 |
| `description` | 必須 | string | ノード設定パラメタデザインシート / パラメタデザインシート ヘッダに表示する説明文 |
| `category` | 必須 | string | ノード設定パラメタデザインシート での分類グループ |
| `allowed_range` | 任意 | object | 値の制約 (後述 4 種類から 1 つ選択) |
| `allowed_values` | 任意 | array of string | 許容する値の列挙リスト |
| `examples` | 任意 | array | 値の例 |
| `notes` | 任意 | string | 補足説明 |

`allowed_range` と `allowed_values` は同時に使用できません。どちらか一方だけ指定します。

### type の許容値

| 値 | 意味 | 使用例 |
|---|---|---|
| `string` | 文字列 | バージョン番号, パス, 汎用文字列 |
| `integer` | 整数 | AS 番号, ポート番号, 数値設定 |
| `number` | 数値 (小数含む) | 実数値を取る設定 |
| `boolean` | 真偽値 | 有効化フラグ |
| `cidr` | CIDR 表記アドレス | ネットワークアドレス |
| `ip` | IP アドレス | ゲートウェイ, サーバアドレス |
| `hostname` | ホスト名または FQDN | サービスホスト名 |
| `interface` | Network Interface Card (以下 NIC と略す) 名 | `eth0`, `ens3` などのデバイス名 |

### category の許容値

| 値 | 意味 |
|---|---|
| `network_interface` | ネットワークインターフェース関連 |
| `routing_bgp` | Border Gateway Protocol (以下 BGP と略す) ルーティング関連 |
| `k8s_network` | Kubernetes ネットワーク関連 |
| `k8s_control_plane` | Kubernetes コントロールプレーン関連 |
| `k8s_features` | Kubernetes 追加機能関連 |
| `storage` | ストレージ関連 |
| `infrastructure` | インフラ全般 |

---

## allowed_range の種別

### numeric (数値範囲)

数値の最小値と最大値を指定します。

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `kind` | 必須 | `"numeric"` | 種別識別子 |
| `min` | 必須 | number | 最小値 (以上) |
| `max` | 必須 | number | 最大値 (以下) |

```yaml
frr_bgp_asn:
  type: integer
  description: Free Range Routing (以下 FRR と略す) BGP 自律システム番号
  category: routing_bgp
  allowed_range:
    kind: numeric
    min: 1
    max: 4294967295
```

### enum (列挙)

許容する文字列値を列挙します。

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `kind` | 必須 | `"enum"` | 種別識別子 |
| `values` | 必須 | array of string | 許容する値のリスト |

```yaml
ip_version:
  type: string
  description: IP バージョン設定
  category: network_interface
  allowed_range:
    kind: enum
    values:
      - ipv4_only
      - ipv6_only
      - dual_stack
```

### pattern (正規表現)

Python の正規表現パターンで許容する書式を定義します。

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `kind` | 必須 | `"pattern"` | 種別識別子 |
| `regex` | 必須 | string | Python 正規表現パターン文字列 |

```yaml
my_version_string:
  type: string
  description: バージョン文字列 (メジャー.マイナー.パッチ 形式)
  category: infrastructure
  allowed_range:
    kind: pattern
    regex: '^\d+\.\d+\.\d+$'
```

### semantic (意味的制約)

Ansible やネットワーク設定で意味を持つ値の形式を指定します。

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `kind` | 必須 | `"semantic"` | 種別識別子 |
| `name` | 必須 | string | 意味的制約の種別名 |

`name` の許容値:

| 値 | 意味 | 使用例 |
|---|---|---|
| `fqdn` | 完全修飾ドメイン名 | サービスホスト名 |
| `ifname` | NIC 名 | `eth0`, `ens3f0` |
| `ip_or_fqdn` | IP アドレスまたは FQDN | ルーター ID, サーバアドレス |
| `asn` | 自律システム番号 | BGP AS 番号 |
| `cidr_ipv4` | IPv4 CIDR 表記 | Pod ネットワーク, サービスサブネット |
| `cidr_ipv6` | IPv6 CIDR 表記 | IPv6 アドレス範囲 |

```yaml
gitlab_hostname:
  type: hostname
  description: GitLab ホスト名
  category: infrastructure
  allowed_range:
    kind: semantic
    name: fqdn

gpm_mgmt_nic:
  type: interface
  description: GPM 管理用 NIC
  category: network_interface
  allowed_range:
    kind: semantic
    name: ifname

frr_bgp_router_id:
  type: string
  description: FRR BGP ルーター ID
  category: routing_bgp
  allowed_range:
    kind: semantic
    name: ip_or_fqdn
```

---

## allowed_values の使い方

真偽値フラグなど, 取りうる値が事前に確定している場合は `allowed_values` で列挙します。

```yaml
k8s_multus_enabled:
  type: boolean
  description: Multus を有効化するフラグ
  category: k8s_features
  allowed_values:
    - "true"
    - "false"
```

> `allowed_values` の各要素は文字列として記述します。Python 型への変換は `type_schema.yaml` が担います。

---

## 登録済みフィールドの一覧 (主要抜粋)

### network_interface カテゴリ

| フィールド名 | 型 | 説明 | 制約種別 |
|---|---|---|---|
| `external_net_nic` | `interface` | Kubernetesなどのサービスを外部公開するためのネットワーク用 NIC | semantic (ifname) |
| `gpm_mgmt_nic` | `interface` | 内部管理ネットワーク用 NIC | semantic (ifname) |
| `mgmt_nic` | `interface` (type_schema より) | 外部管理ネットワーク用 NIC | なし |
| `k8s_nic` | `interface` (type_schema より) | Kubernetes 用 NIC | なし |

### routing_bgp カテゴリ

| フィールド名 | 型 | 説明 | 制約種別 |
|---|---|---|---|
| `frr_bgp_asn` | `integer` | FRR BGP AS 番号 | numeric (1..4294967295) |
| `frr_bgp_router_id` | `string` | FRR BGP ルーター ID | semantic (ip_or_fqdn) |

### infrastructure カテゴリ (主要)

| フィールド名 | 型 | 説明 | 制約種別 |
|---|---|---|---|
| `gitlab_hostname` | `hostname` | GitLab ホスト名 | semantic (fqdn) |
| `build_docker_ce_backup_container_image` | `boolean` | Docker CE バックアップコンテナイメージ構築フラグ | allowed_values |
| `terraform_enabled` | `boolean` | Terraform 有効化フラグ | なし |

### k8s_features カテゴリ (主要)

| フィールド名 | 型 | 説明 | 制約種別 |
|---|---|---|---|
| `k8s_multus_enabled` | `boolean` | Multus 有効化フラグ | allowed_values |
| `k8s_multus_version` | `string` | Multus バージョン | なし |
| `k8s_whereabouts_enabled` | `boolean` | Whereabouts 有効化フラグ | allowed_values |
| `k8s_whereabouts_version` | `string` | Whereabouts バージョン | なし |
| `k8s_hubble_cli_enabled` | `boolean` | Hubble Command Line Interface (以下 CLI と略す) 有効化フラグ | allowed_values |
| `k8s_hubble_ui_enabled` | `boolean` | Hubble UI 有効化フラグ | allowed_values |
| `hubble_ui_enabled` | `boolean` | Hubble UI 有効化フラグ (旧称) | allowed_values |
| `k8s_cilium_version` | `string` | Cilium バージョン | なし |
| `k8s_helm_enabled` | `boolean` | Helm 有効化フラグ | なし |

### k8s_network カテゴリ

| フィールド名 | 型 | 説明 | 制約種別 |
|---|---|---|---|
| `k8s_whereabouts_ipv4_range_start` | `string` | Whereabouts IPv4 レンジ開始アドレス | なし |
| `k8s_whereabouts_ipv4_range_end` | `string` | Whereabouts IPv4 レンジ終了アドレス | なし |
| `k8s_whereabouts_ipv6_range_start` | `string` | Whereabouts IPv6 レンジ開始アドレス | なし |
| `k8s_whereabouts_ipv6_range_end` | `string` | Whereabouts IPv6 レンジ終了アドレス | なし |

### k8s_control_plane カテゴリ

| フィールド名 | 型 | 説明 | 制約種別 |
|---|---|---|---|
| `k8s_major_minor` | `string` | Kubernetes メジャー.マイナーバージョン | なし |
| `enable_create_k8s_ca` | `boolean` | Kubernetes 共通 CA の作成/再利用フラグ | allowed_values |
| `k8s_shared_ca_source_host` | `string` | Kubernetes 共通 CA のソースホスト | なし |
| `k8s_shared_ca_output_dir` | `string` | Kubernetes 共通 CA の出力ディレクトリ | なし |
| `k8s_shared_ca_replace_kube_ca` | `boolean` | Kubernetes 標準 CA を共通 CA で置き換えるフラグ | allowed_values |

---

## ノード設定パラメタデザインシート 出力での利用

`generate_hostvars_matrix.py` は `field_metadata.yaml` を読み込み, 次のようにして ノード設定パラメタデザインシート を生成します。

1. `fields` の各エントリをノード設定パラメタデザインシート の行として出力する。
2. `description` が ノード設定パラメタデザインシート の行ヘッダに表示される。
3. `category` が ノード設定パラメタデザインシート の行グループに相当し, 同じカテゴリのフィールドがまとまって並ぶ。
4. `allowed_range` または `allowed_values` は `validate_hostvars_matrix.py` による検証条件として使用される。

---

## 関連資料

- [ロール作成者向けガイド](ansible-role-author-guide.md): フィールドを追加する手順
- [スキーマファイル参照](schema-files-reference.md): `field_metadata.schema.yaml` の構造詳細
- [変換ルール設定参照](convert-rule-config-reference.md): サービス設定からスカラーへの変換ルール
