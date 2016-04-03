try:
    import numpy as np

    def isnumpy(val):
        """
        :return: True if val is a numpy object (regarldess of its shape and dimension)
        """
        return type(val).__module__ == np.__name__
except ImportError as ierr:
    def isnumpy(val):
        raise ierr

import shutil
import sys
import datetime as dt
import re
import errno
from os import strerror
import os


def ispy2():
    """
    :return: True if the current python version is 2
    """
    return 2 <= sys.version_info[0] < 3


def ispy3():
    """
    :return: True if the current python version is 3
    """
    return 3 <= sys.version_info[0] < 4


def isstr(val):
    """
    Returns if val is a string. Python 2-3 compatible function
    :return: True if val denotes a string (`basestring` in python < 3 and `str` otherwise)
    """
    if ispy2():
        return isinstance(val, basestring)
    else:
        return isinstance(val, str)


def isunicode(val):
    """
    Returns if val is a unicode string. Python 2-3 compatible function (Note that in Python 3 this
    method is equivalent to `isstr`)
    :return: True if val denotes a unicode string (`unicode` in python < 3 and `str` otherwise)
    """
    if ispy2():
        return isinstance(val, unicode)
    else:
        return isinstance(val, str)


def isbytes(val):
    """
    Returns if val is a bytes object. Python 2-3 compatible function (Note that in Python 2 this
    method is equivalent to `isstr`)
    :return: True if val denotes a byte string (`bytes` in both python 2 and 3)
    """
    return isinstance(val, bytes)


def tobytes(unicodestr, encoding='utf-8'):
    """
        Converts unicodestr to a byte string, with the given encoding. Python 2-3 compatible.
        Remember that
            ======= ============ ===============
                    byte strings unicode strings
            ======= ============ ===============
            Python2 "abc" [*]    u"abc"
            Python3 b"abc"       "abc" [*]
            ======= ============ =================

         [*]=default string object for the given python version

        :param unicodestr: a unicode string. If already byte string, this method returns it
            immediately
        :param encoding: the encoding used. Defaults to 'utf-8' when missing
        :return: a bytes class (same as str in python2) resulting from encoding unicodestr
    """
    if isbytes(unicodestr):
        return unicodestr
    return unicodestr.encode(encoding)


def tounicode(bytestr, decoding='utf-8'):
    """
        Converts bytestr to unicode string, with the given decoding. Python 2-3 compatible.
        Remember that
            ======= ============ ===============
                    byte strings unicode strings
            ======= ============ ===============
            Python2 "abc" [*]    u"abc"
            Python3 b"abc"       "abc" [*]
            ======= ============ =================

         [*]=default string object for the given python version

        :param bytestr: a bytes object (same as str in python2). If unicode string,
            this method returns it immediately
        :param decoding: the decoding used. Defaults to 'utf-8' when missing
        :return: a string (unicode string in python2) resulting from decoding bytestr
    """
    if isstr(bytestr):
        return bytestr
    return bytestr.decode(decoding)


def isre(val):
    """Returns true if val is a compiled regular expression"""
    return isinstance(val, re.compile(".").__class__)


def estremttime(time_in_seconds, iteration_number, total_iterations, approx_to_seconds=True):
    remaining_seconds = (total_iterations - iteration_number) * (time_in_seconds / iteration_number)
    dttd = dt.timedelta(seconds=remaining_seconds)
    if approx_to_seconds:
        if dttd.microseconds >= 500000:
            dttd = dt.timedelta(days=dttd.days, seconds=dttd.seconds+1)  # FIXME: ass check!!
        else:
            dttd = dt.timedelta(days=dttd.days, seconds=dttd.seconds)
    return dttd


def regex(arg, retval_if_none=re.compile(".*")):
    """Returns a regular expression built as follows:
        - if arg is already a regular expression, returns it
        - if arg is None, returns retval_if_none, which by default is ".*" (matches everything)
        - Returns the regular expression escaping str(arg) EXCEPT "?" and "*" which will be
        converted to their regexp equivalent (thus arg might be a string with wildcards, as in many
        string processing arguments)
        :return: A regular expression from arg
    """
    if isre(arg):
        return arg

    if arg is None:
        return retval_if_none

    return re.compile(re.escape(str(arg)).replace("\\?", ".").replace("\\*", ".*"))


