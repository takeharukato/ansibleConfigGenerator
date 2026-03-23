# generate_hostvars_matrix

`generate_hostvars_matrix` は, `host_vars_structured.yaml` と `field_metadata.yaml` を入力として, ホスト横断のパラメタシート Comma-Separated Values (以下 CSV と略す) を生成するコマンドです。
設定値確認, レビュー, 後段の `validate_hostvars_matrix` による構造検証で利用する一覧表を出力します。入力は YAML Ain't Markup Language (以下 YAML と略す) で記述され, 一部の値は JavaScript Object Notation (以下 JSON と略す) 形式で直列化されます。Network Interface Card (以下 NIC と略す) の展開行も含まれます。

## 目次

- [generate\_hostvars\_matrix.py](#generate_hostvars_matrixpy)
  - [目次](#目次)
  - [SYNOPSIS](#synopsis)
  - [引数/オプション一覧](#引数オプション一覧)
  - [引数/オプション詳細](#引数オプション詳細)
    - [`--host-vars`](#--host-vars)
    - [`--metadata`](#--metadata)
    - [`--output`](#--output)
    - [`--schema-dir`](#--schema-dir)
  - [設定ファイル](#設定ファイル)
  - [実行例](#実行例)
    - [標準出力へ出力する例](#標準出力へ出力する例)
    - [ファイルへ出力する例](#ファイルへ出力する例)
    - [入力ファイルを明示する例](#入力ファイルを明示する例)
    - [メタデータ探索先を明示する例](#メタデータ探索先を明示する例)
  - [エラーメッセージと終了コード](#エラーメッセージと終了コード)
  - [付録](#付録)
    - [入力ファイル形式](#入力ファイル形式)
      - [`host_vars_structured.yaml`](#host_vars_structuredyaml)
      - [`field_metadata.yaml`](#field_metadatayaml)
    - [出力ファイル形式](#出力ファイル形式)
      - [ノード設定パラメタデザインシート 構造](#ノード設定パラメタデザインシート-構造)
      - [値の直列化規则](#値の直列化規则)


## SYNOPSIS

```plaintext
generate_hostvars_matrix [-h] [-H HOST_VARS] [-m METADATA] [-o OUTPUT] [--schema-dir SCHEMA_DIR]
```

## 引数/オプション一覧

本コマンドは位置引数を持ちません。すべてオプションで指定します。

| ロングオプション | ショートオプション | オプションの意味 | 規定値 | 指定例 |
|---|---|---|---|---|
| `--help` | `-h` | ヘルプメッセージを表示して終了する | - | `-h` |
| `--host-vars` | `-H` | 入力となる構造化 host_vars YAML を指定する | `host_vars_structured.yaml` | `-H host_vars_structured.yaml` |
| `--metadata` | `-m` | フィールドメタデータ YAML を指定する | `field_metadata.yaml` | `-m field_metadata.yaml` |
| `--output` | `-o` | 出力 ノード設定パラメタデザインシート ファイルパスを指定します。未指定時は標準出力へ出力します | 標準出力 | `-o host_vars_scalars_matrix.csv` |
| `--schema-dir` | - | `field_metadata.yaml` の探索先ディレクトリを最優先で指定する | `None` | `--schema-dir /path/to/schema` |

## 引数/オプション詳細

### `--host-vars`

`generate_host_vars_structured` の出力である `host_vars_structured.yaml` を指定します。ホスト一覧, スカラー値, `netif_list` 展開行の生成元として使用します。

### `--metadata`

`field_metadata.yaml` を指定します。各行の `type`, `allowed_range`, `description` の元情報として使用します。

### `--output`

未指定時は標準出力に ノード設定パラメタデザインシート を出力します。ファイル保存が必要な場合は `-o` で保存先を指定します。

### `--schema-dir`

`--metadata` が規定値のままの場合に, `field_metadata.yaml` の探索先ディレクトリを最優先で指定します。

## 設定ファイル

本コマンドは直接の設定ファイルとして `field_metadata.yaml` を参照し, 入力データとして `host_vars_structured.yaml` を使用します。

- `host_vars_structured.yaml`: 前段の `generate_host_vars_structured` の生成物
- `field_metadata.yaml`: フィールドの型, 説明, 許容範囲の定義

`field_metadata.yaml` は `--metadata` で個別指定できるほか, 規定値利用時は `--schema-dir` や `schema_search_paths` の探索結果が適用されます。

## 実行例

### 標準出力へ出力する例

```shell
generate_hostvars_matrix
```

### ファイルへ出力する例

```shell
generate_hostvars_matrix -o host_vars_scalars_matrix.csv
```

### 入力ファイルを明示する例

```shell
generate_hostvars_matrix \
  -H custom_host_vars_structured.yaml \
  -m custom_field_metadata.yaml \
  -o out.csv
```

### メタデータ探索先を明示する例

```shell
generate_hostvars_matrix \
  --schema-dir /path/to/schema \
  -H host_vars_structured.yaml \
  -o host_vars_scalars_matrix.csv
```

## エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|---|---|---|
| `0` | 正常終了 | ノード設定パラメタデザインシート の生成に成功した |
| `1` | エラー終了 | 入力ファイル読み込み失敗, YAML 解析失敗, ノード設定パラメタデザインシート 出力失敗など |

主な失敗要因は以下の通りです:

- `host_vars_structured.yaml` が存在しない
- `field_metadata.yaml` を解決できない
- YAML 構文が不正である
- 出力先へ書き込めない

## 付録

### 入力ファイル形式

#### `host_vars_structured.yaml`

`generate_host_vars_structured` の生成物であり, 少なくとも `hosts` 配列を持ちます。

| フィールド名 | 型 | 説明 |
|---|---|---|
| `hostname` | string | ホスト名 |
| `scalars` | object | スカラー変数 |
| `netif_list` | array | NIC 情報 |

#### `field_metadata.yaml`

トップレベルに `fields` を持ち, 各フィールドの型や説明を定義します。

| フィールド名 | 必須 | 型 | 説明 |
|---|---|---|---|
| `type` | 必須 | string | 項目の型 |
| `description` | 必須 | string | 項目説明 |
| `category` | 必須 | string | ソート用カテゴリ |
| `allowed_values` | 任意 | array | 許可値一覧 |

### 出力ファイル形式

出力 ノード設定パラメタデザインシート は固定 4 列とホスト列から成るCSVファイルです。

#### ノード設定パラメタデザインシート 構造

| 列位置 | 列名 | 説明 |
|---|---|---|
| 1 | `setting_name` | 設定名 |
| 2 | `type` | データ型 |
| 3 | `allowed_range` | 許容範囲の直列化結果 |
| 4 | `description` | 項目説明 |
| 5 以降 | 各ホスト名 | ホストごとの値 |

#### 値の直列化規则

- `None` は空文字列
- `bool` は `true` / `false`
- `list` は `;` 連結
- `dict` は JSON コンパクト文字列

`netif_list` は `netif_list[{IF名}].{sub_field}` の行として展開されます。
