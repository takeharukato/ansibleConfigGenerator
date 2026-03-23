# 変換ルール設定リファレンスマニュアル (convert-rule-config.yaml)

`convert-rule-config.yaml` は `network_topology.yaml` の `services` セクションやネットワークロールに関する変換ルールを一元管理するファイルです。`generate_host_vars_structured.py` が参照し, サービス設定からスカラー変数への変換ポリシーとネットワークロールポリシーを決定します。

## ファイルの構成

| トップレベルキー | 役割 |
|---|---|
| `service_settings` | サービス設定からスカラー変数への変換ルールを定義する |
| `network_role` | ネットワークセグメントのロールに基づく判定ポリシーを定義する |

---

## service_settings セクション

`network_topology.yaml` の `globals.services` または `nodes[].services` に記述したサービス設定を, Ansible host_vars のスカラー変数へ変換するルールを定義します。

### service_settings.services

各サービスのエントリは `services.{サービス名}: {ルール辞書}` の形式で記述します。

#### ルール辞書のキー

| キー | 型 | 省略時の動作 | 説明 |
|---|---|---|---|
| `enabled_flag` | string | 出力しない | サービスが有効なノードで常に `true` として出力するスカラー名を指定する |
| `key_map` | object | 変換しない | `config` の入力キーから出力スカラー名へのマッピングを定義する |
| `passthrough_all_config` | boolean | `false` | `true` の場合, `key_map` で変換済み以外の `config` キーもそのまま出力する |
| `config_keys` | array of string | 全出力 | `passthrough_all_config: false` のとき, 出力を許可する `config` キーを明示的に列挙する |
| `fixed_values` | object | 追加しない | 常に出力に追加する固定値のキーと値のマッピングを定義する |
| `disabled_service_cleanup_keys` | array of string | 削除しない | サービスが無効なノードで削除するスカラーキーを列挙する |

#### サービスエントリの例

```yaml
service_settings:
  services:
    # enabled_flag のみ: サービス有効ノードに k8s_hubble_cli_enabled: true を出力する
    hubble_cli:
      enabled_flag: k8s_hubble_cli_enabled

    # key_map あり: config.hostname を gitlab_hostname へ変換し, 残りをそのまま出力する
    gitlab:
      disabled_service_cleanup_keys:
        - gitlab_hostname
        - gitlab_enable_backup_script
      key_map:
        hostname: gitlab_hostname
      passthrough_all_config: true

    # config_keys 指定: config.external_ntp_servers_list と ntp_allow のみ出力する
    ntp-server:
      disabled_service_cleanup_keys:
        - ntp_allow
        - external_ntp_servers_list
      config_keys:
        - external_ntp_servers_list
        - ntp_allow
```

### 既定のサービス定義一覧

以下は `convert-rule-config.yaml` に登録済みのサービスと, 各サービスの主要なルールです。

| サービス名 | enabled_flag | key_map の主な変換 | passthrough_all_config | disabled_service_cleanup_keys (主要) |
|---|---|---|---|---|
| `gitlab` | なし | `hostname` -> `gitlab_hostname` | `true` | `gitlab_hostname`, バックアップ関連 |
| `cilium` | なし | `version` -> `k8s_cilium_version`, CA 関連 | `false` (key_map のみ) | なし |
| `multus` | `k8s_multus_enabled` | `version` -> `k8s_multus_version` | `false` | なし |
| `whereabouts` | `k8s_whereabouts_enabled` | `version`, IPv4/IPv6 レンジ各キー | `false` | なし |
| `hubble_cli` | `k8s_hubble_cli_enabled` | なし | `false` | なし |
| `hubble_ui` | `k8s_hubble_ui_enabled` | なし | `false` | なし |
| `helm` | `k8s_helm_enabled` | `version` -> `k8s_helm_version` | `false` | なし |
| `terraform` | `terraform_enabled` | なし | `false` | `terraform_enabled` |
| `ntp-server` | なし | なし | `false` | `ntp_allow`, `external_ntp_servers_list` |
| `dns-server` | なし | なし | `true` | DNS 関連スカラー |
| `netgauge` | `netgauge_enabled` | なし | `true` | `netgauge_*` |
| `docker-ce` | なし | なし | `true` | Docker CE バックアップ関連 |
| `backup_home` | なし | なし | `true` | バックアップ関連スカラー |
| `rancher` | なし | なし | `true` | Rancher 関連スカラー |
| `ldap` | なし | なし | `true` | LDAP 関連スカラー |
| `nfs-server` | なし | なし | `true` | NFS 関連スカラー |
| `redmine` | なし | なし | `true` | Redmine バックアップ関連 |
| `kea-dhcp` | なし | なし | `true` | GPM 管理ネットワーク関連 |
| `internal_router` | なし | なし | `true` | ルーター転送/NAT 関連 |
| `radvd` | なし | なし | `true` | ルーター広告関連 |
| `nm_ddns` | なし | なし | `true` | DNS 逆引き関連 |
| `k8s_control_plane_base` | なし | なし | `true` | `k8s_reserved_system_cpus_default` |
| `k8s_worker_base` | なし | なし | `true` | ワーカーノード関連 |
| `k8s_node_common` | なし | なし | `true` | Kubernetes 共通スカラー |
| `vm_params` | なし | なし | `true` | なし |
| `mdns` | なし | なし | `true` | `mdns_enabled`, `mdns_host_list` |
| `ntp_client` | なし | なし | `true` | `ntp_servers_list` |
| `proxy_client` | なし | なし | `true` | プロキシ関連スカラー |
| `sudo` | なし | なし | `true` | sudo 権限関連 |
| `user_skel` | なし | なし | `true` | スケルトン/ユーザー設定関連 |

