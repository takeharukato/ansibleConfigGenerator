# generate_network_topology_design_sheet.py

`generate_network_topology_design_sheet.py` は, YAML Ain't Markup Language (以下 YAML と略す) 形式の `network_topology.yaml` からレビュー用のパラメタデザインシート Comma-Separated Values (以下 CSV と略す) を生成するコマンドです。
`globals`, `roles`, `services`, `hosts` の 4 系統に分割した CSV を出力し, description の解決には `field_metadata.yaml` と `network_topology.schema.yaml` を利用します。

## 目次

- [generate\_network\_topology\_design\_sheet.py](#generate_network_topology_design_sheetpy)
  - [目次](#目次)
  - [SYNOPSIS](#synopsis)
  - [引数/オプション一覧](#引数オプション一覧)
  - [引数/オプション詳細](#引数オプション詳細)
    - [`--input`](#--input)
    - [`--output`](#--output)
    - [`--metadata`](#--metadata)
    - [`--schema-dir`](#--schema-dir)
  - [設定ファイル](#設定ファイル)
  - [実行例](#実行例)
    - [基本例](#基本例)
    - [入力, スキーマ, 出力ヒントを明示する例](#入力-スキーマ-出力ヒントを明示する例)
    - [スキーマ探索先を明示する例](#スキーマ探索先を明示する例)
  - [エラーメッセージと終了コード](#エラーメッセージと終了コード)
  - [付録](#付録)
    - [入力ファイル形式](#入力ファイル形式)
      - [`network_topology.yaml`](#network_topologyyaml)
      - [`field_metadata.yaml`](#field_metadatayaml)
      - [`network_topology.schema.yaml`](#network_topologyschemayaml)
    - [出力ファイル形式](#出力ファイル形式)
      - [globals / roles / services の列](#globals--roles--services-の列)
      - [hosts の列](#hosts-の列)

## SYNOPSIS

```plaintext
generate_network_topology_design_sheet.py [-h] [-i INPUT] [-o OUTPUT] [-m METADATA] [--schema-dir SCHEMA_DIR]
```

## 引数/オプション一覧

本コマンドは位置引数を持ちません。すべてオプションで指定します。

| ロングオプション | ショートオプション | オプションの意味 | 規定値 | 指定例 |
|---|---|---|---|---|
| `--help` | `-h` | ヘルプメッセージを表示して終了する | - | `-h` |
| `--input` | `-i` | 入力となるトポロジー YAML を指定する | `network_topology.yaml` | `-i network_topology.yaml` |
| `--output` | `-o` | 出力パスのヒントを指定します。ディレクトリまたはファイルパスを受け付けます | `network_topology.csv` | `-o .` |
| `--metadata` | `-m` | description フォールバックに使用するスキーマ YAML を指定する | `network_topology.schema.yaml` | `-m network_topology.schema.yaml` |
| `--schema-dir` | - | スキーマ/設定 YAML 探索先ディレクトリを最優先で指定する | `None` | `--schema-dir /path/to/schema` |

## 引数/オプション詳細

### `--input`

レビュー対象となる `network_topology.yaml` を指定します。未指定時はカレントディレクトリの `network_topology.yaml` を利用します。

### `--output`

出力先のヒントを指定します。ファイル名が与えられても, 実際の出力は入力ファイルのベース名とセクション名から導出される 4 ファイルになります。

### `--metadata`

description のフォールバック元となる `network_topology.schema.yaml` を指定します。

### `--schema-dir`

`field_metadata.yaml` やスキーマ YAML の探索先ディレクトリを最優先で指定します。

## 設定ファイル

本コマンドは以下を参照します。

- `network_topology.yaml`: 主入力
- `field_metadata.yaml`: `design_sheet_descriptions` による description 優先解決元
- `network_topology.schema.yaml`: description フォールバック元

description 解決順序は次のとおりです。

1. `field_metadata.yaml` の `design_sheet_descriptions`
2. `network_topology.schema.yaml` の `description`

`field_metadata.yaml` が入力ファイルと同じディレクトリにある場合は自動検出されます。探索先は `--schema-dir` と `schema_search_paths` の影響を受けます。

## 実行例

### 基本例

```shell
generate_network_topology_design_sheet.py
```

### 入力, スキーマ, 出力ヒントを明示する例

```shell
generate_network_topology_design_sheet.py \
  -i network_topology.yaml \
  -m network_topology.schema.yaml \
  -o .
```

### スキーマ探索先を明示する例

```shell
generate_network_topology_design_sheet.py \
  -i network_topology.yaml \
  --schema-dir /path/to/schema \
  -o output/
```

## エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|---|---|---|
| `0` | 正常終了 | 4 種類のパラメタデザインシート CSV 生成に成功した |
| `1` | エラー終了 | 入力ファイル不存在, YAML 解析失敗, 必須キー欠落など |

補足:

- description 未解決は警告であり, それだけでは終了コード 1 になりません。
- 必須トップレベルキー不足や YAML パース失敗はエラー終了になります。

## 付録

### 入力ファイル形式

#### `network_topology.yaml`

必須トップレベルキーは以下です。

| キー | 必須 | 型 | 説明 |
|---|---|---|---|
| `version` | 必須 | integer | スキーマバージョン |
| `globals` | 必須 | object | グローバル定義 |
| `nodes` | 必須 | array | ノード定義 |

#### `field_metadata.yaml`

`design_sheet_descriptions` セクションがある場合, 各 design sheet 行の説明文の優先解決元として使用します。

#### `network_topology.schema.yaml`

`description` のフォールバック解決元として使用します。

### 出力ファイル形式

出力は 4 つの独立した CSV ファイルであり, 入力ファイルのベース名にセクション名を連結して命名されます。

| ファイル名 | セクション | 列構成 |
|---|---|---|
| `{input_stem}-globals.csv` | globals 設定 | `item`, `parameter`, `description`, `value` |
| `{input_stem}-roles.csv` | role 設定 | `item`, `parameter`, `description`, `value` |
| `{input_stem}-services.csv` | service 設定 | `item`, `parameter`, `description`, `value` |
| `{input_stem}-hosts.csv` | ホスト別設定 | `parameter`, `description`, `{hostname_1}`, `{hostname_2}`, ... |

#### globals / roles / services の列

| 列名 | 説明 |
|---|---|
| `item` | 対象キーまたはグループ名 |
| `parameter` | 項目名または dot path |
| `description` | 解決した説明文 |
| `value` | 値 |

#### hosts の列

| 列名 | 説明 |
|---|---|
| `parameter` | 行種別とパラメータ名を `.` で連結した識別子 |
| `description` | 解決した説明文 |
| `{hostname}` | ホスト名ごとの値列 |
