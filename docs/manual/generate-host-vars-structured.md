# generate_host_vars_structured

`generate_host_vars_structured` は, YAML Ain't Markup Language (以下 YAML と略す) 形式の `network_topology.yaml` を入力として, Ansible パスの中間生成物である `host_vars_structured.yaml` を生成するコマンドです。
ネットワーク定義, ノード定義, サービス定義, Border Gateway Protocol (以下 BGP と略す) 関連情報を統合し, 後段の `generate_hostvars_matrix` と `generate_host_vars_files` が利用する共通形式へ正規化します。Free Range Routing (以下 FRR と略す) 関連情報と Network Interface Card (以下 NIC と略す) 情報を扱い, Command Line Interface (以下 CLI と略す) オプションで探索先を切り替えられます。

## 目次

- [generate\_host\_vars\_structured.py](#generate_host_vars_structuredpy)
  - [目次](#目次)
  - [SYNOPSIS](#synopsis)
  - [引数/オプション一覧](#引数オプション一覧)
  - [引数/オプション詳細](#引数オプション詳細)
    - [`--input`](#--input)
    - [`--output`](#--output)
    - [`--schema-dir`](#--schema-dir)
  - [設定ファイル](#設定ファイル)
  - [実行例](#実行例)
    - [基本例](#基本例)
    - [スキーマ探索先を明示する例](#スキーマ探索先を明示する例)
  - [エラーメッセージと終了コード](#エラーメッセージと終了コード)
  - [付録](#付録)
    - [入力ファイル形式](#入力ファイル形式)
      - [必須トップレベルキー](#必須トップレベルキー)
      - [ノード情報の主要項目](#ノード情報の主要項目)
    - [出力ファイル形式](#出力ファイル形式)
      - [標準構造](#標準構造)
      - [各ホスト要素の主要項目](#各ホスト要素の主要項目)


## SYNOPSIS

```plaintext
generate_host_vars_structured [-h] [-i INPUT] [-o OUTPUT] [--schema-dir SCHEMA_DIR]
```

## 引数/オプション一覧

本コマンドは位置引数を持ちません。すべてオプションで指定します。

| ロングオプション | ショートオプション | オプションの意味 | 規定値 | 指定例 |
|---|---|---|---|---|
| `--help` | `-h` | ヘルプメッセージを表示して終了する | - | `-h` |
| `--input` | `-i` | 入力となるネットワークトポロジー YAML ファイルを指定する | `network_topology.yaml` | `-i network_topology.yaml` |
| `--output` | `-o` | 出力する構造化 host_vars YAML ファイルを指定する | `host_vars_structured.yaml` | `-o host_vars_structured.yaml` |
| `--schema-dir` | - | スキーマ/設定 YAML 探索先ディレクトリを最優先で指定する | `None` | `--schema-dir /path/to/schema` |

## 引数/オプション詳細

### `--input`

入力となる `network_topology.yaml` を指定します。未指定時はカレントディレクトリ上の `network_topology.yaml` を参照します。

### `--output`

生成結果を `host_vars_structured.yaml` 形式で書き出す出力先を指定します。未指定時は `host_vars_structured.yaml` を生成します。

### `--schema-dir`

`network_topology.schema.yaml` や `convert-rule-config.yaml` など, 実行時に探索されるスキーマ/設定 YAML の探索先を上書きします。
CLI で指定したディレクトリは, ユーザー設定やシステム設定より優先して参照されます。

## 設定ファイル

本コマンドは直接の入力ファイルとして `network_topology.yaml` を利用し, 補助的に以下のスキーマ/設定ファイルを参照します。

- `network_topology.schema.yaml`
- `convert-rule-config.yaml`

これらの探索には `--schema-dir` または `schema_search_paths` の設定が影響します。探索順の詳細は [toolchain-overview.md](toolchain-overview.md) を参照してください。

本コマンドの出力 `host_vars_structured.yaml` は, 後段の `generate_hostvars_matrix`, `generate_host_vars_files`, `validate_hostvars_matrix` の入力になります。

## 実行例

### 基本例

```shell
generate_host_vars_structured -i network_topology.yaml -o host_vars_structured.yaml
```

### スキーマ探索先を明示する例

```shell
generate_host_vars_structured \
  -i network_topology.yaml \
  -o host_vars_structured.yaml \
  --schema-dir /path/to/schema
```

## エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|---|---|---|
| `0` | 正常終了 | `host_vars_structured.yaml` の生成に成功した |
| `1` | エラー終了 | 入力ファイル読み込み失敗, YAML 解析失敗, バリデーション失敗など |

主な失敗要因は以下の通りです:

- `network_topology.yaml` が存在しない
- YAML 構文が不正である
- 必須フィールドや型がスキーマに合致しない
- 関連するスキーマ/設定ファイルを解決できない

## 付録

### 入力ファイル形式

入力は `network_topology.yaml` であり, トップレベルには少なくとも以下を持ちます。

#### 必須トップレベルキー

| フィールド名 | 必須 | 型 | 説明 |
|---|---|---|---|
| `version` | 必須 | integer | スキーマバージョン |
| `globals` | 必須 | object | ネットワーク, データセンター, サービス, 既定値定義 |
| `nodes` | 必須 | array | ノード一覧 |

グローバル設定（`globals`）の主要項目:

| フィールド名 | 必須 | 型 | 説明 |
|---|---|---|---|
| `networks` | 必須 | object | ネットワーク定義辞書 |
| `datacenters` | 必須 | object | データセンター定義辞書 |
| `roles` | 任意 | object | ロールとサービスの対応 |
| `services` | 任意 | object | サービス既定値 |
| `scalars` | 任意 | object | 全ホスト共通の既定スカラー |
| `reserved_nic_pairs` | 任意 | array | 予約 NIC ペア |

#### ノード情報の主要項目

| フィールド名 | 必須 | 型 | 説明 |
|---|---|---|---|
| `name` | 必須 | string | ノード識別子 |
| `hostname_fqdn` | 必須 | string | 出力ホスト名 |
| `roles` | 必須 | array[string] | ノードロール一覧 |
| `interfaces` | 必須 | array | NIC 一覧 |
| `scalars` | 任意 | object | ホスト固有スカラー |
| `services` | 任意 | object | ホスト固有サービス設定 |

### 出力ファイル形式

出力は `host_vars_structured.yaml` であり, トップレベルに `hosts` 配列を持ちます。

#### 標準構造

| フィールド名 | 必須 | 型 | 説明 |
|---|---|---|---|
| `hosts` | 必須 | array | ホスト情報の配列 |

#### 各ホスト要素の主要項目

| フィールド名 | 必須 | 型 | 説明 |
|---|---|---|---|
| `hostname` | 必須 | string | ホスト名 |
| `scalars` | 必須 | object | スカラー変数群 |
| `netif_list` | 必須 | array | NIC 情報一覧 |
| `k8s_bgp` | 任意 | object | Kubernetes BGP 設定 |
| `k8s_worker_frr` | 任意 | object | Worker FRR 設定 |
| `frr_ebgp_neighbors` | 任意 | array | eBGP ネイバー一覧 |
| `frr_ibgp_neighbors` | 任意 | array | iBGP ネイバー一覧 |
