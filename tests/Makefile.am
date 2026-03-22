# -*- mode: makefile; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2026 Takeharu KATO
#
# This file is distributed under the two-clause BSD license.
# For the full text of the license, see the LICENSE file in the project root directory.
# このファイルは2条項BSDライセンスの下で配布されています。
# ライセンス全文はプロジェクト直下の LICENSE を参照してください。
#
# OpenAI's ChatGPT partially generated this code.
# Author has modified some parts.
# OpenAIのChatGPTがこのコードの一部を生成しました。
# 著者が修正している部分があります。

##
SUBDIRS = mt

## tests_py 以下やシェルスクリプトなど, 配布に含めたいファイル群
EXTRA_DIST = \
	tests_env.sh.sample

## automake の標準 TESTS 機構は使わず, check-local でテストを実行
TESTS =

.PHONY: coverage

## ----------------------------------------
## make check: mt/ 配下のテストを実行
## ----------------------------------------
check-local:
	@echo "Running tests in mt/..."
	@cd mt && $(MAKE) $(AM_MAKEFLAGS) check

## ----------------------------------------
## make coverage: Python カバレッジ計測
## - coverage モジュールが無ければスキップして正常終了
## - tests_env.sh があれば読み込み
## ----------------------------------------
coverage:
	@echo "Checking for Python coverage module..."
	@if $(PYTHON) -m coverage --version >/dev/null 2>&1; then \
	  echo "coverage module found; running coverage for gm_tools"; \
	  if test -f ./tests_env.sh; then \
	    echo "Sourcing ./tests_env.sh"; \
	    . ./tests_env.sh; \
	  fi; \
	  rm -f .coverage; \
	  cd mt && $(MAKE) $(AM_MAKEFLAGS) coverage; \
	else \
	  echo "coverage module not available; skipping coverage"; \
	fi

#------------------------------------------------------
# Clean up test logs
#------------------------------------------------------
CLEANFILES = \
	*.log \
	.coverage
