#!/bin/sh
set -eu


WORKDIR=/tmp/project-build
mkdir -p "${WORKDIR}"

# /src にソースがマウントされている前提
cp -a /src/. "${WORKDIR}/"
cd "${WORKDIR}"

echo "[entrypoint-rpm] autogen.sh / configure / update-po / dist / rpmbuild を実行します"

# 1. autotools と i18n 更新
./autogen.sh
./configure

# po カタログ更新
( cd po && make update-po )

# 2. 配布用ソースアーカイブ生成 (ansibleConfigGenerator-<version>.tar.gz)
make dist

TARBALL="$(ls -t *.tar.gz | head -n 1 || true)"

if [ -z "$TARBALL" ] || [ ! -f "$TARBALL" ]; then
    echo "ERROR: make dist で *.tar.gz が生成されていません" >&2
    exit 1
fi

echo "[entrypoint-rpm] TARBALL = $TARBALL"

# 3. rpmbuild 用ディレクトリ
TOPDIR=/tmp/rpmbuild
mkdir -p "$TOPDIR"/{BUILD,RPMS,SOURCES,SPECS,SRPMS}

# 4. rpmbuild -ta で RPM ビルド
# コンテナ環境のリポジトリ事情で BuildRequires 名解決が失敗する場合があるため,
# ここでは --nodeps でパッケージ生成を優先する。
echo "[entrypoint-rpm] rpmbuild -ta --nodeps を実行します"
rpmbuild -ta --nodeps "$TARBALL" \
  --define "_topdir $TOPDIR"

# 5. 生成された .rpm を /dist にコピー
echo "[entrypoint-rpm] /dist へ .rpm をコピーします"
mkdir -p /dist
find "$TOPDIR/RPMS" -type f -name '*.rpm' -print -exec cp -v {} /dist/ \;

echo "[entrypoint-rpm] 完了しました"
