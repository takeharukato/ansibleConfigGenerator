# トラブルシューティング

本ページでは, ツール実行時に発生しやすい問題と対処方法を説明します。

## スキーマファイルが見つからない

### 症状

```
FileNotFoundError: スキーマファイル 'network_topology.schema.yaml' が見つかりません
```

または `--schema-dir` で指定したディレクトリが存在しないというエラー。

### 原因と確認手順

1. 探索順の確認: ツールは次の順でスキーマファイルを探します。

   | 優先順位 | 場所 |
   |---|---|
   | 1 | コマンドラインオプション `--schema-dir` |
   | 2 | ユーザ設定ファイル `~/.genAnsibleConf.yaml` の `schema_search_paths` |
   | 3 | システム設定ファイル `/etc/genAnsibleConf/config.yaml` の `schema_search_paths` |
   | 4 | 環境変数 `GENANSIBLECONF_SCHEMADIR` |
   | 5 | スクリプトと同じディレクトリ |

2. インストール済み環境では `/usr/share/genAnsibleConf/schema` にスキーマが配置されています。システム設定ファイルに `default_dir` が設定されているか確認してください。

### 対処

`--schema-dir` オプションでスキーマディレクトリを直接指定します。

```shell
generate_host_vars_structured.py \
  --schema-dir /usr/share/genAnsibleConf/schema \
  -i network_topology.yaml -o host_vars_structured.yaml
```

または, ユーザ設定ファイル (`~/.genAnsibleConf.yaml`) に検索パスを追加します。

```yaml
schema_search_paths:
  - /usr/share/genAnsibleConf/schema
```

---

## network_topology.yaml のスキーマ検証エラー

### 症状

```
ValidationError: 'nodes[0]' は必須フィールド 'interfaces' が不足しています
```

または `jsonschema.exceptions.ValidationError` の詳細メッセージ。

### 原因と確認手順

`network_topology.yaml` の記述が `network_topology.schema.yaml` の定義と一致していません。

1. エラーメッセージの `'nodes[0]'` のようなパスを手がかりに, 対象ノードの定義を確認します。
2. 条件付き必須フィールド: `roles` に `k8s_control_plane` を含む場合は `datacenter`, `cluster`, `scalars.k8s_ctrlplane_endpoint` などが必須になります。
3. `role` の値: `globals.networks.{name}.role` には定義済みの 4 種類の値 (`external_control_plane_network`, `private_control_plane_network`, `data_plane_network`, `bgp_transport_network`) のみ使用できます。
4. `name` フィールド: `nodes[].name` は英数字,`-`,`_` のみ使用できます。

### 対処

エラーメッセージの指示に従い, 不足フィールドや不正な値を修正してください。スキーマの詳細は [スキーマファイル参照](schema-files-reference.md) を確認してください。

---

## host_vars_structured.yaml の生成失敗

### 症状

`generate_host_vars_structured.py` が終了コード 1 で終了し, エラーメッセージが出力される。

### 原因と確認手順

1. `network_topology.yaml` のスキーマ検証エラー: 上記「スキーマ検証エラー」の節を参照してください。
2. 設定値の不整合: `globals.roles` に定義されていないロール名を `nodes[].roles` で参照している場合も失敗します。
3. データセンタ参照の不整合: `interfaces[].network` で参照するネットワーク名が `globals.networks` に存在しない場合も失敗します。

### 対処

まず `globals.networks`, `globals.datacenters`, `globals.roles` に必要な定義がすべて揃っているか確認します。次に `nodes` 側の参照が定義済みの名前と一致しているか照合します。

---

## CSV の値が期待通りでない

### 症状

`host_vars_scalars_matrix.csv` を開くと, 特定のホストのスカラー値が空白だったり, 期待と異なる値になっている。

### 原因と確認手順

1. **`globals.scalars` での上書き漏れ**: 全ノード共通の既定値は `globals.scalars` に記述します。ノード固有の値は `nodes[].scalars` に記述します。
2. **サービスが有効になっていない**: `enabled_flag` を持つサービス (multus, whereabouts など) のスカラーは, そのサービスが有効なノードでのみ出力されます。`nodes[].services.{サービス名}:` が正しく設定されているか確認してください。
3. **`key_map` の変換名が異なる**: `convert-rule-config.yaml` の `key_map` で, `config` のキー名と出力スカラー名の対応を確認してください。
4. **`field_metadata.yaml` に未登録のスカラー**: `field_metadata.yaml` に登録されていないスカラーは CSV の行として出力されません。新しいスカラーを追加した場合は `field_metadata.yaml` への追記が必要です。