def oserr_(errnotype, msg=''):  # FIXME: check msg
    """
        Returns an OSError raised by the file argument.
        :param errnotype: the error type, see errno package for details (e.g., errno.ENOENT)
        :param file: the file
    """
    return OSError(strerror(errnotype) + " " + str(msg))


def _ensure(filepath, mode, mkdirs=False, errmsgfunc=None):
    """checks for filepath according to mode, raises an OSError if check is false
    :param mode: either 'd', 'dir', 'r', 'fr', 'w', 'fw' (case insensitive). Checks if file_name is,
        respectively:
            - 'd' or 'dir': an existing directory
            - 'fr', 'r': file for reading (an existing file)
            - 'fw', 'w': file for writing (a file whose dirname exists)
    :param mkdirs: boolean indicating, when mode is 'file_w' or 'dir', whether to attempt to
        create the necessary path. Ignored when mode is 'r'
    :param errmsgfunc: None by default, it indicates a custom function which returns the string
        error to be displayed in case of OSError's. Usually there's no need to implement a custom
        one, but in case the function accepts two arguments, filepath and mode (the latter is
        either 'r', 'w' or 'd') and returns the relative error message as string
    :raises: SyntaxError if some argument is invalid, or OSError if filepath is not valid according
        to mode and mkdirs
    """
    # to see OsError error numbers, see here
    # https://docs.python.org/2/library/errno.html#module-errno
    # Here we use two:
    # errno.EINVAL ' invalid argument'
    # errno.errno.ENOENT 'no such file or directory'
    if not isstr(filepath) or not filepath:
        raise SyntaxError("{0}: '{1}' ({2})".format(strerror(errno.EINVAL),
                                                    str(filepath),
                                                    str(type(filepath))
                                                    )
                          )

    keys = ('fw', 'w', 'fr', 'r', 'd', 'dir')

    # normalize the mode argument:
    if mode.lower() in keys[2:4]:
        mode = 'r'
    elif mode.lower() in keys[:2]:
        mode = 'w'
    elif mode.lower() in keys[4:]:
        mode = 'd'
    else:
        raise SyntaxError('mode argument must be in ' + str(keys))

    if errmsgfunc is None:  # build custom errormsgfunc if None
        def errmsgfunc(filepath, mode):
            if mode == 'w' or (mode == 'r' and not os.path.isdir(os.path.dirname(filepath))):
                return "{0}: '{1}' ({2}: '{3}')".format(strerror(errno.ENOENT),
                                                        os.path.basename(filepath),
                                                        strerror(errno.ENOTDIR),
                                                        os.path.dirname(filepath)
                                                        )
            elif mode == 'd':
                return "{0}: '{1}'".format(strerror(errno.ENOTDIR), filepath)
            elif mode == 'r':
                return "{0}: '{1}'".format(strerror(errno.ENOENT), filepath)

    if mode == 'w':
        to_check = os.path.dirname(filepath)
        func = os.path.isdir
        mkdir_ = mkdirs
    elif mode == 'd':
        to_check = filepath
        func = os.path.isdir
        mkdir_ = mkdirs
    else:  # mode == 'r':
        to_check = filepath
        func = os.path.isfile
        mkdir_ = False

    exists_ = func(to_check)
    if not func(to_check):
        if mkdir_:
            os.makedirs(to_check)
            exists_ = func(to_check)

    if not exists_:
        raise OSError(errmsgfunc(filepath, mode))


def load_module(filepath, name=None):
    """
        Loads a python module indicated by filepath, returns an object where global variables
        and classes can be accessed as attributes
        See: http://stackoverflow.com/questions/67631/how-to-import-a-module-given-the-full-path
        :param filepath: the path of the module
        :param name: defaults to None (implying that the filepath basename, without extension, will
            be taken) and it's only used to set the .__name__ of the returned module. It doesn't
            affect loading
    """
    if name is None:
        name = os.path.splitext(os.path.basename(filepath))[0]
    # name only sets the .__name__ of the returned module. it doesn't effect loading

    if ispy2():  # python 2
        import imp
        return imp.load_source(name, filepath)
    elif ispy3() and sys.version_info[1] >= 5:  # Python 3.5+:
        import importlib.util  # @UnresolvedImport
        spec = importlib.util.spec_from_file_location(name, filepath)
        modul = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(modul)
        return modul
    else:  # actually, for Python 3.3 and 3.4, but we assume is the case also for 3.2 3.1 etcetera
        from importlib.machinery import SourceFileLoader  # @UnresolvedImport
        return SourceFileLoader(name, filepath).load_module()
        # (Although this has been deprecated in Python 3.4.)

    # raise SystemError("unsupported python version: "+ str(sys.version_info))