---

## network_role セクション

ネットワークセグメントのロール (`globals.networks.{name}.role`) に基づいて, NIC 変数や BGP ルーティング設定の導出ポリシーを定義します。

`network_topology.yaml` で定義したネットワークロールが変数生成のどの処理に影響するかは, 以下のポリシーキーで制御します。

### ポリシーキー一覧

| キー | 型 | 説明 |
|---|---|---|
| `role_priority` | object | DNS ドメイン導出時の優先度マッピング (ロール名 -> 整数, 小さいほど優先) |
| `management_roles` | array of string | 管理系ネットワークとして扱うロールの集合 |
| `data_plane_roles` | array of string | `k8s_nic` 候補として選ぶロールの集合 |
| `frr_advertise_roles` | array of string | FRR 広報対象ネットワークを選ぶロールの集合 |
| `internal_network_list_roles` | array of string | `internal_network_list` に含めるロールの集合 |
| `internal_mgmt_role` | string | 内部管理ネットワークとして扱う単一ロール名 |
| `external_mgmt_role` | string | 外部管理ネットワークとして扱う単一ロール名 |

### 各ポリシーの詳細

#### role_priority

| 対象 | 動作 |
|---|---|
| DNS ドメイン (`dns_domain`) の自動導出 | 複数の管理ネットワークに接続しているノードで, 最小値のロールを持つインターフェースの `dns_search` が採用される |

ここに未定義のロールは DNS ドメイン導出の候補に入りません。

```yaml
# デフォルト設定
network_role:
  role_priority:
    private_control_plane_network: 0
    external_control_plane_network: 1
```

#### management_roles

| 対象 | 動作 |
|---|---|
| 管理系ネットワーク判定 | 主にポリシーの意味づけと将来拡張用。`internal_mgmt_role` や `external_mgmt_role` との整合を確認してから変更する |

#### data_plane_roles

| 対象 | 動作 |
|---|---|
| `k8s_nic` の選定 | ノードの `datacenter` / `cluster` に一致するネットワークのうち, ここに含まれるロールのインターフェースが `k8s_nic` の候補になる |

```yaml
network_role:
  data_plane_roles:
    - data_plane_network
```

#### frr_advertise_roles

| 対象 | 動作 |
|---|---|
| `frr_networks_v4` / `frr_networks_v6` の生成 | 同一データセンタのノードが接続するネットワークのうち, ここに含まれるロールの CIDR が広報対象になる |

```yaml
network_role:
  frr_advertise_roles:
    - external_control_plane_network
    - private_control_plane_network
    - data_plane_network
    - bgp_transport_network
```

#### internal_network_list_roles

| 対象 | 動作 |
|---|---|
| `internal_network_list` の生成 | `globals.networks` のうち, ここに含まれるロールのネットワークだけが DNS サーバ向けの内部ネットワーク一覧に含まれる |

#### internal_mgmt_role / external_mgmt_role

| キー | 影響を受ける処理 |
|---|---|
| `internal_mgmt_role` | `gpm_mgmt_nic` の NIC 選定, radvd 対象ネットワーク選択, 内部ルーターの内部側ネットワーク選択 |
| `external_mgmt_role` | `mgmt_nic` の優先選択, 内部ルーターの外部側ネットワーク選択 |

```yaml
network_role:
  internal_mgmt_role: private_control_plane_network
  external_mgmt_role: external_control_plane_network
```

---

## 関連資料

- [ロール作成者向けガイド](ansible-role-author-guide.md): サービス定義変数とノードロールの追加手順
- [スキーマファイル参照](schema-files-reference.md): 入力スキーマの詳細
- [フィールドメタデータ参照](field-metadata-reference.md): スカラー変数の型と制約定義
