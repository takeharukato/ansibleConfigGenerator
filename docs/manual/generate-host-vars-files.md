# generate_host_vars_files.py

`generate_host_vars_files.py` は, YAML Ain't Markup Language (以下 YAML と略す) 形式の `host_vars_structured.yaml` を入力として, ホストごとの Ansible 用 host_vars ファイルを生成するコマンドです。
`field_metadata.yaml` の説明を参照し, スカラーフィールドの直前へコメントを挿入して出力します。

## 目次

- [generate\_host\_vars\_files.py](#generate_host_vars_filespy)
  - [目次](#目次)
  - [SYNOPSIS](#synopsis)
  - [引数/オプション一覧](#引数オプション一覧)
    - [位置引数](#位置引数)
    - [オプション](#オプション)
  - [引数/オプション詳細](#引数オプション詳細)
    - [`output_dir`](#output_dir)
    - [`--input-structured`](#--input-structured)
    - [`--metadata`](#--metadata)
    - [`--schema-dir`](#--schema-dir)
    - [`--overwrite`](#--overwrite)
    - [`--validate-roundtrip`](#--validate-roundtrip)
  - [設定ファイル](#設定ファイル)
  - [実行例](#実行例)
    - [基本例](#基本例)
    - [入力とメタデータを明示する例](#入力とメタデータを明示する例)
    - [上書きを無効化する例](#上書きを無効化する例)
    - [ラウンドトリップ検証を有効化する例](#ラウンドトリップ検証を有効化する例)
  - [エラーメッセージと終了コード](#エラーメッセージと終了コード)
  - [付録](#付録)
    - [入力ファイル形式](#入力ファイル形式)
      - [`host_vars_structured.yaml`](#host_vars_structuredyaml)
      - [`field_metadata.yaml`](#field_metadatayaml)
    - [出力ファイル形式](#出力ファイル形式)
      - [ファイル名規則](#ファイル名規則)
      - [出力内容](#出力内容)
    - [コメント挿入規則](#コメント挿入規則)


## SYNOPSIS

```plaintext
generate_host_vars_files.py [-h] [-i INPUT_STRUCTURED] [-m METADATA]
                            [--schema-dir SCHEMA_DIR] [-w {true,false}]
                            [-v {true,false}] output_dir
```

## 引数/オプション一覧

### 位置引数

| ロングオプション | ショートオプション | オプションの意味 | 規定値 | 指定例 |
|---|---|---|---|---|
| - | - | 生成ファイルの保存先ディレクトリ (`output_dir`) | - | `host_vars.gen` |

### オプション

| ロングオプション | ショートオプション | オプションの意味 | 規定値 | 指定例 |
|---|---|---|---|---|
| `--help` | `-h` | ヘルプメッセージを表示して終了する | - | `-h` |
| `--input-structured` | `-i` | 入力となる構造化 host_vars YAML を指定する | `host_vars_structured.yaml` | `-i host_vars_structured.yaml` |
| `--metadata` | `-m` | フィールドメタデータ YAML を指定する | `field_metadata.yaml` | `-m field_metadata.yaml` |
| `--schema-dir` | - | `field_metadata.yaml` の探索先ディレクトリを最優先で指定する | `None` | `--schema-dir /path/to/schema` |
| `--overwrite` | `-w` | 既存ファイルを上書きするよう指定する | `true` | `-w false` |
| `--validate-roundtrip` | `-v` | 生成後に再読み込み検証を行うよう指定する | `false` | `-v true` |

## 引数/オプション詳細

### `output_dir`

生成した host_vars ファイル群の保存先ディレクトリを指定します。存在しない場合は作成されます。

### `--input-structured`

入力となる `host_vars_structured.yaml` を指定します。通常は `generate_host_vars_structured.py` の出力をそのまま利用します。

### `--metadata`

`field_metadata.yaml` を指定します。各スカラーフィールドの直前に挿入するコメント文の取得元として使用します。

### `--schema-dir`

`--metadata` が規定値のままの場合に, `field_metadata.yaml` の探索先ディレクトリを最優先で指定します。

### `--overwrite`

`true` の場合は既存ファイルを無条件に上書きします。`false` の場合は既存ファイルがあるホストをスキップします。

### `--validate-roundtrip`

`true` の場合, 生成したファイルを再読み込みして元の構造化データと比較します。差分が検出された場合は終了コード 1 で終了します。

## 設定ファイル

本コマンドは以下を参照します。

- `host_vars_structured.yaml`: 前段コマンドの中間生成物
- `field_metadata.yaml`: コメント文の取得元

`field_metadata.yaml` は `--metadata` で個別指定でき, 規定値使用時は `--schema-dir` や `schema_search_paths` の探索結果が適用されます。

## 実行例

### 基本例

```shell
generate_host_vars_files.py host_vars.gen
```

### 入力とメタデータを明示する例

```shell
generate_host_vars_files.py host_vars.gen \
  -i host_vars_structured.yaml \
  -m field_metadata.yaml
```

### 上書きを無効化する例

```shell
generate_host_vars_files.py host_vars.gen -w false
```

### ラウンドトリップ検証を有効化する例

```shell
generate_host_vars_files.py host_vars.gen -v true
```

## エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|---|---|---|
| `0` | 正常終了 | host_vars ファイル群の生成に成功した |
| `1` | エラー終了 | 入力読み込み失敗, 書き込み失敗, ラウンドトリップ検証失敗など |

主な失敗要因は以下の通りです:

- `host_vars_structured.yaml` が存在しない
- `field_metadata.yaml` を解決できない
- 出力ディレクトリを作成できない
- 再読み込み検証で不一致が検出される

## 付録

### 入力ファイル形式

#### `host_vars_structured.yaml`

トップレベルに `hosts` 配列を持ち, 各ホスト要素に `hostname`, `scalars`, `netif_list` などを含めます。

#### `field_metadata.yaml`

トップレベルに `fields` を持ち, 各フィールドの `description` をコメント文として利用します。

### 出力ファイル形式

#### ファイル名規則

| 規則 | 説明 | 例 |
|---|---|---|
| パス | `<output_dir>/<hostname>` | `host_vars.gen/server1.example.com` |
| 拡張子 | なし | - |

#### 出力内容

出力は YAML 形式であり, スカラーフィールドの直前に `field_metadata.yaml` の説明コメントが挿入されます。

### コメント挿入規則

| 規則 | 説明 |
|---|---|
| 挿入位置 | スカラーフィールドの直前行 |
| 形式 | `# <説明文>` |
| 折り返し | 80 文字超過時は複数行へ折り返す |
| メタデータ未定義 | コメントなし |
