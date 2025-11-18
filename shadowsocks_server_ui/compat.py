"""
Python 3.13 和 OpenSSL 3.x 兼容性修复
修复 shadowsocks 库中的兼容性问题
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

# OpenSSL 3.x 兼容性修复
# EVP_CIPHER_CTX_cleanup 在 OpenSSL 1.1.0+ 中被移除，应该使用 EVP_CIPHER_CTX_reset
# 这个方法会在 shadowsocks 导入时自动应用，因为 shadowsocks 会重新加载 libcrypto
def _patch_openssl_compat():
    """修补 OpenSSL 兼容性问题（仅 macOS，Windows/Linux 由 shadowsocks 库处理）"""
    import platform
    if platform.system() != 'Darwin':  # 只在 macOS 上执行
        return False
    
    try:
        import ctypes
        from ctypes import c_void_p
        
        # macOS 上通常使用系统的 OpenSSL
        libcrypto_paths = [
            '/opt/homebrew/lib/libcrypto.dylib',  # Homebrew on Apple Silicon
            '/usr/local/lib/libcrypto.dylib',      # Homebrew on Intel
            '/usr/lib/libcrypto.dylib',           # System OpenSSL
        ]
        
        libcrypto = None
        for path in libcrypto_paths:
            try:
                libcrypto = ctypes.CDLL(path)
                break
            except OSError:
                continue
        
        if libcrypto:
            # 检查是否有 EVP_CIPHER_CTX_reset（OpenSSL 1.1.0+）
            if hasattr(libcrypto, 'EVP_CIPHER_CTX_reset'):
                # 如果存在 reset，但没有 cleanup，则创建 cleanup 作为 reset 的别名
                if not hasattr(libcrypto, 'EVP_CIPHER_CTX_cleanup'):
                    libcrypto.EVP_CIPHER_CTX_cleanup = libcrypto.EVP_CIPHER_CTX_reset
                    libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,)
                    libcrypto.EVP_CIPHER_CTX_cleanup.restype = ctypes.c_int
                    return True
    except Exception:
        pass
    return False

# 立即执行修复（仅在 macOS 上）
_patch_openssl_compat()

# 在 shadowsocks 导入后立即修复（因为 shadowsocks 会重新加载 libcrypto）
def _patch_shadowsocks_openssl():
    """修补 shadowsocks 的 OpenSSL 模块"""
    try:
        import shadowsocks.crypto.openssl as openssl_module
        import ctypes
        from ctypes import c_void_p, c_char_p, c_int
        
        # 保存原始的 load_openssl 函数
        original_load_openssl = openssl_module.load_openssl
        
        def patched_load_openssl():
            """修补后的 load_openssl，在设置 argtypes 之前先创建 cleanup 别名"""
            # 导入 shadowsocks.crypto.util（延迟导入避免循环）
            from shadowsocks.crypto import util
            
            # 加载 libcrypto（使用 shadowsocks 的原始逻辑）
            libcrypto = util.find_library(('crypto', 'eay32'),
                                          'EVP_get_cipherbyname',
                                          'libcrypto')
            if libcrypto is None:
                raise Exception('libcrypto(OpenSSL) not found')
            
            # 在设置 argtypes 之前，先检查并创建 cleanup 别名
            if hasattr(libcrypto, 'EVP_CIPHER_CTX_reset'):
                if not hasattr(libcrypto, 'EVP_CIPHER_CTX_cleanup'):
                    # 创建 cleanup 作为 reset 的别名
                    libcrypto.EVP_CIPHER_CTX_cleanup = libcrypto.EVP_CIPHER_CTX_reset
                    print("[COMPAT] OpenSSL 兼容性修复已应用: EVP_CIPHER_CTX_cleanup -> EVP_CIPHER_CTX_reset")
            
            # 继续原始的设置流程
            libcrypto.EVP_get_cipherbyname.restype = c_void_p
            libcrypto.EVP_CIPHER_CTX_new.restype = c_void_p
            
            libcrypto.EVP_CipherInit_ex.argtypes = (c_void_p, c_void_p, c_char_p,
                                                    c_char_p, c_char_p, c_int)
            
            libcrypto.EVP_CipherUpdate.argtypes = (c_void_p, c_void_p, c_void_p,
                                                   c_char_p, c_int)
            
            # 现在可以安全地设置 cleanup 的 argtypes（因为我们已经创建了别名）
            libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,)
            libcrypto.EVP_CIPHER_CTX_free.argtypes = (c_void_p,)
            
            if hasattr(libcrypto, 'OpenSSL_add_all_ciphers'):
                libcrypto.OpenSSL_add_all_ciphers()
            
            # 创建 buf（shadowsocks 原始代码中的全局变量）
            from ctypes import create_string_buffer
            buf_size = 2048
            buf = create_string_buffer(buf_size)
            
            # 更新模块的全局变量
            openssl_module.loaded = True
            openssl_module.libcrypto = libcrypto
            openssl_module.buf = buf
        
        # 替换 load_openssl 函数
        openssl_module.load_openssl = patched_load_openssl
        
        return True
    except Exception as e:
        print(f"[COMPAT] 修复失败: {e}")
        import traceback
        traceback.print_exc()
        pass
    return False

# 立即尝试修复（会在 shadowsocks 导入后调用）
# 这个函数会在 shadowsocks 导入时被调用

