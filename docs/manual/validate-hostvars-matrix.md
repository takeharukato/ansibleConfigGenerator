# validate_hostvars_matrix.py

`validate_hostvars_matrix.py` は, `generate_hostvars_matrix.py` が生成した Comma-Separated Values (以下 CSV と略す) の構造整合性を検証するコマンドです。
本コマンドは形式検証に特化しており, YAML Ain't Markup Language (以下 YAML と略す) 入力と整合する構造のみを確認し, 値そのものの意味的妥当性やソース値との厳密比較は行いません。

## 目次

- [validate\_hostvars\_matrix.py](#validate_hostvars_matrixpy)
  - [目次](#目次)
  - [SYNOPSIS](#synopsis)
  - [引数/オプション一覧](#引数オプション一覧)
  - [引数/オプション詳細](#引数オプション詳細)
    - [`--csv`](#--csv)
    - [`--metadata`](#--metadata)
    - [`--host-vars`](#--host-vars)
  - [設定ファイル](#設定ファイル)
  - [実行例](#実行例)
    - [基本例](#基本例)
    - [入力ファイルを明示する例](#入力ファイルを明示する例)
    - [パイプラインで利用する例](#パイプラインで利用する例)
  - [エラーメッセージと終了コード](#エラーメッセージと終了コード)
  - [付録](#付録)
    - [入力ファイル形式](#入力ファイル形式)
      - [`host_vars_scalars_matrix.csv`](#host_vars_scalars_matrixcsv)
      - [`field_metadata.yaml`](#field_metadatayaml)
      - [`host_vars_structured.yaml`](#host_vars_structuredyaml)

## SYNOPSIS

```plaintext
validate_hostvars_matrix.py [-h] [-c CSV] [-m METADATA] [-H HOST_VARS]
```

## 引数/オプション一覧

本コマンドは位置引数を持ちません。すべてオプションで指定します。

| ロングオプション | ショートオプション | オプションの意味 | 規定値 | 指定例 |
|---|---|---|---|---|
| `--help` | `-h` | ヘルプメッセージを表示して終了する | - | `-h` |
| `--csv` | `-c` | 検証対象の ノード設定パラメタデザインシート ファイルを指定する | `host_vars_scalars_matrix.csv` | `-c host_vars_scalars_matrix.csv` |
| `--metadata` | `-m` | フィールドメタデータ YAML を指定する | `field_metadata.yaml` | `-m field_metadata.yaml` |
| `--host-vars` | `-H` | 元の構造化 host_vars YAML を指定する | `host_vars_structured.yaml` | `-H host_vars_structured.yaml` |

## 引数/オプション詳細

### `--csv`

検証対象の ノード設定パラメタデザインシート を指定します。通常は `generate_hostvars_matrix.py` の出力を利用します。

### `--metadata`

`field_metadata.yaml` を指定します。期待されるフィールド集合, 型情報, `allowed_range` の検証基準として使用します。

### `--host-vars`

元の `host_vars_structured.yaml` を指定します。ホスト列集合と `netif` 展開期待件数の比較元として使用します。

## 設定ファイル

本コマンドは以下を入力として参照します。

- `host_vars_scalars_matrix.csv`: 検証対象の CSV
- `field_metadata.yaml`: フィールド定義
- `host_vars_structured.yaml`: 元の構造化 host_vars

`field_metadata.yaml` は, `generate_hostvars_matrix.py` の生成時に使用したバージョンと同じものを参照する必要があります。異なるバージョンのメタデータを使用すると, フィールド定義の不整合により以下が発生します。

- 期待されるフィールド集合が異なり, 列の過不足が検出される
- フィールドの型や許容範囲の定義が異なるため, 検証ロジックが不適切な結果を返す
- 結果として, 正当な ノード設定パラメタデザインシート でも検証失敗と判定される可能性がある

## 実行例

### 基本例

```shell
validate_hostvars_matrix.py
```

### 入力ファイルを明示する例

```shell
validate_hostvars_matrix.py \
  -c custom_matrix.csv \
  -m custom_meta.yaml \
  -H custom_hostvars.yaml
```

### パイプラインで利用する例

```shell
generate_hostvars_matrix.py -o matrix.csv && \
validate_hostvars_matrix.py -c matrix.csv
```

## エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|---|---|---|
| `0` | 正常終了 | CSV の構造検証に成功した |
| `1` | エラー終了 | ヘッダー不一致, 列数不一致, フィールド欠落などを検出した |

成功時の代表的な出力:

```plaintext
✓ CSV validation passed
```

失敗時の代表的な出力:

```plaintext
✗ CSV validation failed:
  - CSV header mismatch. Expected ['setting_name', 'type', 'allowed_range', 'description'], got [...]
```

## 付録

### 入力ファイル形式

#### `host_vars_scalars_matrix.csv`

先頭 4 列は以下の固定列です。

| 列名 | 説明 |
|---|---|
| `setting_name` | 設定名 |
| `type` | データ型 |
| `allowed_range` | 許容範囲 |
| `description` | 説明 |

5 列目以降は各ホスト列です。

#### `field_metadata.yaml`

トップレベルに `fields` を持ち, 期待されるフィールド集合の基準となります。

#### `host_vars_structured.yaml`

`hostname` を持つホスト集合と `netif_list` 展開件数の算出元となります。