# スキーマファイルリファレンスマニュアル

本ツール群は 4 種類のスキーマファイルを使用します。各ファイルの役割,構造,主要なキーについて説明します。

## 目次

- [スキーマファイルリファレンスマニュアル](#スキーマファイルリファレンスマニュアル)
  - [目次](#目次)
  - [スキーマファイル一覧](#スキーマファイル一覧)
  - [network\_topology.schema.yaml](#network_topologyschemayaml)
    - [トップレベル構造](#トップレベル構造)
    - [globals セクション](#globals-セクション)
    - [globals.networks の各エントリ](#globalsnetworks-の各エントリ)
    - [globals.datacenters の各エントリ](#globalsdatacenters-の各エントリ)
    - [nodes の各エントリ](#nodes-の各エントリ)
  - [host\_vars\_structured.schema.yaml](#host_vars_structuredschemayaml)
    - [トップレベル構造](#トップレベル構造-1)
    - [hosts の各エントリ (host オブジェクト)](#hosts-の各エントリ-host-オブジェクト)
    - [netif\_list の各エントリ (netif オブジェクト)](#netif_list-の各エントリ-netif-オブジェクト)
    - [frr\_ebgp\_neighbors 等の各エントリ (frr\_neighbor オブジェクト)](#frr_ebgp_neighbors-等の各エントリ-frr_neighbor-オブジェクト)
    - [k8s\_bgp オブジェクト](#k8s_bgp-オブジェクト)
  - [field\_metadata.schema.yaml](#field_metadataschemayaml)
    - [トップレベル構造](#トップレベル構造-2)
    - [fields の各エントリ (field\_entry オブジェクト)](#fields-の各エントリ-field_entry-オブジェクト)
    - [allowed\_range の種別](#allowed_range-の種別)
  - [関連資料](#関連資料)


## スキーマファイル一覧

| ファイル名 | 用途 |
|---|---|
| `network_topology.schema.yaml` | `network_topology.yaml` の入力値を検証する |
| `host_vars_structured.schema.yaml` | 中間出力 `host_vars_structured.yaml` の構造を定義する |
| `field_metadata.schema.yaml` | `field_metadata.yaml` 自体の構造を検証する |

上記ファイルの配置場所は `toolchain-overview.md` の「スキーマ探索ルール」を参照してください。

---

## network_topology.schema.yaml

`network_topology.yaml` の入力値を JavaScript Object Notation (以下 JSON と略す) Schema (Draft 2020-12) で検証します。`generate_host_vars_structured` 実行時に自動的に参照されます。

### トップレベル構造

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `version` | 必須 | integer (>= 2) | スキーマバージョン。現在は `2` を指定する |
| `globals` | 必須 | object | 全ノード共通の設定を記述するセクション |
| `nodes` | 必須 | array | ノード定義の配列。1 件以上必要 |

### globals セクション

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `networks` | 必須 | object | ネットワークセグメント定義。1 件以上必要 |
| `datacenters` | 必須 | object | データセンタ定義。1 件以上必要 |
| `services` | 任意 | object | 全ノード共通のサービス既定値 |
| `roles` | 任意 | object | ロール名とサービスリストのマッピング |
| `scalars` | 任意 | object | 全ノード共通のスカラー変数の既定値 |
| `proxy` | 任意 | object | プロキシ設定の既定値 |
| `kubernetes` | 任意 | object | Kubernetes グローバル設定 |
| `auto_meshed_ebgp_transport_enabled` | 任意 | boolean | データセンタ間 eBGP トランスポートを自動メッシュ生成する設定であることを示す |
| `generate_internal_network_list` | 任意 | boolean | DNS サーバ向け内部ネットワーク一覧を生成する設定であることを示す |
| `reserved_nic_pairs` | 任意 | array | 管理ネットワーク Network Interface Card (以下 NIC と略す) 予約ペア定義 |

### globals.networks の各エントリ

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `role` | 任意 | string | ネットワークの役割。許容値は下表参照 |
| `datacenter` | 任意 | string | 所属データセンタ識別子 (ID) |
| `cluster` | 任意 | string | 所属 Kubernetes クラスタ識別子 (ID) |
| `ipv4_cidr` | 任意 | string | IPv4 CIDR 表記アドレス |
| `ipv6_cidr` | 任意 | string | IPv6 CIDR 表記アドレス |
| `gateway4` | 任意 | string | デフォルト IPv4 ゲートウェイ |
| `gateway6` | 任意 | string | デフォルト IPv6 ゲートウェイ |
| `dns_search` | 任意 | string | DNS 検索ドメイン |
| `name_servers_ipv4` | 任意 | array | IPv4 DNS サーバリスト |
| `name_servers_ipv6` | 任意 | array | IPv6 DNS サーバリスト |
| `use_dhcp4` | 任意 | boolean | DHCP v4 を使用する指定 |
| `use_slaac` | 任意 | boolean | SLAAC (ステートレスアドレス自動設定) を使用する指定 |
| `ignore_auto_ipv4_dns` | 任意 | boolean | 自動取得 IPv4 DNS を無視する指定 |
| `ignore_auto_ipv6_dns` | 任意 | boolean | 自動取得 IPv6 DNS を無視する指定 |
| `route_metric_ipv4` | 任意 | integer | IPv4 ルートメトリック |
| `route_metric_ipv6` | 任意 | integer | IPv6 ルートメトリック |

`role` の許容値:

| 値 | 意味 |
|---|---|
| `external_control_plane_network` | 外部管理ネットワーク |
| `private_control_plane_network` | 内部管理ネットワーク |
| `data_plane_network` | データプレーンネットワーク |
| `bgp_transport_network` | Border Gateway Protocol (以下 BGP と略す) トランスポートネットワーク |

### globals.datacenters の各エントリ

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `name` | 必須 | string | データセンタ名 |
| `asn` | 必須 | integer (1..4294967295) | 自律システム (AS) 番号 |
| `route_reflector` | 任意 | string | ルートリフレクタノード識別子 |

### nodes の各エントリ

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `name` | 必須 | string | ノード識別子。英数字,`-`,`_` のみ使用可 |
| `hostname_fqdn` | 必須 | string | 完全修飾ドメイン名 (FQDN) 形式のホスト名 |
| `roles` | 必須 | array | 割り当てるロール名のリスト。1 件以上必要 |
| `interfaces` | 必須 | array | インターフェース定義のリスト |
| `datacenter` | 条件付き必須 | string | Kubernetes ノードには必須 |
| `cluster` | 条件付き必須 | string | Kubernetes ノードには必須 |
| `scalars` | 任意 | object | ノード固有のスカラー変数 |
| `services` | 任意 | object | ノードレベルのサービス設定 |

`roles` に `k8s_control_plane` を含む場合は `datacenter`, `cluster`, `scalars` (および `k8s_ctrlplane_endpoint`, `k8s_cilium_cm_cluster_name`, `k8s_cilium_cm_cluster_id`) が必須になります。

---

## host_vars_structured.schema.yaml

中間出力 YAML Ain't Markup Language (以下 YAML と略す) (`host_vars_structured.yaml`) の構造を JSON Schema (Draft 2020-12) で定義します。`generate_hostvars_matrix` および `generate_host_vars_files` の入力検証に使用されます。

### トップレベル構造

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `hosts` | 必須 | array | ホスト定義の配列。1 件以上必要 |

### hosts の各エントリ (host オブジェクト)

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `hostname` | 必須 | string | ホスト名 |
| `scalars` | 必須 | object | スカラー変数の辞書 |
| `netif_list` | 必須 | array | ネットワークインターフェース (NIC) 情報のリスト |
| `k8s_bgp` | 任意 | object | Kubernetes BGP コントロールプレーン設定 |
| `k8s_worker_frr` | 任意 | object | Kubernetes ワーカー Free Range Routing (以下 FRR と略す) 設定 |
| `frr_ebgp_neighbors` | 任意 | array | FRR eBGP ネイバーリスト (IPv4) |
| `frr_ebgp_neighbors_v6` | 任意 | array | FRR eBGP ネイバーリスト (IPv6) |
| `frr_ibgp_neighbors` | 任意 | array | FRR iBGP ネイバーリスト (IPv4) |
| `frr_ibgp_neighbors_v6` | 任意 | array | FRR iBGP ネイバーリスト (IPv6) |
| `frr_networks_v4` | 任意 | array of string | FRR 広報対象ネットワーク (IPv4 CIDR) |
| `frr_networks_v6` | 任意 | array of string | FRR 広報対象ネットワーク (IPv6 CIDR) |
| `vcinstances_clusterversions` | 任意 | array | 仮想クラスタバージョン定義リスト |
| `vcinstances_virtualclusters` | 任意 | array | 仮想クラスタインスタンス定義リスト |

### netif_list の各エントリ (netif オブジェクト)

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `netif` | 必須 | string | NIC 名 |
| `static_ipv4_addr` | 任意 | string | 静的 IPv4 アドレス |
| `static_ipv6_addr` | 任意 | string | 静的 IPv6 アドレス |
| `network_ipv4_prefix_len` | 任意 | integer | IPv4 プレフィックス長 |
| `network_ipv6_prefix_len` | 任意 | integer | IPv6 プレフィックス長 |
| `gateway4` | 任意 | string | IPv4 デフォルトゲートウェイ |
| `gateway6` | 任意 | string | IPv6 デフォルトゲートウェイ |
| `dns_search` | 任意 | string | DNS 検索ドメイン |
| `name_server_ipv4_1` | 任意 | string | DNS サーバ 1 (IPv4) |
| `name_server_ipv4_2` | 任意 | string | DNS サーバ 2 (IPv4) |
| `name_server_ipv6_1` | 任意 | string | DNS サーバ 1 (IPv6) |
| `name_server_ipv6_2` | 任意 | string | DNS サーバ 2 (IPv6) |
| `ignore_auto_ipv4_dns` | 任意 | boolean | 自動取得 IPv4 DNS を無視する指定 |
| `ignore_auto_ipv6_dns` | 任意 | boolean | 自動取得 IPv6 DNS を無視する指定 |
| `mac` | 任意 | string | MAC アドレス |
| `route_metric_ipv4` | 任意 | integer | IPv4 ルートメトリック |
| `route_metric_ipv6` | 任意 | integer | IPv6 ルートメトリック |

### frr_ebgp_neighbors 等の各エントリ (frr_neighbor オブジェクト)

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `addr` | 必須 | string | ネイバー IP アドレス |
| `asn` | 必須 | integer | ネイバー AS 番号 |
| `desc` | 必須 | string | ネイバーの説明文 |

### k8s_bgp オブジェクト

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `enabled` | 必須 | boolean | BGP 有効化フラグ |
| `node_name` | 必須 | string | ノード名 |
| `local_asn` | 必須 | integer | ローカル AS 番号 |
| `kubeconfig` | 必須 | string | kubeconfig ファイルパス |
| `export_pod_cidr` | 必須 | boolean | Pod CIDR を広報する設定であることを示す |
| `advertise_services` | 必須 | boolean | Service を広報する設定であることを示す |
| `address_families` | 必須 | array of string | アドレスファミリーリスト |
| `neighbors` | 必須 | array | BGP ネイバー定義の配列 |

`neighbors` の各エントリ:

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `peer_address` | 必須 | string | ネイバー IP アドレス |
| `peer_asn` | 必須 | integer | ネイバー AS 番号 |
| `peer_port` | 必須 | integer | ネイバーポート番号 |
| `hold_time_seconds` | 必須 | integer | ホールドタイム (秒) |
| `connect_retry_seconds` | 必須 | integer | 接続リトライ間隔 (秒) |

---

## field_metadata.schema.yaml

`field_metadata.yaml` 自体の構造を JSON Schema (Draft 2020-12) で検証します。`generate_hostvars_matrix` の実行時に `field_metadata.yaml` の妥当性確認に使用されます。

### トップレベル構造

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `version` | 必須 | integer (>= 1) | スキーマバージョン。現在は `1` を指定する |
| `description` | 任意 | string | このメタデータファイルの説明文 |
| `fields` | 必須 | object | スカラー変数名をキーとするフィールド定義辞書 |

### fields の各エントリ (field_entry オブジェクト)

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `type` | 必須 | string | 変数の型。許容値は下表参照 |
| `description` | 必須 | string | Comma-Separated Values (以下 CSV と略す) とコメントに出力する説明文 |
| `category` | 必須 | string | ノード設定パラメタデザインシート での分類グループ。許容値は下表参照 |
| `allowed_range` | 任意 | object | 値の制約。`allowed_values` と同時使用不可 |
| `allowed_values` | 任意 | array | 許容する値の列挙リスト |
| `examples` | 任意 | array | 値の例 |
| `notes` | 任意 | string | 注記 |

`type` の許容値:

| 値 | 意味 |
|---|---|
| `string` | 文字列 |
| `integer` | 整数 |
| `number` | 数値 (小数含む) |
| `boolean` | 真偽値 |
| `cidr` | CIDR 表記アドレス |
| `ip` | IP アドレス |
| `hostname` | ホスト名または FQDN |
| `interface` | NIC 名 |

`category` の許容値:

| 値 | 意味 |
|---|---|
| `network_interface` | ネットワークインターフェース関連 |
| `routing_bgp` | BGP ルーティング関連 |
| `k8s_network` | Kubernetes ネットワーク関連 |
| `k8s_control_plane` | Kubernetes コントロールプレーン関連 |
| `k8s_features` | Kubernetes 追加機能関連 |
| `storage` | ストレージ関連 |
| `infrastructure` | インフラ全般 |

### allowed_range の種別

`allowed_range` には 4 種類があります。`kind` キーで種別を指定します。

**numeric (数値範囲)**

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `kind` | 必須 | string (`numeric`) | 種別識別子 |
| `min` | 必須 | number | 最小値 |
| `max` | 必須 | number | 最大値 |

```yaml
allowed_range:
  kind: numeric
  min: 1
  max: 65535
```

**enum (列挙)**

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `kind` | 必須 | string (`enum`) | 種別識別子 |
| `values` | 必須 | array of string | 許容する値のリスト |

```yaml
allowed_range:
  kind: enum
  values:
    - ipv4_only
    - ipv6_only
    - dual_stack
```

**pattern (正規表現)**

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `kind` | 必須 | string (`pattern`) | 種別識別子 |
| `regex` | 必須 | string | Python 正規表現パターン文字列 |

```yaml
allowed_range:
  kind: pattern
  regex: '^[0-9]{1,3}(\.[0-9]{1,3}){3}$'
```

**semantic (意味的制約)**

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `kind` | 必須 | string (`semantic`) | 種別識別子 |
| `name` | 必須 | string | 意味的制約の種別名。許容値は下表参照 |

`name` の許容値:

| 値 | 意味 |
|---|---|
| `fqdn` | 完全修飾ドメイン名 (FQDN) |
| `ifname` | NIC 名 (`eth0`, `ens3` など) |
| `ip_or_fqdn` | IP アドレスまたは FQDN |
| `asn` | 自律システム (AS) 番号 |
| `cidr_ipv4` | IPv4 CIDR 表記 |
| `cidr_ipv6` | IPv6 CIDR 表記 |

```yaml
allowed_range:
  kind: semantic
  name: fqdn
```

---


## 関連資料

- [ロール作成者向けガイド](ansible-role-author-guide.md)
- [変換ルール設定リファレンスマニュアル](convert-rule-config-reference.md)
- [フィールドメタデータリファレンスマニュアル](field-metadata-reference.md)
- [ツールチェイン概要](toolchain-overview.md)
