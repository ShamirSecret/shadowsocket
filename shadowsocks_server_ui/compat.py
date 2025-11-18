"""
Python 3.13 and OpenSSL 3.x compatibility fixes
Fixes compatibility issues in the shadowsocks library
"""
import sys
import collections

# Python 3.13+ compatibility fix
if sys.version_info >= (3, 13):
    # Python 3.13 removed collections.MutableMapping
    # Need to import from collections.abc
    try:
        from collections.abc import MutableMapping
        # Add MutableMapping to collections module for backward compatibility
        if not hasattr(collections, 'MutableMapping'):
            collections.MutableMapping = MutableMapping
    except ImportError:
        # If collections.abc is not available, use typing as fallback
        try:
            from typing import MutableMapping
            collections.MutableMapping = MutableMapping
        except ImportError:
            pass

# OpenSSL 3.x compatibility fix
# EVP_CIPHER_CTX_cleanup was removed in OpenSSL 1.1.0+, should use EVP_CIPHER_CTX_reset
# This method will be automatically applied when shadowsocks is imported, as shadowsocks reloads libcrypto
def _patch_openssl_compat():
    """Patch OpenSSL compatibility issues (macOS only, Windows/Linux handled by shadowsocks library)"""
    import platform
    if platform.system() != 'Darwin':  # Only execute on macOS
        return False
    
    try:
        import ctypes
        from ctypes import c_void_p
        
        # macOS typically uses system OpenSSL
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
            # Check if EVP_CIPHER_CTX_reset exists (OpenSSL 1.1.0+)
            if hasattr(libcrypto, 'EVP_CIPHER_CTX_reset'):
                # If reset exists but cleanup doesn't, create cleanup as alias for reset
                if not hasattr(libcrypto, 'EVP_CIPHER_CTX_cleanup'):
                    libcrypto.EVP_CIPHER_CTX_cleanup = libcrypto.EVP_CIPHER_CTX_reset
                    libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,)
                    libcrypto.EVP_CIPHER_CTX_cleanup.restype = ctypes.c_int
                    return True
    except Exception:
        pass
    return False

# Execute fix immediately (macOS only)
_patch_openssl_compat()

# Fix immediately after shadowsocks import (because shadowsocks reloads libcrypto)
def _patch_shadowsocks_openssl():
    """Patch shadowsocks OpenSSL module"""
    try:
        import shadowsocks.crypto.openssl as openssl_module
        import ctypes
        from ctypes import c_void_p, c_char_p, c_int
        
        # Save original load_openssl function
        original_load_openssl = openssl_module.load_openssl
        
        def patched_load_openssl():
            """Patched load_openssl, create cleanup alias before setting argtypes"""
            # Import shadowsocks.crypto.util (lazy import to avoid circular dependency)
            from shadowsocks.crypto import util
            
            # Load libcrypto (using shadowsocks original logic)
            libcrypto = util.find_library(('crypto', 'eay32'),
                                          'EVP_get_cipherbyname',
                                          'libcrypto')
            if libcrypto is None:
                raise Exception('libcrypto(OpenSSL) not found')
            
            # Before setting argtypes, check and create cleanup alias
            if hasattr(libcrypto, 'EVP_CIPHER_CTX_reset'):
                if not hasattr(libcrypto, 'EVP_CIPHER_CTX_cleanup'):
                    # Create cleanup as alias for reset
                    libcrypto.EVP_CIPHER_CTX_cleanup = libcrypto.EVP_CIPHER_CTX_reset
                    print("[COMPAT] OpenSSL compatibility fix applied: EVP_CIPHER_CTX_cleanup -> EVP_CIPHER_CTX_reset")
            
            # Continue with original setup process
            libcrypto.EVP_get_cipherbyname.restype = c_void_p
            libcrypto.EVP_CIPHER_CTX_new.restype = c_void_p
            
            libcrypto.EVP_CipherInit_ex.argtypes = (c_void_p, c_void_p, c_char_p,
                                                    c_char_p, c_char_p, c_int)
            
            libcrypto.EVP_CipherUpdate.argtypes = (c_void_p, c_void_p, c_void_p,
                                                   c_char_p, c_int)
            
            # Now we can safely set cleanup's argtypes (because we've created the alias)
            libcrypto.EVP_CIPHER_CTX_cleanup.argtypes = (c_void_p,)
            libcrypto.EVP_CIPHER_CTX_free.argtypes = (c_void_p,)
            
            if hasattr(libcrypto, 'OpenSSL_add_all_ciphers'):
                libcrypto.OpenSSL_add_all_ciphers()
            
            # Create buf (global variable in shadowsocks original code)
            from ctypes import create_string_buffer
            buf_size = 2048
            buf = create_string_buffer(buf_size)
            
            # Update module global variables
            openssl_module.loaded = True
            openssl_module.libcrypto = libcrypto
            openssl_module.buf = buf
        
        # Replace load_openssl function
        openssl_module.load_openssl = patched_load_openssl
        
        return True
    except Exception as e:
        print(f"[COMPAT] Fix failed: {e}")
        import traceback
        traceback.print_exc()
        pass
    return False

# Try to fix immediately (will be called after shadowsocks import)
# This function will be called when shadowsocks is imported

