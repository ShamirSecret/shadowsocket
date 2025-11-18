"""
Python 3.13 兼容性修复
修复 shadowsocks 库中 collections.MutableMapping 的问题
"""
import sys
import collections

# Python 3.13+ 兼容性修复
if sys.version_info >= (3, 13):
    # Python 3.13 移除了 collections.MutableMapping
    # 需要从 collections.abc 导入
    try:
        from collections.abc import MutableMapping
        # 将 MutableMapping 添加到 collections 模块，保持向后兼容
        if not hasattr(collections, 'MutableMapping'):
            collections.MutableMapping = MutableMapping
    except ImportError:
        # 如果 collections.abc 也不可用，使用 typing 的替代方案
        try:
            from typing import MutableMapping
            collections.MutableMapping = MutableMapping
        except ImportError:
            pass

