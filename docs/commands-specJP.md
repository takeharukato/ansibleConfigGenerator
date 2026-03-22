# Ansible Config Generator コマンド仕様

- [Ansible Config Generator コマンド仕様](#ansible-config-generator-コマンド仕様)
  - [変更履歴](#変更履歴)
  - [表記規則/用語定義](#表記規則用語定義)
    - [表記規則](#表記規則)
    - [用語定義](#用語定義)
  - [概要](#概要)
  - [ツールチェインの構成と想定ワークフロー](#ツールチェインの構成と想定ワークフロー)
    - [ツールチェインの構成](#ツールチェインの構成)
    - [想定ワークフロー](#想定ワークフロー)
    - [共通仕様](#共通仕様)
  - [generate\_host\_vars\_structured](#generate_host_vars_structured)
    - [概要](#概要-1)
    - [SYNOPSIS](#synopsis)
    - [引数](#引数)
    - [オプション](#オプション)
    - [入力ファイル形式: network\_topology.yaml](#入力ファイル形式-network_topologyyaml)
      - [トップレベル構造 (表1)](#トップレベル構造-表1)
      - [globals 構造 (表2)](#globals-構造-表2)
      - [network 要素の構造 (表3)](#network-要素の構造-表3)
      - [ネットワークロール (role) の説明](#ネットワークロール-role-の説明)
        - [external\_control\_plane\_network](#external_control_plane_network)
        - [private\_control\_plane\_network](#private_control_plane_network)
        - [data\_plane\_network](#data_plane_network)
        - [bgp\_transport\_network](#bgp_transport_network)
      - [name\_servers\_ipv4 要素 (表4)](#name_servers_ipv4-要素-表4)
      - [name\_servers\_ipv6 要素 (表5)](#name_servers_ipv6-要素-表5)
      - [datacenter 要素の構造 (表6)](#datacenter-要素の構造-表6)
      - [nodes 要素 (各ノード) の構造 (表8)](#nodes-要素-各ノード-の構造-表8)
      - [interface 要素の構造 (表9)](#interface-要素の構造-表9)
      - [scalars 要素の構造 (表10)](#scalars-要素の構造-表10)
    - [入力ファイルスキーマ: network\_topology.schema.yaml](#入力ファイルスキーマ-network_topologyschemayaml)
      - [スキーマメタ情報 (表S1)](#スキーマメタ情報-表s1)
      - [スキーマプロパティ定義 (表S2)](#スキーマプロパティ定義-表s2)
      - [globals プロパティ定義 (表S3)](#globals-プロパティ定義-表s3)
      - [network additionalProperties スキーマ (表S4)](#network-additionalproperties-スキーマ-表s4)
    - [出力ファイル形式: host\_vars\_structured.yaml](#出力ファイル形式-host_vars_structuredyaml)
      - [トップレベル構造 (表O1)](#トップレベル構造-表o1)
      - [host 要素の構造 (表O2)](#host-要素の構造-表o2)
      - [scalars の一般的なフィールド (表O3)](#scalars-の一般的なフィールド-表o3)
      - [netif\_list 要素の構造 (表O4)](#netif_list-要素の構造-表o4)
      - [frr\_neighbor 要素の構造 (表O5)](#frr_neighbor-要素の構造-表o5)
    - [処理フロー](#処理フロー)
    - [エラーメッセージと終了コード](#エラーメッセージと終了コード)
    - [使用例](#使用例)
    - [制限と注意事項](#制限と注意事項)
  - [generate\_hostvars\_matrix](#generate_hostvars_matrix)
    - [概要](#概要-2)
    - [SYNOPSIS](#synopsis-1)
    - [オプション](#オプション-1)
    - [入力ファイル形式](#入力ファイル形式)
      - [host\_vars\_structured.yaml](#host_vars_structuredyaml)
      - [field\_metadata.yaml 構造 (表M1)](#field_metadatayaml-構造-表m1)
      - [field 要素の構造 (表M2)](#field-要素の構造-表m2)
    - [出力ファイル形式: CSV](#出力ファイル形式-csv)
      - [CSV 構造](#csv-構造)
      - [CSV 例](#csv-例)
    - [処理フロー](#処理フロー-1)
    - [エラーメッセージと終了コード](#エラーメッセージと終了コード-1)
    - [使用例](#使用例-1)
    - [制限と注意事項](#制限と注意事項-1)
  - [generate\_host\_vars\_files](#generate_host_vars_files)
    - [概要](#概要-3)
    - [SYNOPSIS](#synopsis-2)
    - [引数とオプション](#引数とオプション)
    - [入力ファイル形式](#入力ファイル形式-1)
      - [host\_vars\_structured.yaml](#host_vars_structuredyaml-1)
      - [field\_metadata.yaml](#field_metadatayaml)
    - [出力ファイル形式](#出力ファイル形式)
      - [ファイル名規則](#ファイル名規則)
      - [出力 YAML 構造の例](#出力-yaml-構造の例)
      - [コメント挿入規則](#コメント挿入規則)
    - [処理フロー](#処理フロー-2)
    - [上書き制御](#上書き制御)
    - [ラウンドトリップ検証](#ラウンドトリップ検証)
    - [エラーメッセージと終了コード](#エラーメッセージと終了コード-2)
    - [使用例](#使用例-2)
    - [制限と注意事項](#制限と注意事項-2)
  - [validate\_hostvars\_matrix](#validate_hostvars_matrix)
    - [概要](#概要-4)
    - [SYNOPSIS](#synopsis-3)
    - [オプション](#オプション-2)
    - [検証項目](#検証項目)
    - [処理フロー](#処理フロー-3)
    - [検証結果](#検証結果)
    - [エラーメッセージの例](#エラーメッセージの例)
    - [使用例](#使用例-3)
    - [制限と注意事項](#制限と注意事項-3)
  - [generate\_terraform\_tfvars](#generate_terraform_tfvars)
    - [概要](#概要-5)
    - [SYNOPSIS](#synopsis-4)
    - [引数](#引数-1)
    - [オプション](#オプション-3)
    - [入力ファイル形式 (generate\_terraform\_tfvars 固有)](#入力ファイル形式-generate_terraform_tfvars-固有)
      - [globals.roles の Terraform 関連設定](#globalsroles-の-terraform-関連設定)
      - [globals.services.xcp\_ng\_environment.config の構造 (表T1)](#globalsservicesxcp_ng_environmentconfig-の構造-表t1)
      - [vm\_group\_defaults の構造 (表T2)](#vm_group_defaults-の構造-表t2)
    - [出力ファイル形式: terraform.tfvars](#出力ファイル形式-terraformtfvars)
      - [トップレベル変数 (表TV1)](#トップレベル変数-表tv1)
      - [vm\_groups の構造](#vm_groups-の構造)
    - [処理フロー](#処理フロー-4)
    - [エラーメッセージと終了コード](#エラーメッセージと終了コード-4)
    - [使用例](#使用例-4)
    - [制限と注意事項](#制限と注意事項-4)
  - [generate\_network\_topology\_design\_sheet](#generate_network_topology_design_sheet)
    - [概要](#概要-6)
    - [SYNOPSIS](#synopsis-5)
    - [オプション](#オプション-4)
    - [入力ファイル形式](#入力ファイル形式-2)
    - [出力ファイル形式: network\_topology.csv](#出力ファイル形式-network_topologycsv)
      - [共通列](#共通列)
      - [セクション構成](#セクション構成)
    - [処理フロー](#処理フロー-5)
    - [エラーメッセージと終了コード](#エラーメッセージと終了コード-5)
    - [使用例](#使用例-5)
    - [制限と注意事項](#制限と注意事項-5)
  - [ワークフロー例](#ワークフロー例)
    - [標準的な処理フロー](#標準的な処理フロー)
    - [コマンド例](#コマンド例)
    - [実行例](#実行例)
  - [参照](#参照)
    - [関連ファイル一覧](#関連ファイル一覧)
    - [ディレクトリ構成例](#ディレクトリ構成例)
    - [関連ドキュメント](#関連ドキュメント)
  - [付録](#付録)
    - [補足事項](#補足事項)
      - [network\_topology.yaml のネットワーク定義で必須のフィールド](#network_topologyyaml-のネットワーク定義で必須のフィールド)
      - [reserved\_nic\_pairs の使用用途](#reserved_nic_pairs-の使用用途)
      - [パラメタシートのフィールド順序変更方法](#パラメタシートのフィールド順序変更方法)
      - [ラウンドトリップ検証で不一致が検出された場合の対処方法](#ラウンドトリップ検証で不一致が検出された場合の対処方法)
    - [トラブルシューティング](#トラブルシューティング)

## 変更履歴

| 項目 | 値 |
|------|-----|
| 仕様書バージョン | 1.3 |
| 最終更新日 | 2026-03-22 |
| 対応コマンドバージョン | prototype |

| バージョン | 更新内容 |
|-----------|--------|
| 1.3 | `generate_network_topology_design_sheet.py` の出力形式を変更。ファイル名区切り文字をアンダースコアからハイフンに変更。description 解決順序を `field_metadata.yaml` 優先に変更。`hosts` ファイルをホスト別列形式に変更。 |
| 1.2 | `generate_network_topology_design_sheet.py` を追加。CSVデザインシート (`network_topology.csv`) の仕様を追記。 |
| 1.1 | `generate_terraform_tfvars.py` を追加。globals に `xcp_ng_environment` サービス定義, nodes に `services.vm_params` を追加。 |
| 1.0 | 初版 |

## 表記規則/用語定義

### 表記規則

| 記号 | 意味 |
|------|------|
| `必須` | 必ず指定が必要な項目 |
| `オプション` | 省略可能な項目 |
| `[参照: 表N]` | 詳細は別表を参照 |

### 用語定義

| 略語 | 正式名称 | 平易な説明 |
|------|---------|-----------|
| IPv4 | インターネットプロトコルバージョン4 (IPv4) | インターネット通信で使用されるアドレスの形式の1つ (例: 192.168.1.1) |
| IPv6 | インターネットプロトコルバージョン6 (IPv6) | より多くのアドレスを扱えるインターネット通信の新しい住所形式 (例: fd69::1) |
| CIDR | Classless Inter-Domain Routing (CIDR) | クラス（A/B/C）に依存せず, IPアドレスのネットワーク部とホスト部を任意の長さで分割する技術 ネットワークの範囲を指定する記法 (例: 192.168.1.0/24) |
| DNS | ドメインネームシステム ( Domain Name System ) | ドメイン名をIPアドレスに変換するシステム |
| DHCP | 動的ホスト構成プロトコル (Dynamic Host Configuration Protocol) | ネットワーク設定を自動で配布する仕組み |
| SLAAC | ステートレスアドレス自動設定 (Stateless Address Auto Configuration) | IPv6アドレスを自動設定する仕組み |
| NIC | ネットワークインターフェース (Network Interface Card) | コンピュータをネットワークに接続する装置 |
| FQDN | 完全修飾ドメイン名 (Fully Qualified Domain Name) | ホスト名を含む完全なドメイン名 (例: server1.example.com) |
| BGP | ボーダーゲートウェイプロトコル (Border Gateway Protocol) | インターネット上で経路情報を交換するプロトコル |
| eBGP | 外部ボーダーゲートウェイプロトコル (External Border Gateway Protocol) | 異なる自律システム (AS) 間でのBGP通信 |
| MAC | メディアアクセス制御 (Media Access Control) | ネットワーク機器固有の識別番号 |
| AS | 自律システム (Autonomous System) | BGPで使用される組織のネットワーク識別番号 |
| FRR | Free Range Routing | オープンソースのルーティングソフトウェア |
| YAML | YAML Ain't Markup Language (YAML) | 設定ファイルなどで使用される人間が読みやすいデータ形式 |
| CSV | カンマ区切り値 (Comma-Separated Values) | 表形式のデータをカンマで区切って保存するファイル形式 |
| JSON Schema | JSON Schema | データ構造を検証するための仕様。YAMLやJSONファイルの形式を定義する |
| UTF-8 | Unicode Transformation Format 8-bit (UTF-8) | 世界中の様々な文字を扱える文字エンコーディング (文字コード) |
| ID | Identifier | 識別子, 識別番号 |
| Pod | ポッド (Pod) | Kubernetesにおける最小のデプロイ単位。1つ以上のコンテナを含む |
| ルートリフレクタ | ルートリフレクタ (Route Reflector) | BGPにおいて経路情報を他のルーターに中継する特別な役割のルーター |
| ルートメトリック | ルートメトリック (Route Metric) | ネットワーク経路の優先度を示す数値。値が小さいほど優先される |
| コントロールプレーンノード(Control Plane Node) |コントロールプレーンノード(Control Plane Node)| Kubernetesクラスターの管理機能を担うノード |
| ワーカーノード(Worker Node) | ワーカーノード(Worker Node) | Kubernetesでアプリケーションを実行するノード |
| Cilium | Cilium | Kubernetesのネットワーキングとセキュリティを提供するオープンソースソフトウェア |
| Terraform | Terraform | インフラストラクチャをコードで定義し自動構築するオープンソースツール (IaC) |
| HCL | HashiCorp 構成言語 (HashiCorp Configuration Language) | Terraform の設定ファイルで使用するる記述形式 |
| XCP-ng | Xen Cloud Platform next generation (XCP-ng) | オープンソースのサーバ仮想化基盤ソフトウェア |
| XOA | Xen Orchestra Appliance (XOA) | XCP-ng を Web API で操作するための管理ソフトウェア |
| IaC | コードによるインフラ構築 (Infrastructure as Code) | インフラ構成をコードで記述し管理する我ったのもの |

## 概要

本書は Ansible Config Generator プロジェクトが提供する6つのコマンドの仕様を記述する。

本ツール群は, ネットワークトポロジ情報から, Ansible向けのホスト変数ファイル群と, 設定値クロスチェック用のCSV形式のパラメタシートを生成する。
また, XCP-ng (Xen Cloud Platform next generation) 仮想化環境向け Terraform (インフラストラクチャ自動構成ツール) の変数ファイルを生成する独立したツールも提供する。
さらに, `network_topology.yaml` と `field_metadata.yaml`, スキーマから, レビュー向けの4つのCSVデザインシートを生成する独立ツールも提供する。

## ツールチェインの構成と想定ワークフロー

### ツールチェインの構成

本ツール群は以下のコマンド, ツールから構成される:

1. **generate_host_vars_structured.py**: ネットワーク構成定義ファイル (network_topology.yaml) を読み込んで, 各ホストの設定情報をまとめた構造化ファイル (host_vars_structured.yaml) を生成します。
2. **generate_hostvars_matrix.py**: 構造化ファイル (host_vars_structured.yaml) とフィールド定義 (field_metadata.yaml) を読み込んで, ホストごとの設定値を一覧表形式 (CSV) で出力します。
3. **generate_host_vars_files.py**: 構造化ファイル (host_vars_structured.yaml) とフィールド定義 (field_metadata.yaml) を読み込んで, ホストごとに個別の設定ファイル (YAML) を生成します。
4. **validate_hostvars_matrix.py**: CSV形式の一覧表, フィールド定義 (field_metadata.yaml), 構造化ファイル (host_vars_structured.yaml) を読み込んで, データの整合性を検証します。
5. **generate_terraform_tfvars.py**: ネットワーク構成定義ファイル (network_topology.yaml) を読み込んで, XCP-ng (Xen Cloud Platform next generation) 仕想化環境向けの Terraform (IaC ツール) 変数ファイル (terraform.tfvars) を生成します。ツール(1)～(4) の Ansible 向けツールチェインとは独立して動作します。
6. **generate_network_topology_design_sheet.py**: ネットワーク構成定義ファイル (network_topology.yaml), フィールドメタデータ (field_metadata.yaml), スキーマ (network_topology.schema.yaml) を読み込んで, globals, roles, services, hosts の4つのCSVデザインシートを生成します。Ansible 向けツールチェインとは独立して動作します。

### 想定ワークフロー

```mermaid
flowchart TD
    A[network_topology.yaml]
    B[host_vars_structured.yaml]
    C[(CSV形式のパラメタシート)]
    D{検証結果確認}
    E[(Ansible用 最終成果物 host_vars/*.localなど)]
    F[(terraform.tfvars)]
    G[(トポロジーデザインシート (4 CSV))]

    A -->|1: 中間形式作成<br/>generate_host_vars_structured.py| B
    B -->|2: CSV形式のパラメタシート生成<br/>generate_hostvars_matrix.py| C
    C -->|3: 検証<br/>validate_hostvars_matrix.py| D
    D -.->|4: 設定値のクロスチェック後に修正反映| A
    D -->|5: 検証完了後, 最終成果物生成<br/>generate_host_vars_files.py| E
    A -->|Terraform 対象ロール terraform_orchestration を持つノードに対して生成<br/>generate_terraform_tfvars.py| F
    A -->|設計レビュー向けCSV生成<br/>generate_network_topology_design_sheet.py| G
```

1. **中間形式作成**: `network_topology.yaml` から中間形式 `host_vars_structured.yaml` を生成する (generate_host_vars_structured.py)。
2. **CSV形式のパラメタシート生成**: 中間形式からCSV形式のパラメタシートを生成する (generate_hostvars_matrix.py)。
3. **検証**: CSV形式のパラメタシートの妥当性を検証する (validate_hostvars_matrix.py)。
4. **設定値のクロスチェック後に修正反映**: 検証結果を元に設定値をクロスチェックし, 必要に応じて `network_topology.yaml` を修正する (サイクル)。
5. **検証完了後, 最終成果物生成**: 検証完了後に, 中間形式からAnsible向けの個別ホスト変数ファイル (`host_vars/*.local`) を生成する (generate_host_vars_files.py)。
6. **Terraform 変数ファイル生成** (独立実行): `network_topology.yaml` から直接 XCP-ng 向け `terraform.tfvars` を生成する (generate_terraform_tfvars.py)。ステップ (1)〜(5) の Ansible パスとは独立して実行できる。
7. **トポロジーデザインシート生成** (独立実行): `network_topology.yaml`, `field_metadata.yaml`, `network_topology.schema.yaml` から, レビュー用の4つのCSVデザインシートを生成する (generate_network_topology_design_sheet.py)。ステップ (1)〜(5) の Ansible パスとは独立して実行できる。


### 共通仕様

| 項目 | 仕様 |
|------|------|
| ファイル形式 | YAML |
| 文字エンコーディング | UTF-8 |
| 改行コード | LF (Unix形式) |
| 正常終了コード | 0 |
| エラー終了コード | 1 |
| エラー出力先 | 標準エラー出力 |


## generate_host_vars_structured

### 概要

network_topology.yaml からホスト変数の構造化ファイル (host_vars_structured.yaml) を生成する。

### SYNOPSIS

```plaintext
generate_host_vars_structured.py [-h] input output
```

### 引数

| 引数 | 必須/オプション | 型 | 説明 | 例 |
|------|----------------|----|----|-----|
| input | 必須 | ファイルパス | 入力となるネットワークトポロジーYAMLファイル | network_topology.yaml |
| output | 必須 | ファイルパス | 出力先のホスト変数構造化YAMLファイル | host_vars_structured.yaml |

### オプション

| オプション | 説明 |
|-----------|------|
| `-h`, `--help` | ヘルプメッセージを表示して終了 |

### 入力ファイル形式: network_topology.yaml

#### トップレベル構造 (表1)

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
|------------|----------------|----|----|------|
| version | 必須 | integer | スキーマバージョン (最小値: 2) | 例: `2` |
| globals | 必須 | object | グローバル定義 (ネットワーク, データセンター, クラスター情報) | [表2] |
| nodes | 必須 | array | ノード (ホスト) のリスト | [表8] |

#### globals 構造 (表2)

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
| --- | --- | --- | --- | --- |
| auto_meshed_ebgp_transport_enabled | オプション | boolean | データセンタ間 eBGP トランスポートを自動メッシュ生成するか | 既定値: `true` |
| generate_internal_network_list | オプション | boolean | dns-server 向け `internal_network_list` を生成するか | 既定値: `true` |
| networks | 必須 | object | ネットワーク定義の辞書 (キー: ネットワーク名) | [表3] |
| datacenters | 必須 | object | データセンター定義の辞書 (キー: データセンター名) | [表6] |
| roles | オプション | object | ロール名からサービス一覧へのマップ | 例: `k8s_control_plane: [cilium, ...]`。サービス割り当てを持たない用途別ロールは空配列で定義できる (例: `terraform_orchestration: []`) |
| services | オプション | object | サービス既定値のマップ | 例: `dns-server.config.*`, `xcp_ng_environment.config.*` |
| scalars | オプション | object | 全ホスト向けスカラー既定値 | 例: `common_timezone` |
| reserved_nic_pairs | オプション | array | 予約NICペアのリスト。各要素は2要素の配列 `[NIC1, NIC2]` | 例: `[["enp1s0", "enp2s0"]]` |

#### network 要素の構造 (表3)

| フィールド名 | 必須/オプション | 型 | 値の範囲 | 説明 | 設定例 |
| --- | --- | --- | --- | --- | --- |
| role | 必須 | string | `external_control_plane_network`, `private_control_plane_network`, `data_plane_network`, `bgp_transport_network` | ネットワークの役割 | `"external_control_plane_network"` |
| datacenter | オプション | string | - | このネットワークが所属するデータセンターID (使用されていない) | `"dc1"` |
| cluster | オプション | string | - | このネットワークが所属する Kubernetes クラスター ID | `"cluster1"` |
| ipv4_cidr | オプション | string | CIDR形式 | IPv4 CIDR表記 | `"192.168.1.0/24"` |
| ipv6_cidr | オプション | string | CIDR形式 | IPv6 CIDR表記 | `"fd69:6684:61a:1::/64"` |
| gateway4 | オプション | string | IPv4アドレス | デフォルトIPv4ゲートウェイ | `"192.168.1.1"` |
| gateway6 | オプション | string | IPv6アドレス | デフォルトIPv6ゲートウェイ | `"fd69:6684:61a:1::1"` |
| gateway_node | オプション | string | ノードID | ゲートウェイとなるノードID (`private_control_plane_network` で使用) | `"gw01"` |
| dns_search | オプション | string | ドメイン名 | DNS検索ドメイン | `"example.com"` |
| name_servers_ipv4 | オプション | array | - | IPv4 DNSサーバーリスト | [表4] |
| name_servers_ipv6 | オプション | array | - | IPv6 DNSサーバーリスト | [表5] |
| use_dhcp4 | オプション | boolean | true/false | DHCPv4を使用するか | `false` |
| use_slaac | オプション | boolean | true/false | SLAAC (IPv6自動設定) を使用するか | `true` |
| route_metric_ipv4 | オプション | integer | 0以上 | IPv4のルートメトリック値 | `100` |
| route_metric_ipv6 | オプション | integer | 0以上 | IPv6のルートメトリック値 | `100` |
| ignore_auto_ipv4_dns | オプション | boolean | true/false | 自動取得したIPv4 DNSを無視するか | `true` |
| ignore_auto_ipv6_dns | オプション | boolean | true/false | 自動取得したIPv6 DNSを無視するか | `true` |

#### ネットワークロール (role) の説明

##### external_control_plane_network

外部管理ネットワーク。インターネットや組織外ネットワークへの接続に使用する。
このロールのネットワークに接続されたインターフェースが管理NIC (`mgmt_nic`) として優先される。

##### private_control_plane_network

内部管理ネットワーク。外部管理ネットワークへ直接接続されないノード群の管理通信に使用する。
`external_control_plane_network` が存在しない場合, このロールのネットワーク接続IFが管理NIC (`mgmt_nic`) として選択される。

##### data_plane_network

データプレーンネットワーク。Kubernetes ノード間通信やクラスタ内トラフィックで使用する。
このロールのネットワーク接続IFは `k8s_nic` 自動導出対象になる。

##### bgp_transport_network

FRR (Free Range Routing) ルータ間の BGP 交換用ネットワーク。データセンタ間 eBGP ネイバー自動導出で参照される。

#### name_servers_ipv4 要素 (表4)

| 型 | 値の範囲 | 説明 | 設定例 |
|----|---------|------|--------|
| string | IPv4アドレス | IPv4 DNSサーバーアドレス | `"8.8.8.8"` |

*配列として複数指定可能 (例: `["8.8.8.8", "8.8.4.4"]`)*

#### name_servers_ipv6 要素 (表5)

| 型 | 値の範囲 | 説明 | 設定例 |
|----|---------|------|--------|
| string | IPv6アドレス | IPv6 DNSサーバーアドレス | `"2606:4700:4700::1111"` |

*配列として複数指定可能*

#### datacenter 要素の構造 (表6)

| フィールド名 | 必須/オプション | 型 | 値の範囲 | 説明 | 設定例 |
|------------|----------------|----|---------|----|--------|
| name | 必須 | string | - | データセンター名 | `"DataCenter 1"` |
| asn | 必須 | integer | 1-4294967295 | このデータセンターのBGP AS番号 | `65011` |
| route_reflector | オプション | string | - | このデータセンターのルートリフレクタとなるノードID (name) | `"frr01"` |

#### nodes 要素 (各ノード) の構造 (表8)

| フィールド名 | 必須/オプション | 型 | 値の範囲 | 説明 | 設定例 |
|------------|----------------|----|---------|----|--------|
| name | 必須 | string | パターン: `^[A-Za-z0-9_-]+$` | ノード識別子 (内部参照用ID) | `"k8sworker0101"` |
| hostname_fqdn | 必須 | string | パターン: `^[A-Za-z0-9._-]+$` | ホスト名 (FQDN) | `"k8sworker0101.local"` |
| roles | 必須 | array[string] | 例: `k8s_control_plane`, `k8s_worker`, `infra_server`, `rancher`, `docker`, `dev_linux`, `route_reflector`, `internal_router`, `terraform_orchestration` | ノードのロール一覧 | `["k8s_worker"]` |
| datacenter | オプション | string | datacentersで定義した名前 | このノードが所属するデータセンター名 | `"dc1"` |
| cluster | オプション | string | - | 所属するKubernetesクラスター名 (K8sノードの場合) | `"cluster1"` |
| control_plane | オプション | string | - | 所属ワーカーが参照する control plane ノード名 | `"k8sctrlplane01"` |
| interfaces | 必須 | array | - | ネットワークインターフェースのリスト | [表9] |
| scalars | オプション | object | - | ホスト固有のスカラー変数 (任意のキー:値ペア) | [表10] |
| services | オプション | object | - | ホスト固有のサービス設定 (サービス名をキーとする辞書) | [表11] |
| k8s_bgp | オプション | object | - | Kubernetes BGP設定 | - |
| k8s_worker_frr | オプション | object | - | Kubernetes Worker FRR設定 | - |

#### interface 要素の構造 (表9)

| フィールド名 | 必須/オプション | 型 | 値の範囲 | 説明 | 設定例 |
|------------|----------------|----|---------|----|--------|
| netif | 必須 | string | - | ネットワークインターフェース名 | `"enp1s0"` |
| network | 必須 | string | networksで定義した名前 | 接続するネットワーク名 | `"mgmt_external"` (ネットワークID。roleは `external_control_plane_network`) |
| mac | オプション | string | MACアドレス形式 | MACアドレス | `"00:50:56:00:b8:e1"` |
| static_ipv4_addr | オプション | string | IPv4アドレス | 静的IPv4アドレス (未指定時はDHCPv4を使用) | `"192.168.30.81"` |
| static_ipv6_addr | オプション | string | IPv6アドレス | 静的IPv6アドレス (未指定時はSLAACを使用) | `"fdad:ba50:248b:1::81"` |
| gateway4 | オプション | string | IPv4アドレス | IPv4ゲートウェイ (ネットワーク既定値を上書き) | `"192.168.30.1"` |
| gateway6 | オプション | string | IPv6アドレス | IPv6ゲートウェイ (ネットワーク既定値を上書き) | `"fdad:ba50:248b:1::1"` |
| dns_search | オプション | string | ドメイン名 | DNS検索ドメイン (ネットワーク既定値を上書き) | `"example.com"` |
| name_server_ipv4_1 | オプション | string | IPv4アドレス | 1番目のIPv4 DNSサーバー | `"8.8.8.8"` |
| name_server_ipv4_2 | オプション | string | IPv4アドレス | 2番目のIPv4 DNSサーバー | `"8.8.4.4"` |
| name_server_ipv6_1 | オプション | string | IPv6アドレス | 1番目のIPv6 DNSサーバー | `"2606:4700:4700::1111"` |
| name_server_ipv6_2 | オプション | string | IPv6アドレス | 2番目のIPv6 DNSサーバー | `"2606:4700:4700::1001"` |

#### scalars 要素の構造 (表10)

ホスト固有のスカラー変数を格納するオブジェクト。任意のキー:値ペアを定義可能。

**よく使用されるフィールド例:**

| フィールド名 | 型 | 説明 | 設定例 |
|------------|----|----|--------|
| frr_bgp_asn | integer | FRR BGP AS番号 | `65011` |
| frr_bgp_router_id | string | FRR BGPルーターID | `"192.168.40.49"` |
| k8s_ctrlplane_host | string | Kubernetesコントロールプレーンホスト名 | `"k8sctrlplane01.local"` |
| k8s_pod_ipv4_network_cidr | string | Pod用IPv4 CIDR | `"10.244.0.0/16"` |
| k8s_cilium_cm_cluster_id | integer | CiliumクラスターID | `1` |

*その他, ホスト固有の任意の変数を定義可能*

#### services 要素の構造 (表11)

ホスト固有のサービス設定を格納するオブジェクト。サービス名をキーとし, 各値は `config` サブキーを持つ。

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
|------------|----------------|----|----|------|
| vm_params | オプション | object | XCP-ng 仮想マシン (VM) パラメータ設定 | [表11-A] |

#### vm_params.config の構造 (表11-A)

XCP-ng で構築する VM の個別パラメータを定義する。`generate_terraform_tfvars.py` が参照する。

| フィールド名 | 必須/オプション | 型 | 値の範囲 | 説明 | 設定例 |
|------------|----------------|----|---------|----|--------|
| vm_group | オプション | string | - | VM グループ名の明示指定。未指定時は `globals.services.xcp_ng_environment.config.vm_group_map` からロールで自動決定 | `"devlinux"` |
| template_type | 必須 | string | `ubuntu`, `rhel` | 使用するOSテンプレート種別 | `"ubuntu"` |
| firmware | 必須 | string | `uefi`, `bios` | VM のファームウェア種別 | `"uefi"` |
| resource_profile | オプション | string | - | VM リソースプロファイル名 (グループ既定値を上書き) | `"medium"` |
| vcpus | オプション | integer | 1以上 | vCPU 数 (グループ既定値・グローバル既定値を上書き) | `4` |
| memory_mb | オプション | integer | 1以上 | メモリ容量 (MiB 単位, グループ既定値・グローバル既定値を上書き) | `4096` |
| disk_gb | オプション | integer | 1以上 | ディスク容量 (GiB 単位, グループ既定値・グローバル既定値を上書き) | `25` |

### 入力ファイルスキーマ: network_topology.schema.yaml

#### スキーマメタ情報 (表S1)

| フィールド名 | 値 | 説明 |
|------------|----|----|
| $schema | `https://json-schema.org/draft/2020-12/schema` | JSON Schemaのバージョン |
| $id | `network_topology.schema.v2.yaml` | スキーマID |
| title | `network topology input schema (v2)` | スキーマのタイトル |
| description | (スキーマの説明) | ネットワークトポロジー定義のスキーマ |
| type | `object` | ルート要素の型 |

#### スキーマプロパティ定義 (表S2)

| プロパティ名 | 必須 | 型 | 説明 | 詳細参照 |
|-------------|------|----|----|---------|
| version | Yes | integer | スキーマバージョン (minimum: 2) | - |
| globals | Yes | object | グローバル定義 | [表S3] |
| nodes | Yes | array | ノードのリスト | items: object |

#### globals プロパティ定義 (表S3)

| プロパティ名 | 必須 | 型 | 制約 | 説明 |
|-------------|------|----|----|------|
| auto_meshed_ebgp_transport_enabled | No | boolean | - | データセンタ間 eBGP トランスポート自動メッシュ生成 |
| generate_internal_network_list | No | boolean | - | dns-server 向け `internal_network_list` 生成可否 |
| networks | Yes | object | minProperties: 1, additionalProperties: [表S4] | ネットワーク定義 |
| datacenters | Yes | object | additionalProperties: true | データセンター定義 |
| roles | No | object | additionalProperties: array[string] | ロール定義 |
| services | No | object | additionalProperties: object | サービス既定値 |
| scalars | No | object | additionalProperties: object | スカラー既定値 |
| reserved_nic_pairs | No | array | items: array (length=2, items=string) | 予約NICペア |

#### network additionalProperties スキーマ (表S4)

| プロパティ名 | 必須 | 型 | 制約 | 説明 |
|-------------|------|----|----|------|
| role | Yes | string | enum: [external_control_plane_network, private_control_plane_network, data_plane_network, bgp_transport_network] | ネットワークロール |
| datacenter | No | string | - | データセンターID |
| cluster | No | string | - | KubernetesクラスターID |
| ipv4_cidr | No | string | pattern: CIDR | IPv4 CIDR |
| ipv6_cidr | No | string | pattern: CIDR | IPv6 CIDR |
| gateway4 | No | string | - | IPv4ゲートウェイ |
| gateway6 | No | string | - | IPv6ゲートウェイ |
| gateway_node | No | string | - | ゲートウェイノードID |
| dns_search | No | string | - | DNS検索ドメイン |
| name_servers_ipv4 | No | array | items: {type: string} | IPv4 DNSサーバー |
| name_servers_ipv6 | No | array | items: {type: string} | IPv6 DNSサーバー |
| use_dhcp4 | No | boolean | - | DHCPv4使用可否 |
| use_slaac | No | boolean | - | SLAAC使用可否 |
| route_metric_ipv4 | No | integer | minimum: 0 | IPv4ルートメトリック |
| route_metric_ipv6 | No | integer | minimum: 0 | IPv6ルートメトリック |
| ignore_auto_ipv4_dns | No | boolean | - | IPv4 DNS自動取得を無視 |
| ignore_auto_ipv6_dns | No | boolean | - | IPv6 DNS自動取得を無視 |

### 出力ファイル形式: host_vars_structured.yaml

#### トップレベル構造 (表O1)

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
|------------|----------------|----|----|------|
| hosts | 必須 | array | ホスト情報のリスト | [表O2] |

#### host 要素の構造 (表O2)

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
|------------|----------------|----|----|------|
| hostname | 必須 | string | ホスト名 | - |
| scalars | 必須 | object | スカラー変数 (キー:値のペア) | [表O3] |
| netif_list | 必須 | array | ネットワークインターフェースのリスト | [表O4] |
| k8s_bgp | オプション | object | Kubernetes BGP設定 | - |
| k8s_worker_frr | オプション | object | Kubernetes Worker FRR設定 | - |
| frr_ebgp_neighbors | オプション | array | eBGP ネイバーリスト (IPv4) | [表O5] |
| frr_ebgp_neighbors_v6 | オプション | array | eBGP ネイバーリスト (IPv6) | [表O5] |
| frr_ibgp_neighbors | オプション | array | Kubernetes BGPネイバーリスト (IPv4) | [表O5] |
| frr_ibgp_neighbors_v6 | オプション | array | Kubernetes BGPネイバーリスト (IPv6) | [表O5] |
| frr_networks_v4 | オプション | array | 広告するIPv4ネットワーク | items: string |
| frr_networks_v6 | オプション | array | 広告するIPv6ネットワーク | items: string |

#### scalars の一般的なフィールド (表O3)

| フィールド名 | 型 | 説明 | 設定例 |
|------------|----|----|--------|
| mgmt_nic | string | 管理用NIC名 | `"enp1s0"` |
| frr_bgp_asn | integer | FRR BGP AS番号 | `65001` |
| frr_bgp_router_id | string | BGPルーターID | `"192.168.255.1"` |
| k8s_cilium_cm_cluster_name | string | Kubernetesクラスター名 | `"cluster1"` |
| k8s_cilium_cm_cluster_id | integer | Kubernetesクラスター識別子 | `1` |

*その他, 動的に生成されるスカラー変数が含まれる*

#### netif_list 要素の構造 (表O4)

| フィールド名 | 必須/オプション | 型 | 説明 | 設定例 |
|------------|----------------|----|----|--------|
| netif | 必須 | string | NIC名 | `"enp1s0"` |
| mac | オプション | string | MACアドレス | `"00:50:56:00:b8:e1"` |
| static_ipv4_addr | オプション | string | 静的IPv4アドレス | `"192.168.1.10"` |
| network_ipv4_prefix_len | オプション | integer | IPv4プレフィックス長 | `24` |
| static_ipv6_addr | オプション | string | 静的IPv6アドレス | `"fd69::10"` |
| network_ipv6_prefix_len | オプション | integer | IPv6プレフィックス長 | `64` |
| gateway4 | オプション | string | IPv4ゲートウェイ | `"192.168.1.1"` |
| gateway6 | オプション | string | IPv6ゲートウェイ | `"fd69::1"` |
| dns_search | オプション | string | DNS検索ドメイン | `"example.com"` |
| name_server_ipv4_1 | オプション | string | 1番目のIPv4 DNSサーバー | `"8.8.8.8"` |
| name_server_ipv4_2 | オプション | string | 2番目のIPv4 DNSサーバー | `"8.8.4.4"` |
| name_server_ipv6_1 | オプション | string | 1番目のIPv6 DNSサーバー | `"2606:4700:4700::1111"` |
| name_server_ipv6_2 | オプション | string | 2番目のIPv6 DNSサーバー | `"2606:4700:4700::1001"` |
| route_metric_ipv4 | オプション | integer | IPv4ルートメトリック | `100` |
| route_metric_ipv6 | オプション | integer | IPv6ルートメトリック | `100` |
| ignore_auto_ipv4_dns | オプション | boolean | IPv4 DNS自動取得を無視 | `true` |
| ignore_auto_ipv6_dns | オプション | boolean | IPv6 DNS自動取得を無視 | `true` |

#### frr_neighbor 要素の構造 (表O5)

BGPネイバー情報の構造。`frr_ebgp_neighbors`, `frr_ebgp_neighbors_v6`, `frr_ibgp_neighbors`, `frr_ibgp_neighbors_v6`の各配列に含まれる要素。

| フィールド名 | 必須/オプション | 型 | 説明 | 設定例 |
|------------|----------------|----|----|--------|
| addr | 必須 | string | ネイバーのIPアドレス | `"192.168.255.2"` |
| asn | 必須 | integer | ネイバーのAS番号 | `65002` |
| desc | 必須 | string | ネイバーの説明 | `"AS Number: 65002 - router2"` |

### 処理フロー

1. 入力ファイルの読み込み
   - network_topology.yaml を UTF-8 エンコーディングで読み込む
   - YAML パーサーでオブジェクトに変換

2. スキーマ検証 (オプション)
   - network_topology.schema.yaml を使用した JSON Schema バリデーション
   - 必須フィールドと型の確認

3. グローバル定義の抽出
   - `globals` セクションから以下を取得:
     - `networks`: ネットワーク定義の辞書
     - `datacenters`: データセンター定義の辞書
  - `roles`: ロール定義 (オプション)
  - `services`: サービス既定値 (オプション)
  - `scalars`: グローバルスカラー既定値 (オプション)
  - `auto_meshed_ebgp_transport_enabled`: eBGP 自動メッシュ生成可否 (オプション)
  - `generate_internal_network_list`: `internal_network_list` 生成可否 (オプション)
     - `reserved_nic_pairs`: 予約 NIC ペアのリスト (オプション)

4. reserved_nic_pairs の処理
   - 各要素を 2 要素タプル `(NIC1, NIC2)` に変換
   - インデックス指定で要素にアクセス: `(pair[0], pair[1])`

5. ノードマップの構築
   - `nodes` 配列を走査
   - `{name: node_object}` 形式の辞書を作成 (キーはノードの`name`フィールド)

6. 各ノードの処理
   - ノードごとに以下を実行:

   6-1. ホストエントリの初期化
       - `hostname` フィールドを設定 (`node.hostname_fqdn` から設定)

   6-2. スカラー変数の生成
        - ネットワーク設定から管理 NIC を特定
        - FRR 設定から BGP パラメータを抽出
        - Kubernetes 設定からクラスター情報を抽出
        - `scalars` 辞書に格納

   6-3. ネットワークインターフェースリストの生成
        - `node.interfaces` を走査
        - 各インターフェースについて:
          - ネットワーク定義から設定を取得
          - 静的 IP アドレスまたは DHCP 設定を決定
          - DNS サーバー設定を適用
        - `netif_list` 配列に追加

   6-4. BGP 設定の生成 (該当する場合)
        - Kubernetes BGP 設定 (`k8s_bgp`)
        - FRR eBGP ネイバー設定 (`frr_ebgp_neighbors`, `frr_ebgp_neighbors_v6`)
        - Kubernetes BGP ネイバー設定 (`frr_ibgp_neighbors`, `frr_ibgp_neighbors_v6`)
        - アドバタイズネットワーク (`frr_networks_v4`, `frr_networks_v6`)

7. 出力ファイルへの書き込み
   - `hosts` リストを含む YAML 構造を作成
   - 指定された出力パスに UTF-8 エンコーディングで書き込み
   - 成功メッセージを表示: `Generated: <output_path>`

### エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|-----------|------|------|
| 0 | 正常終了 | ファイル生成成功 |
| 1 | エラー | ファイル読み込み失敗, YAML解析エラー, バリデーションエラー等 |

### 使用例

```bash
# 基本的な使用例
python3 generate_host_vars_structured.py network_topology.yaml host_vars_structured.yaml

# 出力例:
# Generated: host_vars_structured.yaml
```

### 制限と注意事項

- 入力ファイルは UTF-8 エンコーディングである必要がある
- network_topology.schema.yaml がスキーマ検証に使用される (同一ディレクトリに配置)
- 予約 NIC ペア (reserved_nic_pairs) の各要素は正確に 2 要素のリストである必要がある

---

## generate_hostvars_matrix

### 概要

`host_vars_structured.yaml` と `field_metadata.yaml` から, ホスト横断のパラメタシートCSVを生成する。
行は設定項目 (`setting_name`) 単位, 列は固定4列 + ホスト列で構成される。
値取得は `scalars` を優先し, 未定義時はトップレベル項目を参照する。
加えて, `netif_list` は `netif_list[{IF名}].{sub_field}` 形式の展開行として追記される。

### SYNOPSIS

```plaintext
generate_hostvars_matrix.py [-h] [-H HOST_VARS] [-m METADATA] [-o OUTPUT]
```

### オプション

| オプション | 短縮 | 必須/オプション | 型 | デフォルト値 | 説明 |
|-----------|------|----------------|----|-----------|----|
| --help | -h | オプション | - | - | ヘルプメッセージを表示して終了 |
| --host-vars | -H | オプション | ファイルパス | host_vars_structured.yaml | 入力ホスト変数ファイル |
| --metadata | -m | オプション | ファイルパス | field_metadata.yaml | フィールドメタデータファイル |
| --output | -o | オプション | ファイルパス | (標準出力) | 出力CSVファイルパス |

### 入力ファイル形式

#### host_vars_structured.yaml

generate_host_vars_structured で生成されたファイル。

抽出対象:

- `scalars` 配下の各フィールド
- ホストトップレベルのフィールド (`hostname`, `scalars`, `netif_list` を除く)
- `netif_list` 配下の展開対象フィールド

#### field_metadata.yaml 構造 (表M1)

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
|------------|----------------|----|----|------|
| fields | 必須 | object | フィールド定義の辞書 (キー: フィールド名) | [表M2] |

#### field 要素の構造 (表M2)

| フィールド名 | 必須/オプション | 型 | 値の範囲 | 説明 | 設定例 |
|------------|----------------|----|---------|----|--------|
| type | 必須 | string | `str`, `int`, `bool` | フィールドの型 | `"str"` |
| description | 必須 | string | - | フィールドの説明 (日本語) | `"管理用ネットワークインターフェース (NIC) 名"` |
| category | 必須 | string | - | フィールドのカテゴリ (ソート用) | `"network"` |
| allowed_values | オプション | array | - | 許可される値のリスト | `["worker", "control_plane"]` |

### 出力ファイル形式: CSV

#### CSV 構造

| 列位置 | 列名 | 説明 | 例 |
|--------|------|------|-----|
| 1 | setting_name | 設定名 | `frr_bgp_asn`, `netif_list[enX0].static_ipv4_addr` |
| 2 | type | `field_metadata.yaml` 上の型 | `integer`, `string`, `array` |
| 3 | allowed_range | `allowed_range` の直列化結果 | `numeric[1:4294967295]` |
| 4 | description | `field_metadata.yaml` 上の説明 | `FRR BGP 自律システム番号` |
| 5以降 | 各ホスト名列 | ホストごとの値 | `65011`, `192.168.30.81` |

#### 値の直列化規則

- `None` -> 空文字
- `bool` -> `true` / `false`
- `list` -> 各要素を再帰直列化し `;` 連結
- `dict` -> JSONコンパクト文字列
- その他 -> `str(value)`

#### CSV 例

```csv
setting_name,type,allowed_range,description,extgw.local,frr01.local
frr_bgp_asn,integer,numeric[1:4294967295],FRR BGP 自律システム番号,65011,65011
frr_networks_v4,array,,FRRで広告するIPv4ネットワーク一覧,192.168.255.0/24;192.168.30.0/24,
netif_list[enX0].static_ipv4_addr,string,,固定IPv4アドレス,192.168.30.81,
```

### 処理フロー

1. host_vars_structured.yaml の読み込み
   - UTF-8 エンコーディングで読み込み
   - YAML パーサーでオブジェクトに変換

2. field_metadata.yaml の読み込み
  - フィールド定義を取得

3. ホスト列の決定
  - `hostname` を持つホストを対象に, 順序を保持して列ヘッダを作成

4. メタデータ定義フィールド行の生成
  - `fields` のキーをソートして走査
  - 値取得は `scalars` 優先, 未定義時はトップレベル参照
  - `type`, `allowed_range`, `description` を付与

5. netif 展開行の生成
  - 全ホストの `netif_list` から IF 名集合と sub_field 集合を抽出
  - `netif_list[{IF名}].{sub_field}` 行を生成して末尾へ追加

6. CSV ファイルまたは標準出力へ出力
  - `--output` 指定時: ファイルに書き込み
  - 未指定時: 標準出力に出力

### netif 展開行の命名規則

- 形式: `netif_list[{netif_name}].{sub_field}`
- 例: `netif_list[enX0].netif`, `netif_list[enX0].static_ipv4_addr`

### エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|-----------|------|------|
| 0 | 正常終了 | CSV生成成功 |
| 1 | エラー | ファイル読み込み失敗, YAML解析エラー等 |

### 使用例

```bash
# 標準出力への出力
python3 generate_hostvars_matrix.py

# ファイルへの出力
python3 generate_hostvars_matrix.py -o host_vars_scalars_matrix.csv
# 出力: CSV generated: host_vars_scalars_matrix.csv

# カスタムファイルの使用
python3 generate_hostvars_matrix.py -H custom.yaml -m custom_meta.yaml -o out.csv
```

### 制限と注意事項

- すべてのホストで共通して存在しない項目は空欄として出力される
- `netif_list` 展開行は, IF 名集合 × sub_field 集合の組み合わせで生成される
- CSV出力は UTF-8 エンコーディングで行われる

---

## generate_host_vars_files

### 概要

host_vars_structured.yaml からホスト別の YAML ファイルを生成する。
各ホストのファイルにはメタデータコメントが 80 文字で折り返されて挿入される。

### SYNOPSIS

```plaintext
generate_host_vars_files.py [-h] [-i INPUT_STRUCTURED] [-m METADATA]
                            [-w {true,false}] [-v {true,false}]
                            output_dir
```

### 引数とオプション

| 引数/オプション | 短縮 | 必須/オプション | 型 | デフォルト値 | 説明 |
|---------------|------|----------------|----|-----------|----|
| output_dir | - | 必須 (位置引数) | ディレクトリパス | - | 生成ファイルの保存先ディレクトリ |
| --help | -h | オプション | - | - | ヘルプメッセージを表示 |
| --input-structured | -i | オプション | ファイルパス | host_vars_structured.yaml | 入力ホスト変数ファイル |
| --metadata | -m | オプション | ファイルパス | field_metadata.yaml | メタデータファイル |
| --overwrite | -w | オプション | 列挙型 | true | 既存ファイル上書き制御 |
| --validate-roundtrip | -v | オプション | 列挙型 | false | ラウンドトリップ検証の有効化 |

### 入力ファイル形式

#### host_vars_structured.yaml

generate_host_vars_structured で生成された構造化ファイル。

#### field_metadata.yaml

各フィールドのメタデータ。メタデータの `description` がコメントとして挿入される。

### 出力ファイル形式

#### ファイル名規則

| 規則 | 説明 | 例 |
|------|------|-----|
| パス | `<output_dir>/<hostname>` | `/path/to/output/server1.example.com` |
| 拡張子 | なし (YAML ファイルだが拡張子なし) | - |

#### 出力 YAML 構造の例

```yaml
# 管理用ネットワークインターフェース (NIC) 名
mgmt_nic: enp1s0

# FRR ボーダーゲートウェイプロトコル (BGP) 自律システム (AS) 番号
frr_bgp_asn: 65001

# FRR ボーダーゲートウェイプロトコル (BGP) ルーター識別子 (ID)
frr_bgp_router_id: "192.168.255.1"

netif_list:
  - netif: enp1s0
    mac: "00:50:56:00:b8:e1"
    static_ipv4_addr: "192.168.1.10"
    network_ipv4_prefix_len: 24
```

#### コメント挿入規則

| 規則 | 説明 |
|------|------|
| 挿入位置 | スカラーフィールドの直前行 |
| フォーマット | `# <説明文>` |
| 折り返し | 80 文字を超える場合は複数行に分割 |
| メタデータなし | メタデータに定義がない場合はコメントなし |

### 処理フロー

1. host_vars_structured.yaml の読み込み
   - UTF-8 エンコーディングで読み込み
   - YAML パーサーでオブジェクトに変換

2. field_metadata.yaml の読み込み
   - フィールドメタデータを取得
   - 各フィールドの `description` を取得

3. 出力ディレクトリの作成 (存在しない場合)
   - 指定されたディレクトリパスが存在しない場合は作成
   - 親ディレクトリも必要に応じて作成

4. 各ホストについてループ

   4-1. ファイルパスの決定
        - `output_dir/hostname` のパスを構築

   4-2. 既存ファイルチェック (`--overwrite=false` の場合)
        - ファイルが既に存在する場合はスキップ
        - スキップした場合はメッセージを出力

   4-3. スカラー変数にメタデータコメント挿入
        - 各スカラーフィールドについて:
          - メタデータから `description` を取得
          - 80 文字で折り返し処理
          - `# ` プレフィックスを追加
          - フィールドの直前に挿入

   4-4. YAML ファイルとして出力
        - UTF-8 エンコーディングで書き込み
        - YAML フォーマットで整形

5. ラウンドトリップ検証 (`--validate-roundtrip=true` の場合)
   - 生成された各ファイルを再読み込み
   - 元の `host_vars_structured.yaml` のデータと比較
   - 不一致があればエラーを報告

### 上書き制御

| オプション値 | 動作 |
|------------|------|
| true (既定) | 既存ファイルを無条件に上書き |
| false | 既存ファイルが存在する場合はスキップ |

### ラウンドトリップ検証

| オプション値 | 動作 |
|------------|------|
| true | 生成ファイルを再読み込みし元データと照合 |
| false (既定) | 検証しない |

検証で不一致が検出された場合, エラーメッセージを出力して終了コード 1 で終了。

### エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|-----------|------|------|
| 0 | 正常終了 | ファイル生成成功 |
| 1 | エラー | ディレクトリ作成失敗, ファイル書き込み失敗, ラウンドトリップ検証失敗等 |

### 使用例

```bash
# 基本的な使用例
python3 generate_host_vars_files.py /path/to/output_dir
# 出力: Generated 25 host_vars files under: /path/to/output_dir

# 上書き無効化
python3 generate_host_vars_files.py /path/to/output_dir -w false

# ラウンドトリップ検証を有効化
python3 generate_host_vars_files.py /path/to/output_dir -v true

# すべてのオプションを指定
python3 generate_host_vars_files.py /path/to/output_dir \
  -i custom_hostvars.yaml \
  -m custom_metadata.yaml \
  -w false \
  -v true
```

### 制限と注意事項

- ホスト名にファイルシステムで無効な文字が含まれる場合は注意が必要
- メタデータに定義されていないフィールドにはコメントが付与されない
- ラウンドトリップ検証は YAML のキー順序の違いは許容するが, 値の不一致は検出する

---

## validate_hostvars_matrix

### 概要

`generate_hostvars_matrix.py` で生成されたCSVの構造整合性を検証する。
本ツールは形式検証に特化し, 値の意味的妥当性やソース値との厳密比較は行わない。

### SYNOPSIS

```plaintext
validate_hostvars_matrix.py [-h] [-c CSV] [-m METADATA] [-H HOST_VARS]
```

### オプション

| オプション | 短縮 | 必須/オプション | 型 | デフォルト値 | 説明 |
|-----------|------|----------------|----|-----------|----|
| --help | -h | オプション | - | - | ヘルプメッセージを表示 |
| --csv | -c | オプション | ファイルパス | host_vars_scalars_matrix.csv | 検証対象CSVファイル |
| --metadata | -m | オプション | ファイルパス | field_metadata.yaml | メタデータファイル |
| --host-vars | -H | オプション | ファイルパス | host_vars_structured.yaml | 元のホスト変数ファイル |

### 検証項目

| 検証項目 | 検証内容 | エラー条件 |
|---------|---------|-----------|
| CSV 構造検証 | ヘッダー行の存在, 全行の列数一致 | ヘッダーなし, 列数不一致 |
| 固定列検証 | 先頭4列が `setting_name,type,allowed_range,description` か | 列名不一致 |
| フィールド整合性 | メタデータ定義行の欠落/余剰の有無 | 欠落フィールド, 未許可余剰フィールド |
| netif 展開整合性 | `netif_list[*].*` 行を追加行として許容し件数を検証 | 期待件数不一致 |
| ホスト列整合性 | `host_vars_structured.yaml` 側ホスト集合と一致するか | 欠落ホスト, 余剰ホスト |
| allowed_range 形式検証 | `numeric[` などの直列化形式か | 形式不正 |

### 処理フロー

1. CSV ファイルの読み込み
   - UTF-8 エンコーディングで読み込み
   - CSV パーサーで解析
   - ヘッダー行を抽出

2. field_metadata.yaml の読み込み
  - フィールドメタデータを取得

3. host_vars_structured.yaml の読み込み
  - `hostname` を持つホスト集合を取得
  - netif 展開期待件数を算出する

4. CSV 構造検証の実行
   - ヘッダー行が存在するか確認
  - 固定列ヘッダーが一致するか確認
   - 各データ行の列数がヘッダーと一致するか確認
   - 不一致があればエラーを記録

5. メタデータ整合性検証の実行
  - `setting_name` 列の集合を確認
  - `netif_list[*].*` 以外の余剰行を検出
  - 欠落フィールドを検出

6. 件数整合性検証の実行
  - 期待件数 = メタデータ行数 + netif 展開期待件数
  - CSV 実行数との差分を検証

7. ホスト列整合性検証の実行
  - CSV ヘッダーのホスト列と `host_vars_structured.yaml` のホスト集合を比較

8. allowed_range 形式検証の実行
  - `allowed_range` 列が許可形式 (`numeric[...]` など) か確認

9. 結果の集計と表示
   - エラーがなければ成功メッセージを表示
   - エラーがあればエラー内容を表示
   - 適切な終了コードで終了

### 検証結果

| 結果 | 出力メッセージ | 終了コード |
|------|--------------|-----------|
| 成功 | `✓ CSV validation passed` | 0 |
| 失敗 | `✗ CSV validation failed` + エラー詳細 | 1 |

### エラーメッセージの例

```
✗ CSV validation failed
Error: CSV header mismatch. Expected ['setting_name', 'type', 'allowed_range', 'description'], got ['hostname', ...]
Error: Missing fields in CSV: ['frr_bgp_asn']
Error: Field count mismatch: CSV has 120 rows, expected 124 (100 fields + 24 netif rows)
```

### 使用例

```bash
# デフォルトファイルでの検証
python3 validate_hostvars_matrix.py
# 出力: ✓ CSV validation passed

# カスタムファイルでの検証
python3 validate_hostvars_matrix.py \
  -c custom_matrix.csv \
  -m custom_meta.yaml \
  -H custom_hostvars.yaml

# パイプラインでの使用
python3 generate_hostvars_matrix.py -o matrix.csv && \
python3 validate_hostvars_matrix.py -c matrix.csv
```

### 制限と注意事項

- CSV ファイルは UTF-8 エンコーディングである必要がある
- `netif_list[*].*` 形式行は追加行として許容される
- 値そのものの意味的妥当性検証 (例: CIDRの正しさ) は行わない

---

## generate_terraform_tfvars

### 概要

`network_topology.yaml` を読み込んで, XCP-ng 仮想化環境向けの Terraform 変数ファイル (`terraform.tfvars`) を HCL (HashiCorp Configuration Language) 形式で生成する。
`globals.roles.terraform_orchestration: []` を定義した Terraform 対象ロールを持つノードに対して生成する。
Ansible 向けツールチェイン (1)〜(4) とは独立して動作する単独ツールである。

### SYNOPSIS

```plaintext
generate_terraform_tfvars.py [-h] [-t TOPOLOGY] [-o OUTPUT] [-n] [-s]
```

### オプション

| オプション | 短縮 | 必須/オプション | 既定値 | 説明 |
|-----------|------|----------------|--------|------|
| `--help` | `-h` | オプション | - | ヘルプメッセージを表示して終了 |
| `--topology` | `-t` | オプション | `network_topology.yaml` | 入力となるネットワークトポロジー YAML ファイル |
| `--output` | `-o` | オプション | `terraform.tfvars` | 出力先 Terraform 変数ファイル |
| `--dry-run` | `-n` | オプション | `false` | ファイルを書き込まず, 生成内容を標準出力に表示する |
| `--strict` | `-s` | オプション | `false` | 必須キーの欠落を厳格にエラー扱いにする (既定: 警告のみ) |

### 入力ファイル形式 (generate_terraform_tfvars 固有)

`generate_host_vars_structured` と同一の `network_topology.yaml` を入力とする。
Terraform 生成に必要な追加フィールドを以下に示す。

#### globals.roles の Terraform 関連設定

| キー | 型 | 説明 | 設定例 |
|------|----|----|--------|
| terraform_orchestration | array[string] | Terraform 対象ロール。配列要素は空で構わない | `terraform_orchestration: []` |

#### globals.services.xcp_ng_environment.config の構造 (表T1)

XCP-ng 環境への接続情報と VM テンプレート設定を定義する。

| フィールド名 | 必須/オプション | 型 | 説明 | 設定例 |
|------------|----------------|----|----|--------|
| xoa_url | 必須 | string | XOA の API エンドポイント URL | `"https://xoa.example.com"` |
| xoa_username | 必須 | string | XOA ログインユーザー名 | `"admin@example.com"` |
| xoa_insecure | オプション | boolean | TLS 証明書検証をスキップするか | `false` |
| xcpng_pool_name | 必須 | string | XCP-ng リソースプール名 | `"pool01"` |
| xcpng_sr_name | 必須 | string | XCP-ng ストレージリポジトリ名 | `"Local storage"` |
| xcpng_template_ubuntu | 必須 | string | Ubuntu 用テンプレート名 | `"Ubuntu 22.04 LTS"` |
| xcpng_template_rhel | 必須 | string | RHEL 系 OS 用テンプレート名 | `"AlmaLinux 9"` |
| xcpng_vm_vcpus | オプション | integer | VM のデフォルト vCPU 数 | `4` |
| xcpng_vm_mem_mb | オプション | integer | VM のデフォルトメモリ容量 (MiB) | `4096` |
| xcpng_vm_disk_gb | オプション | integer | VM のデフォルトディスク容量 (GiB) | `25` |
| network_key_map | 必須 | object | topology 内ネットワークキー → Terraform 通常ネットワークキーへの変換マップ | `{mgmt_external: ext_mgmt, k8s_net1: k8s_net01}` |
| network_names | 必須 | object | Terraform ネットワークキー → 表示名のマップ | `{ext_mgmt: "Pool-wide network associated with eth0"}` |
| network_roles | オプション | object | ネットワーク役割 → Terraform 通常ネットワークキー配列のマップ (生成時に自動構築) | `{external_control_plane_network: [ext_mgmt]}` |
| network_options | オプション | object | ネットワーク別のオプション設定 (追加 HCL プロパティ) | `{}` |
| vm_group_map | 必須 | object | ロール名 → VM グループ名への変換マップ | `{k8s_worker: k8s, infra_server: infrastructure}` |
| vm_group_defaults | 必須 | object | VM グループごとのデフォルト設定 | [表T2] |

#### vm_group_defaults の構造 (表T2)

`vm_group_defaults` の各キーは VM グループ名で, 値は以下の構造を持つ。

| フィールド名 | 必須/オプション | 型 | 説明 | 設定例 |
|------------|----------------|----|----|--------|
| default_template_type | 必須 | string | グループのデフォルト OS テンプレート種別 (`ubuntu` または `rhel`) | `"ubuntu"` |
| default_firmware | 必須 | string | グループのデフォルトファームウェア (`uefi` または `bios`) | `"uefi"` |
| default_resource_profile | オプション | string | グループのデフォルトリソースプロファイル名 | `"standard"` |

### 出力ファイル形式: terraform.tfvars

HCL (HashiCorp Configuration Language) 形式のテキストファイル。Terraform `xcp-ng` プロバイダーで使用する。

#### トップレベル変数 (表TV1)

| 変数名 | 型 | 説明 |
|--------|----|----|
| xoa_url | string | XOA API エンドポイント URL |
| xoa_username | string | XOA ユーザー名 |
| xoa_insecure | bool | TLS 証明書スキップフラグ |
| xcpng_pool_name | string | XCP-ng プール名 |
| xcpng_sr_name | string | ストレージリポジトリ名 |
| xcpng_template_ubuntu | string | Ubuntu テンプレート名 |
| xcpng_template_rhel | string | RHEL テンプレート名 |
| xcpng_vm_vcpus | number | デフォルト vCPU 数 |
| xcpng_vm_mem_mb | number | デフォルトメモリ (MiB) |
| xcpng_vm_disk_gb | number | デフォルトディスク (GiB) |
| network_names | map(string) | ネットワーク表示名マップ |
| network_roles | map(list(string)) | ネットワーク役割マップ |
| network_options | map(any) | ネットワーク追加オプションマップ |
| vm_group_defaults | map(object) | VM グループ別デフォルト設定マップ |
| vm_groups | map(map(object)) | グループ別 VM 定義マップ |

#### vm_groups の構造

```hcl
vm_groups = {
  "<group>" = {
    "<vm_name>" = {
      template_type     = "ubuntu"
      firmware          = "uefi"
      resource_profile  = "standard"   # optional
      networks = [
        {
          network_key = "ext_mgmt"
          mac_address = "00:50:56:00:b8:e1"
        },
        ...
      ]
    }
  }
}
```

### 処理フロー

1. `network_topology.yaml` を読み込む
2. `globals.services.xcp_ng_environment.config` から環境設定を取得し必須キーを検証する
3. `globals.roles.terraform_orchestration` を持つノードを抽出する (`roles` 配列を参照)
4. 各対象ノードについて:
   - `services.vm_params.config.vm_group` の明示指定を確認する
   - 未指定の場合は `vm_group_map` でロールからグループを決定する
  - インターフェース定義を `network_key_map` で変換して `networks` リストを構築する
    - `node.interfaces[*].network` が `network_key_map` 未登録の場合は `ValueError` で処理を停止する
   - `template_type`, `firmware`, `resource_profile` はノード設定→グループ既定値の優先順で決定する
5. `vm_groups` 辞書を構築する
6. `globals.networks.role` から `network_roles` を自動構築する
  - `globals.networks` の network 名が `network_key_map` 未登録の場合は `network_roles` へ含めない (エラーにはしない)
7. HCL 形式でレンダリングして出力ファイルへ書き込む

### エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|-----------|------|------|
| 0 | 正常終了 | ファイル生成成功 |
| 1 | エラー | ファイル読み込み失敗, 必須キー欠落, グループ解決失敗等 |

### 使用例

```bash
# 基本的な使用例 (カレントディレクトリのデフォルトファイルを使用)
python3 src/prototype/generate_terraform_tfvars.py

# 入力・出力ファイルを明示指定
python3 src/prototype/generate_terraform_tfvars.py \
  -t src/prototype/network_topology.yaml \
  -o terraform.tfvars

# 内容を確認してからファイル生成 (-n / --dry-run)
python3 src/prototype/generate_terraform_tfvars.py \
  -t src/prototype/network_topology.yaml \
  -n

# 必須キー欠落を厳格にエラーとして扱う (-s / --strict)
python3 src/prototype/generate_terraform_tfvars.py \
  -t src/prototype/network_topology.yaml \
  -o terraform.tfvars \
  -s
```

### 制限と注意事項

- `globals.roles.terraform_orchestration` が定義されていない場合, 対象ノードが0件となり空の `vm_groups` が出力される
- ロールから VM グループへの変換 (`vm_group_map`) に一致するロールが無く, `vm_params.config.vm_group` も未設定の場合はエラーになる
- ネットワークキー変換 (`network_key_map`) に存在しないインターフェースのネットワークキーはエラーとして扱われる
- `globals.networks` 由来の `network_roles` 生成では, `network_key_map` 未登録の network は出力に含めない (エラーにはしない)
- `xoa_password` は `terraform.tfvars` へは出力されない。Terraform 実行時に環境変数 `TF_VAR_xoa_password` で指定すること

---

## generate_network_topology_design_sheet

### 概要

`network_topology.yaml`, `field_metadata.yaml`, `network_topology.schema.yaml` を読み込み, globals, roles, services, hosts の4つの独立したCSVデザインシートファイルを生成する。
description は `field_metadata.yaml` の `design_sheet_descriptions` を優先して参照し, 未定義項目はスキーマの `description` にフォールバックする。どちらにも定義がない項目は description を空欄で出力しつつ警告を標準エラーへ出力する。

### SYNOPSIS

```plaintext
generate_network_topology_design_sheet.py [-h] [-i INPUT] [-o OUTPUT] [-m METADATA]
```

### オプション

| オプション | 短縮 | 必須/オプション | 既定値 | 説明 |
|-----------|------|----------------|--------|------|
| `--help` | `-h` | オプション | - | ヘルプメッセージを表示して終了 |
| `--input` | `-i` | オプション | `network_topology.yaml` | 入力トポロジー YAML |
| `--output` | `-o` | オプション | `network_topology.csv` | 出力パスのヒント (ディレクトリまたはファイルパス).出力ファイル名は入力ファイル名から自動決定 |
| `--metadata` | `-m` | オプション | `network_topology.schema.yaml` | description フォールバックに使用するスキーマ YAML |

### 入力ファイル形式

- `network_topology.yaml`
  - 必須トップレベルキー: `version`, `globals`, `nodes`
- `field_metadata.yaml` (オプション, 入力ファイルと同じディレクトリから自動検索)
  - `design_sheet_descriptions` セクションを description の優先解決元として使用する
- `network_topology.schema.yaml`
  - description のフォールバック解決元として使用する
  - 未定義の `description` は警告対象になるが処理は継続する

### 出力ファイル形式

4つの独立したCSVファイルを生成する。ファイル名は入力ファイルのベース名 (拡張子除く) とセクション名を `-` で連結した形式になる。

| ファイル名 | セクション | 列構成 |
|---------|-------|-------|
| `{input_stem}-globals.csv` | globals 設定 | `item`, `parameter`, `description`, `value` |
| `{input_stem}-roles.csv` | role 設定 | `item`, `parameter`, `description`, `value` |
| `{input_stem}-services.csv` | service 設定 | `item`, `parameter`, `description`, `value` |
| `{input_stem}-hosts.csv` | ホスト別設定 | `parameter`, `description`, `{hostname_1}`, `{hostname_2}`, ... |

#### globals / roles / services の列

| 列名 | 説明 |
|------|------|
| item | 対象キーまたはグループ名 |
| parameter | 項目名または dot path |
| description | 解決した説明文 |
| value | 値 |

#### hosts の列

| 列名 | 説明 |
|------|------|
| parameter | 行種別とパラメータ名を `.` で連結した識別子 (例: `host_scalar.scalars.frr_bgp_asn`) |
| description | 解決した説明文 |
| {hostname} | 各ホスト名を列名とした値列 |

### 処理フロー

1. 入力トポロジーとスキーマを読み込む。
2. 入力ファイルと同じディレクトリに `field_metadata.yaml` があれば読み込み, description 先行索引を構築する。
3. 必須トップレベルキー (`version`, `globals`, `nodes`) を検証する。
4. スキーマから description フォールバック索引を構築する。
5. `globals`, `roles`, `services`, `hosts` の各行を生成する。
6. 各セクションを山別CSVファイルに書き出す。
7. description 未解決パスを警告として標準エラーへ出力する。

### エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|-----------|------|------|
| 0 | 正常終了 | CSVファイル生成成功 (description 欠落警告のみの場合も含む) |
| 1 | エラー | 入力ファイル不存在, YAMLパース失敗, 必須キー欠落, 型不一致など |

### 使用例

```bash
# デフォルトファイルで生成
python3 src/prototype/generate_network_topology_design_sheet.py

# 入力, スキーマ, 出力を明示指定
python3 src/prototype/generate_network_topology_design_sheet.py \
  -i src/prototype/network_topology.yaml \
  -m src/prototype/network_topology.schema.yaml \
  -o src/prototype/
```

上記の実行により `network_topology-globals.csv`, `network_topology-roles.csv`, `network_topology-services.csv`, `network_topology-hosts.csv` の4ファイルが生成される。

### 制限と注意事項

- 出力CSVはレビュー用途の設計シートであり, 既存の `generate_hostvars_matrix.py` が出力するクロスチェックCSVとは目的が異なる
- `field_metadata.yaml` の `design_sheet_descriptions` に定義がない項目はスキーマの description を参照する
- どちらにも定義がない項目は description 列が空欄になる
- warning は標準エラー出力へ出るため, CIで扱う場合は標準エラーの取り扱い方針を明確化すること

---

## ワークフロー例

### 標準的な処理フロー

**Ansible パス**

| ステップ | コマンド | 入力 | 出力 |
|---------|---------|------|------|
| 1. トポロジー → 構造化 | generate_host_vars_structured.py | network_topology.yaml | host_vars_structured.yaml |
| 2. 構造化 → CSV | generate_hostvars_matrix.py | host_vars_structured.yaml, field_metadata.yaml | CSV |
| 3. CSV 検証 | validate_hostvars_matrix.py | CSV, metadata, host_vars_structured | 検証結果 |
| 4. ホスト別ファイル生成 | generate_host_vars_files.py | host_vars_structured.yaml, field_metadata.yaml | ホスト別 YAML ファイル群 |

**Terraform パス (独立実行)**

| ステップ | コマンド | 入力 | 出力 |
|---------|---------|------|------|
| T. tfvars 生成 | generate_terraform_tfvars.py | network_topology.yaml | terraform.tfvars |

**トポロジーデザインシートパス (独立実行)**

| ステップ | コマンド | 入力 | 出力 |
|---------|---------|------|------|
| D. デザインシート生成 | generate_network_topology_design_sheet.py | network_topology.yaml, field_metadata.yaml, network_topology.schema.yaml | network_topology-globals.csv, network_topology-roles.csv, network_topology-services.csv, network_topology-hosts.csv |

### コマンド例

```bash
# ステップ1: 構造化ファイル生成
python3 generate_host_vars_structured.py \
  network_topology.yaml \
  host_vars_structured.yaml

# ステップ2: パラメタシート生成
python3 generate_hostvars_matrix.py \
  -o host_vars_scalars_matrix.csv

# ステップ3: CSV 検証
python3 validate_hostvars_matrix.py \
  -c host_vars_scalars_matrix.csv

# ステップ4: ホスト別ファイル生成
python3 generate_host_vars_files.py \
  /path/to/host_vars \
  -v true

# Terraform 変数ファイル生成 (独立実行)
python3 generate_terraform_tfvars.py

# トポロジーデザインシート生成 (独立実行)
python3 generate_network_topology_design_sheet.py
```

### 実行例

すべてのステップを一度に実行 (エラー時は即座に停止)する場合の例を以下に示す:

```bash
python3 generate_host_vars_structured.py network_topology.yaml host_vars_structured.yaml && \
python3 generate_hostvars_matrix.py -o host_vars_scalars_matrix.csv && \
python3 validate_hostvars_matrix.py -c host_vars_scalars_matrix.csv && \
python3 generate_host_vars_files.py /path/to/host_vars -v true && \
echo "✓ All Ansible steps completed successfully"

# Terraform 変数ファイル生成 (独立)
python3 generate_terraform_tfvars.py && \
echo "✓ Terraform tfvars generated"

# トポロジーデザインシート生成 (独立)
python3 generate_network_topology_design_sheet.py && \
echo "✓ Topology design sheet generated"
```

---

## 参照

### 関連ファイル一覧

| ファイル名 | 用途 | 形式 |
|-----------|------|------|
| network_topology.yaml | ネットワークトポロジー定義 | YAML |
| network_topology.schema.yaml | トポロジースキーマ | JSON Schema (YAML) |
| host_vars_structured.yaml | ホスト変数構造化ファイル | YAML |
| host_vars_structured.schema.yaml | ホスト変数スキーマ | JSON Schema (YAML) |
| field_metadata.yaml | フィールドメタデータ定義 | YAML |
| field_metadata.schema.yaml | メタデータスキーマ | JSON Schema (YAML) |
| host_vars_scalars_matrix.csv | パラメタシート | CSV |
| network_topology-globals.csv | トポロジーデザインシート (globalsセクション) | CSV |
| network_topology-roles.csv | トポロジーデザインシート (rolesセクション) | CSV |
| network_topology-services.csv | トポロジーデザインシート (servicesセクション) | CSV |
| network_topology-hosts.csv | トポロジーデザインシート (hostsセクション) | CSV |
| terraform.tfvars | XCP-ng 向け Terraform 変数ファイル | HCL (Terraform) |

### ディレクトリ構成例

```
src/prototype/
├── network_topology.yaml
├── network_topology.schema.yaml
├── host_vars_structured.yaml
├── host_vars_structured.schema.yaml
├── field_metadata.yaml
├── field_metadata.schema.yaml
├── host_vars_scalars_matrix.csv
├── network_topology-globals.csv
├── network_topology-roles.csv
├── network_topology-services.csv
├── network_topology-hosts.csv
├── terraform.tfvars
├── generate_host_vars_structured.py
├── generate_hostvars_matrix.py
├── generate_host_vars_files.py
├── validate_hostvars_matrix.py
├── generate_terraform_tfvars.py
├── generate_network_topology_design_sheet.py
└── commands-specJP.md (本書)
```

### 関連ドキュメント

| ドキュメント | 説明 |
|------------|------|
| README.md | プロジェクト概要 |
| SPECIFICATION.md | 設計メモ |

---

## 付録

### 補足事項

#### network_topology.yaml のネットワーク定義で必須のフィールド

`role` フィールドのみが必須です。その他のフィールドはすべてオプションですが, ネットワークの役割によって推奨されるフィールドが異なります。

#### reserved_nic_pairs の使用用途

特定の NIC ペアを処理から除外するために使用されます。例えば, bonding や teaming で使用される NIC ペアを指定します。

#### パラメタシートのフィールド順序変更方法

field_metadata.yaml の各フィールドの `category` を変更することで, CSV の列順序を制御できます。カテゴリごとにグループ化され, 同一カテゴリ内ではアルファベット順にソートされます。

#### ラウンドトリップ検証で不一致が検出された場合の対処方法

検証エラーの詳細を確認し, 以下を確認してください:

- YAML ファイルの文字エンコーディングが UTF-8 であること
- 特殊文字が正しくエスケープされていること
- 数値型のフィールドが文字列として解釈されていないこと

### トラブルシューティング

| 問題 | 原因 | 解決方法 |
|------|------|---------|
| YAML 解析エラー | 不正なYAML構文 | YAML リンター (yamllint) で構文チェック |
| スキーマ検証エラー | 必須フィールドの欠落または型の不一致 | エラーメッセージを確認し該当フィールドを修正 |
| CSV 検証失敗 | 元データとの不一致 | host_vars_structured.yaml と CSV を比較 |
| ファイル生成失敗 | ディレクトリの書き込み権限不足 | 出力ディレクトリの権限を確認 |
