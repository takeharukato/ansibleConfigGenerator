# generate_host_vars_structured

データセンタ内のコンピューティングノードの機能定義やネットワークトポロジ定義を記載したファイル(`network_topology.yaml`)から, host_varsに出力する変数の構造化ファイル (`host_vars_structured.yaml`) を生成します。

## 目次

- [generate\_host\_vars\_structured](#generate_host_vars_structured)
  - [目次](#目次)
  - [SYNOPSIS](#synopsis)
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
    - [services 要素の構造 (表11)](#services-要素の構造-表11)
    - [vm\_params.config の構造 (表11-A)](#vm_paramsconfig-の構造-表11-a)
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


## SYNOPSIS

```plaintext
generate_host_vars_structured [-h] [-i INPUT] [-o OUTPUT] [--schema-dir SCHEMA_DIR]
```

## オプション

| オプション | 必須/オプション | 型 | 既定値 | 説明 |
|-----------|----------------|----|--------|------|
| `-h`, `--help` | オプション | - | - | ヘルプメッセージを表示して終了 |
| `-i`, `--input` | オプション | ファイルパス | `network_topology.yaml` | 入力となるネットワークトポロジーYAMLファイル |
| `-o`, `--output` | オプション | ファイルパス | `host_vars_structured.yaml` | 出力先のホスト変数構造化YAMLファイル |
| `--schema-dir` | オプション | ディレクトリパス | `None` | スキーマ/設定YAML探索先ディレクトリを最優先で指定 |


## 入力ファイル形式: network_topology.yaml

### トップレベル構造 (表1)

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
|------------|----------------|----|----|------|
| version | 必須 | integer | スキーマバージョン (最小値: 2) | 例: `2` |
| globals | 必須 | object | グローバル定義 (ネットワーク, データセンター, クラスター情報) | [表2] |
| nodes | 必須 | array | ノード (ホスト) のリスト | [表8] |

### globals 構造 (表2)

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
| --- | --- | --- | --- | --- |
| auto_meshed_ebgp_transport_enabled | オプション | boolean | データセンタ間 eBGP トランスポートを自動メッシュ生成する設定であることを示す | 既定値: `true` |
| generate_internal_network_list | オプション | boolean | dns-server 向け `internal_network_list` を生成する設定であることを示す | 既定値: `true` |
| networks | 必須 | object | ネットワーク定義の辞書 (キー: ネットワーク名) | [表3] |
| datacenters | 必須 | object | データセンター定義の辞書 (キー: データセンター名) | [表6] |
| roles | オプション | object | ロール名からサービス一覧へのマップ | 例: `k8s_control_plane: [cilium, ...]`。サービス割り当てを持たない用途別ロールは空配列で定義できる (例: `terraform_orchestration: []`) |
| services | オプション | object | サービス既定値のマップ | 例: `dns-server.config.*`, `xcp_ng_environment.config.*` |
| scalars | オプション | object | 全ホスト向けスカラー既定値 | 例: `common_timezone` |
| reserved_nic_pairs | オプション | array | 予約NICペアのリスト。各要素は2要素の配列 `[NIC1, NIC2]` | 例: `[["enp1s0", "enp2s0"]]` |

### network 要素の構造 (表3)

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
| use_dhcp4 | オプション | boolean | true/false | DHCPv4を使用する指定 | `false` |
| use_slaac | オプション | boolean | true/false | SLAAC (IPv6自動設定) を使用する指定 | `true` |
| route_metric_ipv4 | オプション | integer | 0以上 | IPv4のルートメトリック値 | `100` |
| route_metric_ipv6 | オプション | integer | 0以上 | IPv6のルートメトリック値 | `100` |
| ignore_auto_ipv4_dns | オプション | boolean | true/false | 自動取得したIPv4 DNSを無視する指定 | `true` |
| ignore_auto_ipv6_dns | オプション | boolean | true/false | 自動取得したIPv6 DNSを無視する指定 | `true` |

### ネットワークロール (role) の説明

#### external_control_plane_network

外部管理ネットワークです。インターネットや組織外ネットワークへの接続に使用します。
このロールのネットワークに接続されたインターフェースが管理NIC (`mgmt_nic`) として優先されます。

#### private_control_plane_network

内部管理ネットワークです。外部管理ネットワークへ直接接続されないノード群の管理通信に使用します。
`external_control_plane_network` が存在しない場合, このロールのネットワーク接続IFが管理NIC (`mgmt_nic`) として選択されます。

#### data_plane_network

データプレーンネットワークです。Kubernetes ノード間通信やクラスタ内トラフィックで使用します。
このロールのネットワーク接続IFは `k8s_nic` 自動導出対象になります。

#### bgp_transport_network

FRR (Free Range Routing) ルータ間の BGP 交換用ネットワークです。データセンタ間 eBGP ネイバー自動導出で参照されます。

### name_servers_ipv4 要素 (表4)

| 型 | 値の範囲 | 説明 | 設定例 |
|----|---------|------|--------|
| string | IPv4アドレス | IPv4 DNSサーバーアドレス | `"8.8.8.8"` |

*配列として複数指定可能 (例: `["8.8.8.8", "8.8.4.4"]`)*

### name_servers_ipv6 要素 (表5)

| 型 | 値の範囲 | 説明 | 設定例 |
|----|---------|------|--------|
| string | IPv6アドレス | IPv6 DNSサーバーアドレス | `"2606:4700:4700::1111"` |

*配列として複数指定可能*

### datacenter 要素の構造 (表6)

| フィールド名 | 必須/オプション | 型 | 値の範囲 | 説明 | 設定例 |
|------------|----------------|----|---------|----|--------|
| name | 必須 | string | - | データセンター名 | `"DataCenter 1"` |
| asn | 必須 | integer | 1-4294967295 | このデータセンターのBGP AS番号 | `65011` |
| route_reflector | オプション | string | - | このデータセンターのルートリフレクタとなるノードID (name) | `"frr01"` |

### nodes 要素 (各ノード) の構造 (表8)

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

### interface 要素の構造 (表9)

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

### scalars 要素の構造 (表10)

ホスト固有のスカラー変数を格納するオブジェクトです。任意のキー:値ペアを定義できます。

**よく使用されるフィールド例:**

| フィールド名 | 型 | 説明 | 設定例 |
|------------|----|----|--------|
| frr_bgp_asn | integer | FRR BGP AS番号 | `65011` |
| frr_bgp_router_id | string | FRR BGPルーターID | `"192.168.40.49"` |
| k8s_ctrlplane_host | string | Kubernetesコントロールプレーンホスト名 | `"k8sctrlplane01.local"` |
| k8s_pod_ipv4_network_cidr | string | Pod用IPv4 CIDR | `"10.244.0.0/16"` |
| k8s_cilium_cm_cluster_id | integer | CiliumクラスターID | `1` |

*その他, ホスト固有の任意の変数を定義できます*

### services 要素の構造 (表11)

ホスト固有のサービス設定を格納するオブジェクトです。サービス名をキーとし, 各値は `config` サブキーを持ちます。

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
|------------|----------------|----|----|------|
| vm_params | オプション | object | XCP-ng 仮想マシン (VM) パラメータ設定 | [表11-A] |

### vm_params.config の構造 (表11-A)

XCP-ng で構築する VM の個別パラメータを定義します。`generate_terraform_tfvars` が参照します。

| フィールド名 | 必須/オプション | 型 | 値の範囲 | 説明 | 設定例 |
|------------|----------------|----|---------|----|--------|
| vm_group | オプション | string | - | VM グループ名の明示指定。未指定時は `globals.services.xcp_ng_environment.config.vm_group_map` からロールで自動決定 | `"devlinux"` |
| template_type | 必須 | string | `ubuntu`, `rhel` | 使用するOSテンプレート種別 | `"ubuntu"` |
| firmware | 必須 | string | `uefi`, `bios` | VM のファームウェア種別 | `"uefi"` |
| resource_profile | オプション | string | - | VM リソースプロファイル名 (グループ既定値を上書き) | `"medium"` |
| vcpus | オプション | integer | 1以上 | vCPU 数 (グループ既定値・グローバル既定値を上書き) | `4` |
| memory_mb | オプション | integer | 1以上 | メモリ容量 (MiB 単位, グループ既定値・グローバル既定値を上書き) | `4096` |
| disk_gb | オプション | integer | 1以上 | ディスク容量 (GiB 単位, グループ既定値・グローバル既定値を上書き) | `25` |

## 入力ファイルスキーマ: network_topology.schema.yaml

### スキーマメタ情報 (表S1)

| フィールド名 | 値 | 説明 |
|------------|----|----|
| $schema | `https://json-schema.org/draft/2020-12/schema` | JSON Schemaのバージョン |
| $id | `network_topology.schema.v2.yaml` | スキーマID |
| title | `network topology input schema (v2)` | スキーマのタイトル |
| description | (スキーマの説明) | ネットワークトポロジー定義のスキーマ |
| type | `object` | ルート要素の型 |

### スキーマプロパティ定義 (表S2)

| プロパティ名 | 必須 | 型 | 説明 | 詳細参照 |
|-------------|------|----|----|---------|
| version | Yes | integer | スキーマバージョン (minimum: 2) | - |
| globals | Yes | object | グローバル定義 | [表S3] |
| nodes | Yes | array | ノードのリスト | items: object |

### globals プロパティ定義 (表S3)

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

### network additionalProperties スキーマ (表S4)

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

## 出力ファイル形式: host_vars_structured.yaml

### トップレベル構造 (表O1)

| フィールド名 | 必須/オプション | 型 | 説明 | 参照 |
|------------|----------------|----|----|------|
| hosts | 必須 | array | ホスト情報のリスト | [表O2] |

### host 要素の構造 (表O2)

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

### scalars の一般的なフィールド (表O3)

| フィールド名 | 型 | 説明 | 設定例 |
|------------|----|----|--------|
| mgmt_nic | string | 管理用NIC名 | `"enp1s0"` |
| frr_bgp_asn | integer | FRR BGP AS番号 | `65001` |
| frr_bgp_router_id | string | BGPルーターID | `"192.168.255.1"` |
| k8s_cilium_cm_cluster_name | string | Kubernetesクラスター名 | `"cluster1"` |
| k8s_cilium_cm_cluster_id | integer | Kubernetesクラスター識別子 | `1` |

*その他, 動的に生成されるスカラー変数が含まれます*

### netif_list 要素の構造 (表O4)

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

### frr_neighbor 要素の構造 (表O5)

BGPネイバー情報の構造です。`frr_ebgp_neighbors`, `frr_ebgp_neighbors_v6`, `frr_ibgp_neighbors`, `frr_ibgp_neighbors_v6`の各配列に含まれる要素です。

| フィールド名 | 必須/オプション | 型 | 説明 | 設定例 |
|------------|----------------|----|----|--------|
| addr | 必須 | string | ネイバーのIPアドレス | `"192.168.255.2"` |
| asn | 必須 | integer | ネイバーのAS番号 | `65002` |
| desc | 必須 | string | ネイバーの説明 | `"AS Number: 65002 - router2"` |
