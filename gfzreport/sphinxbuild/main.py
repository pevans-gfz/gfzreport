#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Created on Mar 14, 2016

@author: riccardo
'''

import sys
import os
import subprocess
from sphinx import build_main as sphinx_build_main
# from reportbuild.core.utils import ensurefiler
import click

_DEFAULT_BUILD_TYPE = 'latex'


def pdflatex(texfile, texfolder=None, numruns=1):
    """
    Runs pdflatex with the given texfile as input
    :param texfile the input tex file
    :param texfolder: the texfile location directory. The pdflatex process will be run inside it.
        If None (default if missing), then it is texfile directory. Otherwise, texfile denotes the
        file name which must exist inside texfolder
    :raise: OsError in case of file not founds, pdflatex not installed etcetera.
    """
    texexists = False
    if texfolder is None:
        texexists = os.path.isfile(texfile)
        texfolder = os.path.dirname(texfile)
        texfile = os.path.basename(texfile)
    else:
        texexists = os.path.isfile(os.path.join(texfolder, texfile))

    if not texexists:
        raise OSError(os.errno.ENOENT, "'%s' does not exist")

    warn_printed = False  # print warning once
    # seems that we need to call subprocess.call according to this post:
    # http://stackoverflow.com/questions/4230926/pdflatex-in-a-python-subprocess-on-mac
    # for interaction options, see here:
    # http://tex.stackexchange.com/questions/91592/where-to-find-official-and-extended-documentation-for-tex-latexs-commandlin
    popenargs = ['pdflatex', "-interaction=nonstopmode", texfile]
    kwargs = dict(cwd=texfolder, shell=False)
    try:
        for _ in xrange(numruns):
            ret = subprocess.call(popenargs, **kwargs)
            if ret != 0 and not warn_printed:
                warn_printed = True
                sys.stdout.write(("WARNING: pdflatex returned an exit "
                                  "status {0:d} (0=Ok)").format(ret))
    except OSError as oserr:
        appendix = " (is pdflatex installed?)" if oserr.errno == os.errno.ENOENT else ""
        # copied from sphinx, we want to preserve the same way of handling errors:
        raise OSError(oserr.errno, ("Unable to run 'pdflatex {0}': "
                                    "{1}{2}\n").format(texfile, os.strerror(oserr.errno), appendix))

    return ret


def get_tex_files(path):
    """Returns a dict of tex files directly under 'path' (no recursive search). The dict
    keys are the tex files absolute path, the values are the relative last modified timestamps"""
    ret = {}
    if os.path.isdir(path):
        for file_ in os.listdir(path):
            if ".dontcompile." in file_:
                continue
            absfile = os.path.abspath(os.path.join(path, file_))
            if os.path.splitext(file_)[1].lower() == '.tex':
                ret[absfile] = os.stat(absfile)[8]

    return ret


def run(sourcedir, outdir, build=_DEFAULT_BUILD_TYPE, *other_sphinxbuild_options):
    """Runs sphinx-build
    :param sourcedir: the source input directory
    :param outdir: the output build directory
    :param build: the build type (string). Currently supported are 'latex' (default), 'html', 'pdf'
    If 'pdf', then pdflatex and relative libraries must be installed
    :param other_sphinxbuild_options: positional command line argument to be forwarded to
    sphinx-build
    :raise: OsError (returned from pdflatex) or any exception raised by sphinx build (FIXME: check)
    Example
    -------

    run('/me/my/path', '/me/another/path', 'pdf', '-E')
    """
    old_tex_files = {}
    do_pdf = build == 'pdf'
    if do_pdf:
        build = 'latex'
        old_tex_files = get_tex_files(outdir)

    # call sphinx:
    argv = ["", sourcedir, outdir, "-b", build] + list(other_sphinxbuild_options)
    res = sphinx_build_main(argv)

    if res == 0 and do_pdf:
        new_tex_files = get_tex_files(outdir)
        tex_files = []  # real list of tex files to pdf-process
        for fileabspath, file_mtime in new_tex_files.iteritems():
            if fileabspath not in old_tex_files or file_mtime > old_tex_files[fileabspath]:
                tex_files.append(fileabspath)

        for fileabspath in tex_files:
            res += pdflatex(fileabspath, None, 2)

    return 1 if res else 0


# use a commandline ability to forward to sphinx-build with some pre- and post-processing on
# the --build argument:

# as when we provide --sphinxhelp we should not check for sourcedir and outdir existence
# we cannot set the nargs=1 and required=True in @click.argument, so we implement this function
# that behaves as nargs=1+required=True
def check_dirs(ctx, param, value):
    if not value and "sphinxhelp" not in ctx.params:
        raise click.BadParameter("Missing argument", ctx=ctx, param=param)
    return value


@click.command(context_settings=dict(ignore_unknown_options=True,),
               options_metavar='[options]')
@click.argument('sourcedir', nargs=1, required=False, callback=check_dirs,
                metavar='sourcedir')  # @IgnorePep8
@click.argument('outdir', nargs=1, required=False, callback=check_dirs, metavar='outdir')
@click.option('-b', '--build',
              help=('builder to use. Default is ' + _DEFAULT_BUILD_TYPE + ' (in ' +
                    'sphinx-build is html). You can also type pdf: if this program is correctly ' +
                    'installed (with all latex libs) then `sphinx-build -b latex ...` is first ' +
                    'executed and then pdflatex is run on all .tex files in outdir which '
                    'were modified by sphinx-build (by checking their last modified time prior '
                    'and after sphinx-build execution). Note that this program has been '
                    'currently tested only for sphinx builds generating a single .tex file '
                    'in outdir'),
              default=_DEFAULT_BUILD_TYPE, type=click.Choice(['html', 'pdf', _DEFAULT_BUILD_TYPE]))
@click.argument('other_sphinxbuild_options', nargs=-1, type=click.UNPROCESSED,
                metavar='[other_sphinxbuild_options]')
@click.option('--sphinxhelp', is_flag=True, default=False, help='print out the sphinx-build help '
              'to know which options (except -b, --build) or arguments (except sourcedir, outdir) '
              'can be passed in [other_sphinxbuild_options]')
def main(sourcedir, outdir, build, other_sphinxbuild_options, sphinxhelp):
    """A wrapper around sphinx-build. Note: if build is 'pdf', all tex files in `outdir`
    with ".tex" extension will be checked before execution, and later compiled with `pdflatex`
    if they are new or modified in between the execution. This usually works fine but might compile
    separately latex additional files provided in conf.py (at least the first build, as they will be
    seen as new). To avoid this, put the string ".dontcompile." in the file name
    """
    if sphinxhelp:
        sphinx_build_main(["", "--help"])
        sys.exit(0)

    # for info see:
    # sphinx/cmdline.py, or
    # http://www.sphinx-doc.org/en/1.5.1/man/sphinx-build.html
    try:
        return run(sourcedir, outdir, build, *list(other_sphinxbuild_options))
    except (ValueError, OSError) as exc:  # FIXME: ValueError raised where?
        sys.stderr.write("%s: %s" % (exc.__class__.__name__, str(exc)))
        return 1

if __name__ == '__main__':
    sys.exit(main())  # pylint:disable=no-value-for-parameter
