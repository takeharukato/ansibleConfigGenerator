# -*- mode: python; coding: utf-8; line-endings: unix -*-
# SPDX-License-Identifier: BSD-2-Clause
# Copyright (c) 2025 TAKEHARU KATO
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
"""
ローカル一時ディレクトリのクリーンアップと, ローカル実行の薄いラッパを提供します。
"""

from __future__ import annotations

import os
from importlib import import_module
from typing import List, Optional, Any
from .test_common_cleanup import safe_rmtree_abs
from ._local_types import Config
from ._local_types import LocalRun


def cleanup_local_temps(cfg: Config, rel_dirs: Optional[List[str]] = None) -> None:
    """共通のローカル一時ディレクトリクリーンアップを行う関数である。

    Args:
        cfg (Config): 実行時構成 ( `local_root` を参照 ) 。
        rel_dirs (Optional[List[str]]): カレント配下の相対ディレクトリ群。

    Notes:
        - `cfg.local_root` を安全に削除する。
        - `rel_dirs` が与えられた場合, それらも安全に削除する。

    Examples:
        >>> # doctest: +SKIP
        >>> from tests.tests_py._local_types import Config
        >>> cfg = Config(
        ...     ssh_user="user",
        ...     target_user="root",
        ...     hosts_both=["host"],
        ...     host_ubuntu="host",
        ...     host_alma="host",
        ...     ssh_port=22,
        ...     ssh_strict="no",
        ...     ssh_strict_bool=False,
        ...     remote_dest_root="/tmp",
        ...     local_work_root="/tmp",
        ...     local_root="/tmp",
        ...     gm_gather_cmd=["echo"],
        ...     gm_scatter_cmd=["echo"],
        ...     verbose=False,
        ...     parallel=1,
        ... )
        >>> cleanup_local_temps(cfg, rel_dirs=["work"])  # safe_rmtree_abs が best-effort のため
    """
    cwd: str = os.getcwd()
    safe_rmtree_abs(cfg.local_root, ensure_under=cwd)
    for d in (rel_dirs or []):
        abs_path: str = os.path.join(cwd, d)
        safe_rmtree_abs(abs_path, ensure_under=cwd)


def _gm_run_local_argv_public(argv: List[str]) -> Any:
    """`gmwrap` の公開関数を動的に呼び出す薄いラッパである。

    Args:
        argv (List[str]): 実行するコマンドライン。

    Returns:
        Any: `gmwrap` の戻り値オブジェクト。

    Raises:
        RuntimeError: `gmwrap` または `run_local_argv_public` が利用できない場合。

    Examples:
        >>> # doctest: +SKIP
        >>> _gm_run_local_argv_public(["echo", "hello"])
    """
    module: Any
    try:
        module = import_module("tests.tests_py.gmwrap")
    except ModuleNotFoundError as exc:
        raise RuntimeError("gmwrap module is not available.") from exc

    run_func: Any = getattr(module, "run_local_argv_public", None)
    if run_func is None:
        raise RuntimeError("gmwrap.run_local_argv_public is not available.")

    return run_func(argv)


def run_local_with_argv(argv: List[str]) -> LocalRun:
    """公開ローカル実行ヘルパ関数である。

    `gmwrap` の公開関数で実行し, 結果を `LocalRun` として返す。

    Args:
        argv (List[str]): 実行するコマンドライン。

    Returns:
        LocalRun: 実行結果 ( rc/stdout/stderr ) 。

    Raises:
        RuntimeError: `gmwrap` または `run_local_argv_public` が利用できない場合。

    Examples:
        >>> # doctest: +SKIP
        >>> run_local_with_argv(["echo", "hello"])
    """
    res: Any = _gm_run_local_argv_public(argv)
    return LocalRun(int(getattr(res, "rc", 0)), str(getattr(res, "stdout", "")), str(getattr(res, "stderr", "")))
