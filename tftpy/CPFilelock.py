import os
import platform
import time
import errno

class FileLock:
    """ A cross-platform file lock solution. """

    def __init__(self, file_obj):
        self.file_obj = file_obj
        self.fd = file_obj.fileno()
        self.is_windows = platform.system() == 'Windows'
        
    def acquire_shared(self):
        if self.is_windows:
            self._win32_lock(shared=True)
        else:
            self._posix_lock(shared=True)
            

    def acquire_exclusive(self):
        if self.is_windows:
            self._win32_lock(shared=False)
        else:
            self._posix_lock(shared=False)
            

    def release(self):
        if self.is_windows:
            self._win32_unlock()
        else:
            self._posix_unlock()
            
    def _win32_lock(self, shared=True):
        lockfile = f"{self.file_obj.name}.lock"
        while True:
            try:
                fd = os.open(lockfile, 
                           os.O_CREAT | os.O_EXCL | os.O_RDWR)
                os.close(fd)
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise
                time.sleep(0.1)
                

    def _win32_unlock(self):
        try:
            os.unlink(f"{self.file_obj.name}.lock")
        except OSError:
            pass
            
            
    def _posix_lock(self, shared=True):
        import fcntl
        flags = fcntl.LOCK_SH if shared else fcntl.LOCK_EX
        try:
            fcntl.flock(self.fd, flags | fcntl.LOCK_NB)
        except IOError as e:
            raise OSError(f"Failed to acquire lock: {e}")
    
            
    def _posix_unlock(self):
        import fcntl
        try:
            fcntl.flock(self.fd, fcntl.LOCK_UN)
        except IOError as e:
            raise OSError(f"Failed to release lock: {e}")