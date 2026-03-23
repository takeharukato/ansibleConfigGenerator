# generate_terraform_tfvars.py

`generate_terraform_tfvars.py` は, YAML Ain't Markup Language (以下 YAML と略す) 形式の `network_topology.yaml` を入力として, Xen Cloud Platform next generation (以下 XCP-ng と略す) 向けの `terraform.tfvars` を生成するコマンドです。
Ansible パスとは独立して動作し, `globals.roles.terraform_orchestration` を持つノードを対象に, Virtual Machine (以下 VM と略す) 定義とネットワーク定義を HashiCorp Configuration Language (以下 HCL と略す) 形式へ変換します。

## 目次

- [generate\_terraform\_tfvars.py](#generate_terraform_tfvarspy)
  - [目次](#目次)
  - [SYNOPSIS](#synopsis)
  - [引数/オプション一覧](#引数オプション一覧)
  - [引数/オプション詳細](#引数オプション詳細)
    - [`--topology`](#--topology)
    - [`--output`](#--output)
    - [`--dry-run`](#--dry-run)
    - [`--strict`](#--strict)
  - [設定ファイル](#設定ファイル)
  - [実行例](#実行例)
    - [基本例](#基本例)
    - [入力と出力を明示する例](#入力と出力を明示する例)
    - [生成内容だけ確認する例](#生成内容だけ確認する例)
    - [警告をエラー扱いにする例](#警告をエラー扱いにする例)
  - [エラーメッセージと終了コード](#エラーメッセージと終了コード)
  - [付録](#付録)
    - [入力ファイル形式](#入力ファイル形式)
      - [`globals.roles`](#globalsroles)
      - [`globals.services.xcp_ng_environment.config`](#globalsservicesxcp_ng_environmentconfig)
      - [`nodes[*].services.vm_params.config`](#nodesservicesvm_paramsconfig)
    - [出力ファイル形式](#出力ファイル形式)
      - [トップレベル変数](#トップレベル変数)


## SYNOPSIS

```plaintext
generate_terraform_tfvars.py [-h] [-t TOPOLOGY] [-o OUTPUT] [-n] [-s]
```

## 引数/オプション一覧

本コマンドは位置引数を持ちません。すべてオプションで指定します。

| ロングオプション | ショートオプション | オプションの意味 | 規定値 | 指定例 |
|---|---|---|---|---|
| `--help` | `-h` | ヘルプメッセージを表示して終了する | - | `-h` |
| `--topology` | `-t` | 入力となるネットワークトポロジー YAML を指定する | `network_topology.yaml` | `-t network_topology.yaml` |
| `--output` | `-o` | 出力する `terraform.tfvars` のパスを指定する | `terraform.tfvars` | `-o terraform.tfvars` |
| `--dry-run` | `-n` | ファイルを書き込まず, 生成内容を標準出力へ表示する | `false` | `-n` |
| `--strict` | `-s` | 警告をエラーとして扱う | `false` | `-s` |

## 引数/オプション詳細

### `--topology`

入力となる `network_topology.yaml` を指定します。未指定時はカレントディレクトリの `network_topology.yaml` を利用します。

### `--output`

生成する Terraform 変数ファイルの出力先を指定します。未指定時は `terraform.tfvars` を出力します。

### `--dry-run`

生成結果をファイルへ書き込まず, 標準出力へ出力します。内容確認や Continuous Integration (以下 CI と略す) 上の差分確認に向きます。

### `--strict`

警告をエラーとして扱います。たとえば `terraform_orchestration` ロールを持つノードが見つからない場合, 通常は警告だけで続行しますが, `--strict` 指定時は終了コード 1 を返します。

## 設定ファイル

本コマンドは直接の入力として `network_topology.yaml` を使用し, その中の以下の設定に依存します。

- `globals.roles.terraform_orchestration`
- `globals.services.xcp_ng_environment.config`
- `nodes[*].services.vm_params.config`

主に必要となる設定は, XCP-ng 接続情報, テンプレート名, ネットワークキー変換, VM グループ完全形です。
`xoa_url` や `xoa_username` は Xen Orchestra Appliance (以下 XOA と略す) 接続で使う値であり, API は Application Programming Interface (以下 API と略す), TLS は Transport Layer Security (以下 TLS と略す) を意味します。
`xoa_password` は `terraform.tfvars` へは出力されず, Terraform 実行時に環境変数 `TF_VAR_xoa_password` で渡す前提です。

## 実行例

### 基本例

```shell
generate_terraform_tfvars.py
```

### 入力と出力を明示する例

```shell
generate_terraform_tfvars.py \
  -t network_topology.yaml \
  -o terraform.tfvars
```

### 生成内容だけ確認する例

```shell
generate_terraform_tfvars.py -t network_topology.yaml -n
```

### 警告をエラー扱いにする例

```shell
generate_terraform_tfvars.py -t network_topology.yaml -o terraform.tfvars -s
```

## エラーメッセージと終了コード

| 終了コード | 状態 | 説明 |
|---|---|---|
| `0` | 正常終了 | `terraform.tfvars` の生成に成功した |
| `1` | エラー終了 | 入力読み込み失敗, 必須キー欠落, グループ解決失敗など |

主な失敗要因は以下の通りです:

- `network_topology.yaml` が存在しない
- `globals.services.xcp_ng_environment.config` に必須キーが足りない
- VM グループをロールや `vm_params` から解決できない
- `network_key_map` に未登録のネットワークをノードが参照している

## 付録

### 入力ファイル形式

入力は `network_topology.yaml` であり, Terraform 生成では特に以下を参照します。

#### `globals.roles`

| キー | 型 | 説明 |
|---|---|---|
| `terraform_orchestration` | array[string] | Terraform 対象ロール |

#### `globals.services.xcp_ng_environment.config`

| フィールド名 | 必須 | 型 | 説明 |
|---|---|---|---|
| `xoa_url` | 必須 | string | XOA API エンドポイント |
| `xoa_username` | 必須 | string | XOA ログインユーザー |
| `xoa_insecure` | 任意 | boolean | TLS 検証スキップ指定 |
| `xcpng_pool_name` | 必須 | string | XCP-ng プール名 |
| `xcpng_sr_name` | 必須 | string | ストレージリポジトリ名 |
| `xcpng_template_ubuntu` | 必須 | string | Ubuntu テンプレート名 |
| `xcpng_template_rhel` | 必須 | string | RHEL テンプレート名 |
| `network_key_map` | 必須 | object | topology ネットワーク名から Terraform ネットワークキーへの変換 |
| `network_names` | 必須 | object | Terraform ネットワークキーの表示名 |
| `vm_group_map` | 必須 | object | ロールから VM グループ名への変換 |
| `vm_group_defaults` | 必須 | object | VM グループ既定値 |

#### `nodes[*].services.vm_params.config`

| フィールド名 | 必須 | 型 | 説明 |
|---|---|---|---|
| `vm_group` | 任意 | string | VM グループの明示指定 |
| `template_type` | 必須 | string | OS テンプレート種別 |
| `firmware` | 必須 | string | ファームウェア種別 |
| `resource_profile` | 任意 | string | リソースプロファイル |
| `vcpus` | 任意 | integer | vCPU 数 |
| `memory_mb` | 任意 | integer | メモリ容量 |
| `disk_gb` | 任意 | integer | ディスク容量 |

### 出力ファイル形式

出力は HCL 形式の `terraform.tfvars` であり, 主要なトップレベル変数は以下です。

#### トップレベル変数

| 変数名 | 型 | 説明 |
|---|---|---|
| `xoa_url` | string | XOA API エンドポイント |
| `xoa_username` | string | XOA ユーザー名 |
| `xoa_insecure` | bool | TLS 検証スキップ |
| `xcpng_pool_name` | string | XCP-ng プール名 |
| `xcpng_sr_name` | string | ストレージリポジトリ名 |
| `xcpng_template_ubuntu` | string | Ubuntu テンプレート名 |
| `xcpng_template_rhel` | string | RHEL テンプレート名 |
| `network_names` | map(string) | ネットワーク表示名マップ |
| `network_roles` | map(list(string)) | ネットワーク役割マップ |
| `network_options` | map(any) | 追加ネットワークオプション |
| `vm_group_defaults` | map(object) | VM グループ別既定値 |
| `vm_groups` | map(map(object)) | グループ別 VM 定義 |

`vm_groups` は, グループ名ごとに VM 名と属性, さらに `networks` 配列を持つ構造で出力されます。