def ensurefiler(filepath):
    """Checks that filepath denotes a valid file, raises an OSError if not.
    In many cases it's more convenient to simply call the equivalent
        os.path.isfile(filepath)
    except that this function raises a meaningful OSError in case of non-existing parent directory
    (hopefully saving useless browsing time)
    :param filepath: a file path
    :type filepath: string
    :return: nothing
    :raises: OSError if filepath does not denote an existing file
    """
    _ensure(filepath, 'r', False)  # last arg ignored, set to False for safety


def ensurefilew(filepath, mkdirs=True):
    """Checks that filepath denotes a valid file for writing, i.e., if its parent directory D
    exists. Raises an OSError if not.
    :param filepath: a file path
    :type filepath: string
    :param mkdirs: True by default, if D does not exists will try to build it via mkdirs before
        re-checking again its existence
    :return: nothing
    :raises: OSError if filepath directory does not denote an existing directory
    """
    _ensure(filepath, 'w', mkdirs)


def ensuredir(filepath, mkdirs=True):
    """Checks that filepath denotes a valid existing directory. Raises an OSError if not.
    In many cases it's more convenient to simply call the equivalent
        os.path.isdir(filepath)
    except that this function has the optional mkdirs argument which will try to build filepath if
    not existing
    :param filepath: a file path
    :type filepath: string
    :param mkdirs: True by default, if D does not exists will try to build it via mkdirs before
        re-checking again its existence
    :return: nothing
    :raises: OSError if filepath directory does not denote an existing directory
    """
    _ensure(filepath, 'd', mkdirs)


def rsync(source, dest, update=True, modify_window=1):
    """
    Copies source to dest emulating a simple rsync unix command
    :param source: the source file. If it does not exist, an OSError is raised
    :param dest: the destination file. According to shutil.copy2, if dest is a directory then
    the destination file will be os.path.join(dest, os.basename(source)
    :param update: If True (the default), the copy will be skipped for a file which exists on
        the destination and has a modified time that is newer than the source file.
        (If an existing destination file has a modification time equal to the source file's,
        it will be updated if the sizes are different.)
    :param modify_window: (1 by default). This argument is ignored if update is False. Otherwise,
        when comparing two timestamps, this function treats the timestamps as being equal if they
        differ by no more than the modify-window value. This is normally 0 (for an exact match),
        but it defaults to 1 as (quoting from rsync docs):
        "In particular, when transferring to or from an MS Windows FAT filesystem
         (which represents times with a 2-second resolution), --modify-window=1 is useful
         (allowing times to differ by up to 1 second).
        If update is a float, or any object parsable to float (e.g. "4.5"), it will be rounded to
        integer
    :return: the tuple (destination_file, copied), where the first item is the destination file
    (which might not be the dest argument, if the latter is a directory) and a boolean denoting if
    the copy has been performed. Note that it is not guaranteed that the returned file exists (the
    user has to check for it)
    """
    if not os.path.isfile(source):
        raise OSError(strerror(errno.ENOENT) + ": '" + source + "'")

    if os.path.isdir(dest):
        dest = os.path.join(dest, os.path.basename(source))

    if update and os.path.isfile(dest):
        st1, st2 = os.stat(source), os.stat(dest)
        # st# = (mode, ino, dev, nlink, uid, gid, size, atime, mtime, ctime)
        mtime_src, mtime_dest = st1[8], st2[8]
        # ignore if
        # 1) dest is newer than source OR
        # 2) times are equal (i.e. within the specified interval) AND sizes are equal (sizes are
        # the stats elements at index 6)
        if mtime_dest > mtime_src + update or \
                (mtime_src - update <= mtime_dest <= mtime_src + update and st1[6] == st2[6]):
            return dest, False

    shutil.copy2(source, dest)
    return dest, True
