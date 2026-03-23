#!/bin/sh
set -eu


WORKDIR=/tmp/project-build
mkdir -p "${WORKDIR}"

# /src にソースがマウントされている前提
cp -a /src/. "${WORKDIR}/"
cd "${WORKDIR}"

echo "[entrypoint-rpm] autogen.sh / configure / ソース tarball 生成 / rpmbuild を実行します"

# 1. autotools 設定生成
./autogen.sh
sed -i 's/^DISTFILESDEPS_ = update-po$/DISTFILESDEPS_ =/' po/Makefile.in.in
./configure

# 2. rpmbuild 用のソースアーカイブ生成
VERSION="$(sed -n 's/^Version:[[:space:]]*//p' rpm/ansibleConfigGenerator.spec | head -n 1)"
PKGROOT="ansibleconfiggenerator-${VERSION}"
STAGEDIR="/tmp/${PKGROOT}"
TARBALL="${PKGROOT}.tar.gz"

if [ -z "$VERSION" ]; then
  echo "ERROR: rpm/ansibleConfigGenerator.spec から Version を取得できません" >&2
  exit 1
fi

rm -rf "$STAGEDIR" "$TARBALL"
mkdir -p "$STAGEDIR"

tar \
  --exclude-vcs \
  --exclude='./dist' \
  --exclude='./.pkgtest' \
  --exclude='./.venv' \
  --exclude='./tests/.pytest_cache' \
  --exclude='__pycache__' \
  -cf - . | tar -xf - -C "$STAGEDIR"

tar -czf "$TARBALL" -C /tmp "$PKGROOT"

if [ ! -f "$TARBALL" ]; then
  echo "ERROR: ソース tarball $TARBALL が生成されていません" >&2
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
