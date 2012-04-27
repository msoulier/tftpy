"""This module implements virtual file system functionality.  It contains
classes that provide or simulate file system access for TftpServer.

Each VFS class is expected to provide two methods:

`open_read` is called when a TFTP path should be read.  If the path exists, a
file-like object should be returned, otherwise ``None``.

`open_write` is called when a TFTP path should be written to.  If the path can
be written to, a file-like object should be returned, otherwise ``None``.
"""

import os
import os.path
from tftpy.TftpShared import TftpException
from tftpy.TftpShared import log


class TftpVfsStack(object):
    """Allows delegation of VFS requests to other VFS providers, based on the
    request path.  If a request path matches more than one provider, the first
    provider that was registered is tried first, then the second and so on.  The
    search is aborted as soon a provider succeeds."""

    def __init__(self):
        self._file_systems = []

    def mount(self, vfs, base_path='/'):
        """Registers the VFS provider `vfs` for requests prefixed with
        `base_path`."""
        base_path = os.path.normpath(base_path)
        # The base_path should end with a slash.
        if not base_path.endswith('/'):
            base_path += '/'
        self._file_systems.append((vfs, base_path))

    def _matching_vfs_paths(self, path):
        """Generator that searches through the list of VFS providers. For each
        base path that matches `path`, a tuple with the matching VFS provider
        and the sub path (relative to the base path) is yielded."""
        path = os.path.normpath(path)
        if not path.startswith('/'):
            path = '/' + path
        for vfs, base_path in self._file_systems:
            if not path.startswith(base_path):
                continue
            sub_path = path[len(base_path) - 1:]
            yield (vfs, sub_path)

    def open_read(self, path):
        """Returns the file-like object from the first matching file system that
        provides one.  Returns ``None`` if no file was found.
        """
        for vfs, sub_path in self._matching_vfs_paths(path):
            log.debug('attempting path %s, sub path %s' % (path, sub_path))
            fp = vfs.open_read(sub_path)
            if fp is not None:
                return fp
        return None

    def open_write(self, path):
        """Returns the file-like object from the first matching file system that
        provides one.  Returns ``None`` if no file was found or writing isn't
        supported.
        """
        for vfs, sub_path in self._matching_vfs_paths(path):
            log.debug('attempting path %s, sub path %s' % (path, sub_path))
            fp = vfs.open_write(sub_path)
            if fp is not None:
                return fp
        return None

class TftpVfsNative(object):
    """Provides access to the operating system's file system.  Access is
    provided relative to the sub-tree at `root`.

    Allows read and write access.  During write access, any missing
    intermediate directories of the target path are automatically created.  If
    the target file already exists, it is replaced.
    """
    def __init__(self, root):
        self.root = os.path.abspath(root)

        if os.path.exists(self.root):
            log.debug("tftproot %s does exist" % self.root)
            if not os.path.isdir(self.root):
                raise TftpException, "The tftproot must be a directory."
            else:
                log.debug("tftproot %s is a directory" % self.root)
                if os.access(self.root, os.R_OK):
                    log.debug("tftproot %s is readable" % self.root)
                else:
                    raise TftpException, "The tftproot must be readable"
                if os.access(self.root, os.W_OK):
                    log.debug("tftproot %s is writable" % self.root)
                else:
                    log.warning("The tftproot %s is not writable" % self.root)
        else:
            raise TftpException, "The tftproot does not exist."

    def _full_path(self, path):
        """Translates the relative path `path` to the absolute path within the
        native file system and returns that path.  Also makes sure, that the
        resulting path resides within the designated sub-tree.
        """
        # Remove any starting slash
        if path.startswith('/'):
            path = path[1:]
        # Make sure that the path to the file is contained in the server's
        # root directory.
        full_path = os.path.abspath(os.path.join(self.root, path))
        log.debug("full_path is %s" % full_path)
        if full_path.startswith(self.root):
            log.info("requested file is in the server root - good")
        else:
            log.warn("requested file is not within the server root - bad")
            raise TftpException, "bad file path"
        return full_path

    def open_read(self, path):
        """If `path` exists relative to `root`, a file-like object for read
        access is provided.  Otherwise ``None`` is returned.
        Throws :class:``TftpException`` if the requested path tries to exit the
        sub-tree."""
        full_path = self._full_path(path)
        if not os.path.exists(full_path):
            return None
        log.info("Opening file %s for reading" % full_path)
        # Note: Open in binary mode for win32 portability, since win32 blows.
        return open(full_path, "rb")

    def _make_subdirs(self, full_path):
        """The purpose of this method is to, if necessary, create all of the
        subdirectories leading up to the file to the written.
        """
        # Pull off everything below the root.
        subpath = full_path[len(self.root):]
        log.debug("make_subdirs: subpath is %s" % subpath)
        # Split on directory separators, but drop the last one, as it should
        # be the filename.
        dirs = subpath.split(os.sep)[:-1]
        log.debug("dirs is %s" % dirs)
        current = self.root
        for directory in dirs:
            if directory:
                current = os.path.join(current, directory)
                if os.path.isdir(current):
                    log.debug("%s is already an existing directory" % current)
                else:
                    os.mkdir(current, 0700)

    def open_write(self, path):
        """A file-like object for write access is provided.  Any missing
        directories are created automatically.  Throws :class:``TftpException``
        if the requested path tries to exit the sub-tree.
        """
        full_path = self._full_path(path)
        log.info("Opening file %s for writing" % full_path)
        if os.path.exists(full_path):
            # FIXME: correct behavior?
            log.warn("File %s exists already, overwriting..." % full_path)
        # FIXME: I think we should upload to a temp file and not overwrite the
        # existing file until the file is successfully uploaded.
        self._make_subdirs(full_path)
        return open(full_path, "wb")

class TftpVfsReadOnlyDynFileFunc(object):
    """Allows read access to potentially dynamic content provided by the
    call-back `dyn_file_func`.
    """
    def __init__(self, dyn_file_func):
        self.dyn_file_func = dyn_file_func

    def open_read(self, path):
        """Returns the file-like object provided by the call-back, based on
        `path`."""
        return self.dyn_file_func(path)

    def open_write(self, path):
        """Always returns ``None``, because the `dyn_file_func` does not support
        write access."""
        return None

class TftpVfsCompat(TftpVfsStack):
    """Provides a layered VFS which combines a native file-system and, as a
    fall-back in case the file isn't found in the native file-system, an
    optional call-back function for potentially dynamic content.
    """
    def __init__(self, tftproot='/tftpboot', dyn_file_func=None):
        TftpVfsStack.__init__(self)
        self.mount(TftpVfsNative(tftproot), '/')
        if dyn_file_func is not None:
            self.mount(TftpVfsReadOnlyDynFileFunc(dyn_file_func), '/')