### 対処

次の手順でデバッグします。

```shell
# host_vars_structured.yaml の内容を直接確認する
generate_host_vars_structured.py -i network_topology.yaml -o /tmp/hvs.yaml
cat /tmp/hvs.yaml
```

中間出力の `scalars` に期待する値が含まれているかを確認します。`scalars` に値があれば `field_metadata.yaml` の不足が原因です。`scalars` に値がなければ `convert-rule-config.yaml` または `network_topology.yaml` の設定を見直します。

---

## CSV のバリデーションエラー

### 症状

`validate_hostvars_matrix.py` 実行時に値が制約違反だというエラーが出る。

### 原因と確認手順

1. `allowed_range` の制約違反: `field_metadata.yaml` の `allowed_range` で定義した範囲を外れた値が設定されています。
2. `allowed_values` の制約違反: 許容値リスト外の文字列が設定されています。
3. 型不一致: `type_schema.yaml` の Python 型と実際の値の型が一致していません。

### 対処

エラーメッセージに表示されるフィールド名と値を確認し, `network_topology.yaml` の設定値を修正してください。制約の定義内容は [フィールドメタデータ参照](field-metadata-reference.md) を確認してください。

---

## Terraform 変数ファイルが生成されない

### 症状

`generate_terraform_tfvars.py` が空のファイルを出力する,または必要な変数が含まれていない。

### 原因と確認手順

1. `host_vars_structured.yaml` が最新か: `generate_host_vars_structured.py` を先に実行して中間出力を更新してから再試行してください。
2. Terraform 向けのノードが `host_vars_structured.yaml` に含まれているか: ノード定義の `roles` に Terraform 管理対象を示すロールが含まれているか確認してください。
3. `--include-nodes` または `--exclude-nodes` オプションの絞り込みが原因でノードが除外されていないか確認してください。

---

## サービスのスカラーが生成されない

### 症状

`convert-rule-config.yaml` の `enabled_flag` で定義したスカラー (`k8s_multus_enabled` など) が host_vars ファイルに出力されない。

### 原因と確認手順

1. `network_topology.yaml` でサービスが有効化されているか: `nodes[].services.{サービス名}:` または `globals.services.{サービス名}:` の定義が存在するか確認してください。
2. `network_topology.yaml` の `globals.roles` に対象サービスが含まれているか: `roles.{ロール名}: [サービス名]` の形式で登録されているか確認してください。
3. `nodes[].roles` に対象ロールが含まれているか確認してください。

---

## NIC 変数が期待通りに選ばれない

### 症状

`k8s_nic`, `mgmt_nic`, `gpm_mgmt_nic` が期待するインターフェース名にならない。

### 原因と確認手順

1. `k8s_nic`: `convert-rule-config.yaml` の `network_role.data_plane_roles` に含まれるロールのネットワークに接続するインターフェースが選ばれます。ノードの `datacenter` と `cluster` が正しく設定されているか確認してください。
2. `mgmt_nic`: `network_role.external_mgmt_role` (デフォルト: `external_control_plane_network`) のネットワークに接続するインターフェースが優先されます。
3. `gpm_mgmt_nic`: `network_role.internal_mgmt_role` (デフォルト: `private_control_plane_network`) のネットワークに接続するインターフェースが選ばれます。

### 対処

`generate_host_vars_structured.py` を実行して出力された `host_vars_structured.yaml` の `netif_list` を確認します。インターフェースの割り当てが正しければ, NIC 選定ポリシーの `convert-rule-config.yaml` を見直してください。詳細は [変換ルール設定参照](convert-rule-config-reference.md) の `network_role` セクションを参照してください。

---

## 関連資料

- [ユーザ向けワークフロー](user-guide-linux-ansible-setup.md)
- [ツールチェイン概要](toolchain-overview.md)
- [スキーマファイル参照](schema-files-reference.md)
- [変換ルール設定参照](convert-rule-config-reference.md)
- [フィールドメタデータ参照](field-metadata-reference.md)
