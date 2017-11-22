"""This module provides the needed syscalls for hosts"""

import ctypes
from ctypes.util import find_library
import os

_LIBC = ctypes.CDLL(find_library("c"), use_errno=True)

#pylint: disable=invalid-name

def _raise_OSError(result, *_):
    if result:
        errno = ctypes.get_errno()
        raise OSError(errno, os.strerror(errno))

unshare = _LIBC.unshare
unshare.argtypes = [ctypes.c_int]
unshare.restype = ctypes.c_int
unshare.errcheck = _raise_OSError

CLONE_NEWNS = 0x00020000
CLONE_NEWUTS = 0x04000000

umount2 = _LIBC.umount2
umount2.argtypes = [ctypes.c_char_p, ctypes.c_int]
umount2.restype = ctypes.c_int
umount2.errcheck = _raise_OSError

MNT_DETACH = 2

mount = _LIBC.mount
mount.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_char_p, ctypes.c_ulong,
                  ctypes.c_void_p]
mount.restype = ctypes.c_int
mount.errcheck = _raise_OSError

MS_BIND = 4096
MS_REC = 16384
MS_SLAVE = 1 << 19
