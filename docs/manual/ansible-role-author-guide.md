# ロール作成者向けガイド: 変数・サービス・ロールの追加

本ガイドでは, [ansible-linux-setup](https://github.com/takeharukato/ansible-linux-setup) 向けの Ansible ロールを作成した際に,
作成したロールの各種設定値を出力する機能を追加する作業を実施するための手順やガイドラインを提示します。

## 目次

- [ロール作成者向けガイド: 変数・サービス・ロールの追加](#ロール作成者向けガイド-変数サービスロールの追加)
  - [目次](#目次)
  - [対象読者と前提知識](#対象読者と前提知識)
  - [本ツールで扱う変数モデル](#本ツールで扱う変数モデル)
  - [変更時に見るべき主要ファイル](#変更時に見るべき主要ファイル)
  - [スカラー変数を追加する作業](#スカラー変数を追加する作業)
    - [作業フロー](#作業フロー)
    - [手順 1: field\_metadata.yaml に追記する](#手順-1-field_metadatayaml-に追記する)
    - [手順 3: network\_topology.yaml に値を記述する](#手順-3-network_topologyyaml-に値を記述する)
    - [確認](#確認)
  - [リスト変数を追加する作業](#リスト変数を追加する作業)
    - [作業フロー](#作業フロー-1)
    - [手順 1: host\_vars\_structured.schema.yaml に追記する](#手順-1-host_vars_structuredschemayaml-に追記する)
    - [手順 3: 生成ロジックを追加する](#手順-3-生成ロジックを追加する)
  - [辞書型ノード設定変数を追加する作業](#辞書型ノード設定変数を追加する作業)
    - [作業フロー](#作業フロー-2)
    - [手順 1: host\_vars\_structured.schema.yaml に追記する](#手順-1-host_vars_structuredschemayaml-に追記する-1)
  - [service 定義変数を追加する作業](#service-定義変数を追加する作業)
    - [service 定義の仕組み](#service-定義の仕組み)
    - [手順 1: convert-rule-config.yaml に変換ルールを追加する](#手順-1-convert-rule-configyaml-に変換ルールを追加する)
    - [手順 2: field\_metadata.yaml に追記する](#手順-2-field_metadatayaml-に追記する)
    - [手順 4: network\_topology.yaml にサービス設定を記述する](#手順-4-network_topologyyaml-にサービス設定を記述する)
  - [node role を追加する作業](#node-role-を追加する作業)
    - [ノードロールの仕組み](#ノードロールの仕組み)
    - [ノードへのロール追加](#ノードへのロール追加)
    - [ネットワークロールポリシーを変更する作業](#ネットワークロールポリシーを変更する作業)
  - [補足: Python 実装追加要否判断基準](#補足-python-実装追加要否判断基準)
    - [Python 追加が不要なケース](#python-追加が不要なケース)
      - [ケース1: サービス設定の単純なキー変換の例](#ケース1-サービス設定の単純なキー変換の例)
      - [ケース2: サービス有効フラグの出力の例](#ケース2-サービス有効フラグの出力の例)
      - [ケース3: config 値の通過制御の例](#ケース3-config-値の通過制御の例)
      - [ケース4: サービス無効時に削除するキーの定義の例](#ケース4-サービス無効時に削除するキーの定義の例)
      - [ケース5: network\_role ポリシー値の差し替え例](#ケース5-network_role-ポリシー値の差し替え例)
    - [Python 追加が必要なケース](#python-追加が必要なケース)
      - [ケース1: ノード横断/ネットワーク横断の計算](#ケース1-ノード横断ネットワーク横断の計算)
      - [ケース2: NIC 優先選定と検証](#ケース2-nic-優先選定と検証)
      - [ケース3: 辞書型/リスト型の既定値自動生成](#ケース3-辞書型リスト型の既定値自動生成)
      - [ケース4: サービス設定の自動注入](#ケース4-サービス設定の自動注入)
      - [ケース5: 生成パイプラインへの新規ステップ追加](#ケース5-生成パイプラインへの新規ステップ追加)
    - [Python 追加が必要な場合に参照する既存コード](#python-追加が必要な場合に参照する既存コード)
    - [実装判断の実務ルール](#実装判断の実務ルール)
  - [変更後に確認する生成物](#変更後に確認する生成物)
  - [関連テストで確認するポイント](#関連テストで確認するポイント)
  - [関連資料](#関連資料)


## 対象読者と前提知識

このガイドは, [ansible-linux-setup](https://github.com/takeharukato/ansible-linux-setup) 向けの Ansible ロールを開発する方を対象としています。

次のことを前提とします。

- Ansible のホスト変数とロールの基本的な考え方を理解していること
- YAML Ain't Markup Language (以下 YAML と略す) の基本的な書き方を理解していること
- Python のデータ型 (dict, list, str, int, bool) を把握していること

## 本ツールで扱う変数モデル

本ツールが生成する変数には次の 3 種類があります。

| 種類 | 説明 | 例 |
|---|---|---|
| スカラー変数 | 単一の値を持つキーと値のペア | `gitlab_hostname: "gitlab.example.local"` |
| リスト変数 | 辞書の配列 | `frr_ebgp_neighbors: [{addr: ..., asn: ...}]` |
| 辞書型変数 | ネストした辞書構造 | `k8s_bgp: {enabled: true, local_asn: 65001, ...}` |


## 変更時に見るべき主要ファイル

| ファイル | 役割 | 変更する場面 |
|---|---|---|
| `field_metadata.yaml` | スカラーの名称, 型, 制約を定義する | スカラー変数を追加するとき |
| `host_vars_structured.schema.yaml` | 中間出力の JavaScript Object Notation (以下 JSON と略す) Schema を定義する | リスト, 辞書を追加するとき |
| `convert-rule-config.yaml` | サービス設定からスカラーへの変換ルールを定義する | サービス定義変数を追加するとき |
| `network_topology.yaml` | ノードの設定値を定義する | 実際の設定値を書くとき |
| 生成ロジック (`lib/` 配下) | スカラー/リスト/辞書の生成処理を実装する | 自動導出が必要なリスト/辞書変数を追加するとき |

## スカラー変数を追加する作業

### 作業フロー

スカラー変数の追加は次の 4 ファイルへの変更で完結します。

1. `field_metadata.yaml`: 変数の名称, 型, 制約を登録する
3. `network_topology.yaml`: 設定値を記述する
4. Ansible ロール/テンプレート: `{{ 変数名 }}` で参照する

### 手順 1: field_metadata.yaml に追記する

`fields` セクションに新しいエントリを追加します。

| キー | 内容 | 例 |
|---|---|---|
| `type` | 値の型。`string`, `integer`, `boolean`, `hostname`, `interface`, `cidr`, `ip`, `number` のいずれか | `string` |
| `description` | Comma-Separated Values (以下 CSV と略す) と YAML コメントに出力する説明文 | `"GitLab サーバのホスト名"` |
| `category` | ノード設定パラメタデザインシート/パラメタデザインシート での分類グループ。行の並び順に影響する | `infrastructure` |
| `allowed_range` | 値の制約。種別は `numeric`, `enum`, `pattern`, `semantic` | `{kind: semantic, name: fqdn}` |
| `allowed_values` | 許容する値の列挙リスト (`allowed_range` の代わりに使用) | `["true", "false"]` |

```yaml
# field_metadata.yaml への追記例
fields:
  my_service_hostname:
    type: hostname
    description: MyService サーバのホスト名
    category: infrastructure
    allowed_range:
      kind: semantic
      name: fqdn
```


`schema` セクションに変数名と Python 型のペアを追加します。

| 記法 | 意味 |
|---|---|
| `変数名: str` | 文字列型 |
| `変数名: int` | 整数型 |
| `変数名: bool` | 真偽値型 |

```yaml
schema:
  my_service_hostname: str
```

### 手順 3: network_topology.yaml に値を記述する

`globals.scalars` (全ノード共通値) またはノードの `scalars` セクション (ノード固有値) に記述します。

```yaml
# globals に書く場合 (全ノード共通の既定値)
globals:
  scalars:
    my_service_hostname: "my-service.example.local"

# 特定ノードで上書きする場合
nodes:
  - hostname_fqdn: node01.example.local
    scalars:
      my_service_hostname: "node01-service.example.local"
```

### 確認

追加後, 次のコマンドで ノード設定パラメタデザインシート に新しい行が出現し, 値が期待通りであることを確認します。

```shell
generate_host_vars_structured.py -i network_topology.yaml -o host_vars_structured.yaml && \
generate_hostvars_matrix.py -H host_vars_structured.yaml -m field_metadata.yaml \
  -o host_vars_scalars_matrix.csv
```

## リスト変数を追加する作業

### 作業フロー

リスト変数の追加は次の 3 ファイルへの変更が基本です。

1. `host_vars_structured.schema.yaml`: 中間出力の JSON Schema に配列定義を追加する
3. 生成ロジック (`lib/` 配下): 配列を組み立てる Python 関数を追加/拡張する

### 手順 1: host_vars_structured.schema.yaml に追記する

`$defs` セクションに要素の型定義を追加し, `host` の `properties` 配下に配列型として定義します。

| キー | 意味 | 例 |
|---|---|---|
| `$defs/{名前}` | 要素の型定義 | `$defs/my_list_item:` |
| `type: object` | リストの各要素が辞書であることを示す | |
| `required: [...]` | 必須フィールドの列挙 | `required: [addr, port]` |
| `properties.{フィールド名}` | 各フィールドの型を定義する | `addr: {type: string}` |

```yaml
# host_vars_structured.schema.yaml への追記例
$defs:
  my_list_item:
    type: object
    required:
      - addr
      - port
    additionalProperties: false
    properties:
      addr:
        type: string
      port:
        type: integer

# host の properties に追記
$defs:
  host:
    properties:
      my_service_list:
        type: array
        items:
          $ref: '#/$defs/my_list_item'
```


リスト本体と, 各要素のフィールドをドット記法で登録します。

```yaml
schema:
  my_service_list: list
  my_service_list.addr: str
  my_service_list.port: int
```

### 手順 3: 生成ロジックを追加する

トポロジー情報からリストを組み立てる Python 関数を `lib/` 配下に追加し, `lib/hostvars_node_pipeline.py` の適切な処理ステップから呼び出します。

既存の実装例として次のファイルを参照してください。

- `lib/routing_frr.py`: `frr_ebgp_neighbors`, `frr_networks_v4` などのリスト生成
- `lib/k8s_normalize.py`: `k8s_bgp` などの辞書/リスト生成

## 辞書型ノード設定変数を追加する作業

### 作業フロー

辞書型変数の追加はリスト変数と同様ですが, JSON Schema の定義がネスト構造になります。

1. `host_vars_structured.schema.yaml`: 辞書型の JSON Schema を追加する
3. 生成ロジック (`lib/` 配下): 辞書を組み立てる Python 関数を追加する

### 手順 1: host_vars_structured.schema.yaml に追記する

辞書型は `$defs` に `type: object` として定義し, `$ref` で参照します。

```yaml
# 辞書型定義の追記例
$defs:
  my_service_config:
    type: object
    required:
      - enabled
    additionalProperties: false
    properties:
      enabled:
        type: boolean
      endpoint:
        type: string
      port:
        type: integer

# host の properties に追記
$defs:
  host:
    properties:
      my_service_config:
        $ref: '#/$defs/my_service_config'
```


ドット記法でネストした全フィールドを登録します。

```yaml
schema:
  my_service_config: dict
  my_service_config.enabled: bool
  my_service_config.endpoint: str
  my_service_config.port: int
```

## service 定義変数を追加する作業

### service 定義の仕組み

`network_topology.yaml` の `globals.services` (または `nodes[].services`) でサービスの設定を記述すると, `convert-rule-config.yaml` の変換ルールを介してスカラー変数に展開されます。

Ansible ロールで新しいサービスのスカラーを参照したい場合, 次のファイルを変更します。

1. `convert-rule-config.yaml`: `service_settings.services` に変換ルールを追加する
2. `field_metadata.yaml`: 生成されるスカラーの定義を追加する
4. `network_topology.yaml`: サービスの設定値を記述する

### 手順 1: convert-rule-config.yaml に変換ルールを追加する

`service_settings.services` に新しいサービス名でエントリを作成します。

| キー | 意味 | 指定例 |
|---|---|---|
| `enabled_flag` | サービス有効ノードに常に `true` で出力するスカラー名 | `my_service_enabled` |
| `key_map` | `config.{入力キー}` をどのスカラー名に変換するためのマッピング | `hostname: my_service_hostname` |
| `passthrough_all_config` | `key_map` で変換済み以外の `config` キーをそのまま出力する | `true` / `false` |
| `config_keys` | `passthrough_all_config: false` の場合に出力を許可するキーの列挙 | `[setting1, setting2]` |
| `disabled_service_cleanup_keys` | サービスが無効なノードで削除するスカラーキーの列挙 | `[my_service_enabled, my_service_hostname]` |

```yaml
# convert-rule-config.yaml への追記例
service_settings:
  services:
    my_service:
      enabled_flag: my_service_enabled
      key_map:
        hostname: my_service_hostname
        port: my_service_port
      disabled_service_cleanup_keys:
        - my_service_enabled
        - my_service_hostname
        - my_service_port
      passthrough_all_config: false
```

### 手順 2: field_metadata.yaml に追記する

生成されるスカラーをすべて `fields` に登録します。

```yaml
# field_metadata.yaml への追記例
fields:
  my_service_enabled:
    type: boolean
    description: MyService 有効化フラグ
    category: infrastructure
    allowed_values:
      - "true"
      - "false"
  my_service_hostname:
    type: hostname
    description: MyService ホスト名
    category: infrastructure
    allowed_range:
      kind: semantic
      name: fqdn
  my_service_port:
    type: integer
    description: MyService ポート番号
    category: infrastructure
    allowed_range:
      kind: numeric
      min: 1
      max: 65535
```


```yaml
schema:
  my_service_enabled: bool
  my_service_hostname: str
  my_service_port: int
```

### 手順 4: network_topology.yaml にサービス設定を記述する

`globals.services` にサービス既定値を, `globals.roles` にロールとサービスの関係を定義します。

```yaml
globals:
  services:
    my_service:
      config:
        hostname: "my-service.example.local"
        port: 8080
  roles:
    my_role: [my_service]

nodes:
  - hostname_fqdn: node01.example.local
    roles: [my_role]
```

## node role を追加する作業

### ノードロールの仕組み

`globals.roles` はロール名とサービス一覧のマッピングです。ノードに `roles: [my_role]` を指定すると, そのロールに紐づくサービスが有効になります。

`convert-rule-config.yaml` の `network_role` セクションは, ネットワークロール (ネットワークセグメントの役割) に基づいて NIC 変数や Free Range Routing (以下 FRR と略す) 設定を導出するポリシーを定義します。

### ノードへのロール追加

既存のロールをノードに割り当てるだけであれば, `network_topology.yaml` の変更だけで完結します。

```yaml
globals:
  roles:
    my_new_role: [service_a, service_b]  # 新しいロールの定義

nodes:
  - hostname_fqdn: node01.example.local
    roles: [my_new_role]
```

### ネットワークロールポリシーを変更する作業

`convert-rule-config.yaml` の `network_role` セクションを変更することで, ネットワークセグメントのロールが NIC 変数や FRR 経路生成に与える影響を制御できます。

| ポリシーキー | 意味 | 変更の影響 |
|---|---|---|
| `role_priority` | DNS ドメイン自動導出時の優先度。小さい値が優先される | DNS 関連スカラーの導出結果が変わる |
| `management_roles` | 管理系ネットワークとして扱うロールの集合 | 将来の拡張時に参照される |
| `data_plane_roles` | `k8s_nic` 候補として扱うロールの集合 | `k8s_nic` に選ばれる NIC が変わる |
| `frr_advertise_roles` | FRR 経路広報対象に含めるロールの集合 | `frr_networks_v4/v6` の内容が変わる |
| `internal_network_list_roles` | `internal_network_list` に含めるロールの集合 | DNS サーバ向けの内部ネットワーク一覧が変わる |
| `internal_mgmt_role` | 内部管理ネットワークとして扱う単一のロール名 | `gpm_mgmt_nic` の NIC 選定に影響する |
| `external_mgmt_role` | 外部管理ネットワークとして扱う単一のロール名 | `mgmt_nic` の NIC 選定に影響する |

新しいネットワーク用途のロールを追加し, そのロールが特定のポリシーに含まれるべき場合は, 該当するポリシーキーのリストに追加します。

```yaml
# convert-rule-config.yaml の network_role 追記例
network_role:
  data_plane_roles:
    - data_plane_network
    - my_storage_network   # 追加
  frr_advertise_roles:
    - external_control_plane_network
    - private_control_plane_network
    - data_plane_network
    - bgp_transport_network
    - my_storage_network   # 必要なら追加
```

各ポリシーの詳細は [変換ルール設定リファレンスマニュアル](convert-rule-config-reference.md) の `network_role` セクションを参照してください。

## 補足: Python 実装追加要否判断基準

この節では, `convert-rule-config.yaml` だけで対応可能な拡張と, Python 実装が必要な拡張とを区別するための判断方針を示します。

### Python 追加が不要なケース

次のような変更は, 原則として `convert-rule-config.yaml` のルール追記だけで対応できます。

| ケース | 具体例 | 主に変更する場所 |
|---|---|---|
| サービス設定の単純なキー変換 | `config.hostname` を `gitlab_hostname` へ写像する | `service_settings.services.{service}.key_map` |
| サービス有効フラグの出力 | サービス有効ノードに `*_enabled: true` を出力する | `service_settings.services.{service}.enabled_flag` |
| config 値の通過制御 | `config` をそのまま出力する, または許可キーだけ出力する | `passthrough_all_config`, `config_keys` |
| 無効時に消すキーの定義 | サービス無効ノードでスカラーを削除する | `disabled_service_cleanup_keys` |
| 既存ポリシー値の差し替え | `data_plane_roles`, `frr_advertise_roles` の集合を変更する | `network_role` セクション |

#### ケース1: サービス設定の単純なキー変換の例

`service_settings.services.{service}.key_map` に, 入力側キーと出力側キーの対応を追加します。

```yaml
service_settings:
  services:
    my_service:
      key_map:
        hostname: my_service_hostname
        port: my_service_port
```

`network_topology.yaml` 側は `services.{service}.config` に入力キーを記述します。

```yaml
globals:
  services:
    my_service:
      config:
        hostname: my-service.example.local
        port: 8080
```

#### ケース2: サービス有効フラグの出力の例

`enabled_flag` を指定すると, そのサービスが有効なノードに `true` が出力されます。

```yaml
service_settings:
  services:
    my_service:
      enabled_flag: my_service_enabled
```

#### ケース3: config 値の通過制御の例

通過制御は `passthrough_all_config` と `config_keys` で行います。

1. 全通過: `passthrough_all_config: true`
2. 選択通過: `passthrough_all_config: false` + `config_keys`

型別の具体例を以下に示します。

**3-1. スカラ値を通過させる例**

```yaml
service_settings:
  services:
    scalar_service:
      passthrough_all_config: false
      config_keys:
        - endpoint
```

```yaml
globals:
  services:
    scalar_service:
      config:
        endpoint: api.example.local
```

**3-2. リスト値を通過させる例**

```yaml
service_settings:
  services:
    list_service:
      passthrough_all_config: false
      config_keys:
        - allowed_cidrs
```

```yaml
globals:
  services:
    list_service:
      config:
        allowed_cidrs:
          - 10.10.0.0/16
          - 10.20.0.0/16
```

**3-3. 辞書値を通過させる例**

```yaml
service_settings:
  services:
    dict_service:
      passthrough_all_config: false
      config_keys:
        - tls
```

```yaml
globals:
  services:
    dict_service:
      config:
        tls:
          enabled: true
          cert_path: /etc/pki/tls/certs/service.crt
```

**3-4. 辞書のリスト値を通過させる例**

```yaml
service_settings:
  services:
    dict_list_service:
      passthrough_all_config: false
      config_keys:
        - upstreams
```

```yaml
globals:
  services:
    dict_list_service:
      config:
        upstreams:
          - host: 10.0.10.11
            port: 6443
          - host: 10.0.10.12
            port: 6443
```

**3-5. すべての config キーを通過させる例**

```yaml
service_settings:
  services:
    passthrough_service:
      passthrough_all_config: true
```

この場合, `config` 内のスカラ, リスト, 辞書, 辞書のリストがそのまま出力へ渡されます。

#### ケース4: サービス無効時に削除するキーの定義の例

`disabled_service_cleanup_keys` に列挙したキーは, サービスが無効なノードで削除対象になります。

```yaml
service_settings:
  services:
    my_service:
      enabled_flag: my_service_enabled
      disabled_service_cleanup_keys:
        - my_service_enabled
        - my_service_hostname
        - my_service_port
```

#### ケース5: network_role ポリシー値の差し替え例

既存ロジックを変えずに挙動だけ変えたい場合は, `network_role` セクションを更新します。

```yaml
network_role:
  data_plane_roles:
    - data_plane_network
    - storage_network
  frr_advertise_roles:
    - external_control_plane_network
    - private_control_plane_network
    - data_plane_network
    - storage_network
```

### Python 追加が必要なケース

次のような変更は, ルール記述だけでは完結せず Python 実装が必要です。

| ケース | 理由 | 代表的な出力例 |
|---|---|---|
| ノード横断/ネットワーク横断の計算 | 複数ノードや同一データセンタ全体を走査して計算する必要がある | `frr_networks_v4`, `frr_networks_v6` |
| NIC の優先選定と検証 | `mgmt_nic`/`gpm_mgmt_nic`/`k8s_nic` を条件分岐で選び, 予約ペア検証も行う | `mgmt_nic`, `k8s_nic` |
| 辞書型/リスト型の既定値自動生成 | 入力不足時に構造化データを組み立てる処理が必要 | `k8s_bgp`, `k8s_worker_frr` |
| サービス設定の自動注入 | services へ自動導出値を注入してからスカラー変換する必要がある | `radvd`, `internal_router` の自動項目 |
| 生成パイプラインへの新規ステップ追加 | 既存処理順へ新しい計算処理を組み込む必要がある | host エントリ組み立て全般 |

各ケースへの具体的な対処方法は, 処理内容の実装に依存して変わるため, 本節では, 具体的な記述例ではなく, 各ケースでの記述方針について述べる。

#### ケース1: ノード横断/ネットワーク横断の計算

記述方針:

1. 計算対象 (例: 同一 datacenter ノード) を明示する。
2. 収集条件 (例: `network.role` が対象集合に含まれる) を明示する。
3. 出力形式 (例: `frr_networks_v4: list[str]`) を固定する。

参照実装: `lib/routing_frr.py` の `build_frr_networks`。

#### ケース2: NIC 優先選定と検証

記述方針:

1. 優先順位 (external -> internal など) を先に定義する。
2. フォールバック条件を定義する。
3. 妥当性検証 (予約ペア, 必須 NIC 存在) を例外で明示する。

参照実装: `lib/netif_builder.py` の `derive_nic_variables`。

#### ケース3: 辞書型/リスト型の既定値自動生成

記述方針:

1. 入力不足時の既定値を導出する情報を定義する。
2. ネスト構造の最終スキーマに合わせて出力を組み立てる。

参照実装: `lib/k8s_normalize.py` の `build_default_k8s_bgp`。

#### ケース4: サービス設定の自動注入

記述方針:

1. サービス有効判定後に自動導出関数を実行する。
2. 既存 `config` と導出値をマージする。
3. その後に通常の `service_settings_to_scalars` 変換へ渡す。

参照実装: `lib/service_processing.py` の `apply_auto_service_configs`。

#### ケース5: 生成パイプラインへの新規ステップ追加

記述方針:

1. ノード単位処理の新処理を実行ステップを決定する。
2. 既存ステップの入出力 (`host_entry`, `scalars`) を壊さない形で接続する。
3. 既存の pass-through 項目と競合しないことを確認する。

参照実装: `lib/hostvars_node_pipeline.py` の `apply_node_routing_entries`, `apply_node_service_scalars`。

### Python 追加が必要な場合に参照する既存コード

実装時は, 追加したい機能に最も近い既存関数を最初に参照します。

| 追加したい処理 | 参照する既存コード |
|---|---|
| サービス設定 -> スカラー変換の拡張 | `lib/service_rules.py` の `map_service_config_to_scalars` |
| サービス自動設定の注入 | `lib/service_processing.py` の `apply_auto_service_configs` |
| NIC 変数導出の追加/変更 | `lib/netif_builder.py` の `derive_nic_variables` |
| FRR 広報ネットワーク生成の追加/変更 | `lib/routing_frr.py` の `build_frr_networks` |
| Kubernetes Border Gateway Protocol (以下 BGP と略す) 既定値生成の追加/変更 | `lib/k8s_normalize.py` の `build_default_k8s_bgp` |
| ノード生成パイプラインへの組み込み | `lib/hostvars_node_pipeline.py` の `apply_node_routing_entries`, `apply_node_service_scalars` |
| ルール読み込みと実行フローの入口確認 | `generate_host_vars_structured.py` の `generate_host_vars_structured` |

### 実装判断の実務ルール

迷う場合は, 次の順で判断すると実装方針を誤りにくくなります。

1. 変更内容が `service_settings` の写像規則だけで表現可能であることを確認する。
2. 単一ノード内の静的変換で完結するなら, まず `convert-rule-config.yaml` で対応する。
3. ノード横断計算, 自動補完, 構造生成が必要なら, Python 関数を追加する。

## 変更後に確認する生成物

変更後は必ず次のコマンドを実行して, 期待した変数が生成されることを確認してください。

```shell
generate_host_vars_structured.py -i network_topology.yaml -o host_vars_structured.yaml && \
generate_hostvars_matrix.py -H host_vars_structured.yaml -m field_metadata.yaml \
  -o host_vars_scalars_matrix.csv
```

CSV を表計算ソフトで確認し, 追加したスカラーが対象ノードの列に正しい値で現れることを確認します。

## 関連テストで確認するポイント

`tests/tests_py/` 配下に次のテストがあります。変数追加後はこれらが引き続きパスすることを確認してください。

| テストファイル | 確認内容 |
|---|---|
| `test_service_settings_to_scalars_rules.py` | `service_settings` の変換ルール (`enabled_flag`, `key_map`, `passthrough_all_config`) |
| `test_network_role_policy.py` | `network_role` ポリシーの解析と判定 |
| `test_prototype_generators.py` | サンプル topology からの CSV とファイル生成 (エンドツーエンド) |
| `test_k8s_normalize.py` | K8s 関連の辞書型変数の導出 |
| `test_routing_frr.py` | FRR 関連のリスト型変数の導出 |

```shell
make check
```

## 関連資料

- [ツールチェイン概要](toolchain-overview.md)
- [スキーマファイルリファレンスマニュアル](schema-files-reference.md)
- [変換ルール設定リファレンスマニュアル](convert-rule-config-reference.md)
- [フィールドメタデータリファレンスマニュアル](field-metadata-reference.md)
- [トラブルシューティング](troubleshooting.md)
