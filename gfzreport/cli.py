#!/usr/bin/env ptatioython
# -*- coding: utf-8 -*-
'''
Created on Oct 23, 2017
@author: riccardo
'''
import click
import sys

from sphinx import build_main as sphinx_build_main
from gfzreport.sphinxbuild.map import parse_margins
from gfzreport.templates.network import run as networktemplate_run, Templater as NetworkTemplater
from gfzreport.sphinxbuild import run as sphinxbuild_run
from gfzreport.sphinxbuild import _DEFAULT_BUILD_TYPE
import os
from click.decorators import _make_command, command
from click.core import Command

# define terminal width for help (bigger)
TERMINAL_HELP_WIDTH = 120


# define a custom option with show defaults = True
def option(*a, **v):
    try:
        return click.option(*a, show_default=True, **v)
    except TypeError:  # show_default already defined? try normally:
        return click.option(*a, **v)


@click.group()
def main():
    """gfzreport is a program to generate reports and report templates for the
    Helmholtz-Centre Potsdam - GFZ German Research Centre for Geosciences
    """
    pass


# as when we provide --sphinxhelp we should not check for sourcedir and outdir existence
# we cannot set the nargs=1 and required=True in @click.argument, so we implement this function
# that behaves as nargs=1+required=True
def check_dirs(ctx, param, value):
    if not value and "sphinxhelp" not in ctx.params:
        raise click.BadParameter("Missing argument", ctx=ctx, param=param)
    return value


@main.command(context_settings=dict(ignore_unknown_options=True,
                                    max_content_width=TERMINAL_HELP_WIDTH),
              options_metavar='[options]')
@click.argument('sourcedir', nargs=1, required=False, callback=check_dirs,
                metavar='sourcedir')  # @IgnorePep8
@click.argument('outdir', nargs=1, required=False, callback=check_dirs, metavar='outdir')
@option('-b', '--build',
        help=('builder to use. You can also type pdf: if this program is correctly '
              'installed (with all latex libs) then `sphinx-build -b latex ...` is first '
              'executed and then pdflatex is run on all .tex files in outdir which '
              'did not exist before (or whose last-modified time changed during) this '
              'program execution. This usually works fine but might compile also latex '
              'additional files provided in conf.py, at least after the first build, as they '
              'will be seen as new: to avoid this, put the string ".dontcompile." in the '
              '.tex file names. Note that this program has been currently tested '
              'only for sphinx builds generating a single .tex file in outdir'),
        default=_DEFAULT_BUILD_TYPE, type=click.Choice(['html', 'pdf', _DEFAULT_BUILD_TYPE]))
@click.argument('other_sphinxbuild_options', nargs=-1, type=click.UNPROCESSED,
                metavar='[other_sphinxbuild_options]')
@option('--sphinxhelp', is_flag=True, default=False,
        help='print out the sphinx-build help '
             'to know which options (except -b, --build) or arguments (except sourcedir, outdir) '
             'can be passed in [other_sphinxbuild_options]')
def build(sourcedir, outdir, build, other_sphinxbuild_options, sphinxhelp):
    """A wrapper around sphinx-build"""
    if sphinxhelp:
        sphinx_build_main(["", "--help"])
        return 0

    # for info see:
    # sphinx/cmdline.py, or
    # http://www.sphinx-doc.org/en/1.5.1/man/sphinx-build.html
    sys.exit(sphinxbuild_run(sourcedir, outdir, build, *list(other_sphinxbuild_options)))


@main.group(short_help="creates templates reports. Type template --help for help")
def template():
    pass


def _validate_margins(ctx, param, value):
    """Does a check on the outdir: when it's None, it returns the dir specified in
    ```reportgen.network.www.config.SOURCE_PATH```
    """
    try:
        return parse_margins(value)
    except:
        raise click.BadParameter("invalid value for '%s': '%s'"
                                 % (param.human_readable_name, str(value)))


def templatecommand(*args, **kwargs):

    doc_append = """
-----------------------------------------

    The directory tree that will be created will look like the following:

    \b
    dest_dir:             destination directory. It can be out_path or
                          a dub-directory depending on the command
                          invoked (see command help)
    \b
        conf_files:       directory with sphinx
                          additional files (see conf.py)

    \b
        conf.py:          Sphinx configuration file

    \b
        report.rst:       ReStructuredText report. The file name
                          might change depending on the value of
                          'master_doc' in conf.py

    \b
        data:             data files directory. It can have sub-directories or
                          be empty depending on the command invoked
"""
    _destpath = option('-o', '--out_path', required=True,  # callback=validate_outdir,
                       help=("The output path. The destination directory (which depends on the "
                             "command invoked, it is usually a sub-directory of out_path)"
                             "must *not* exist if -c is missing (the default), or the program "
                             "will exit. If -c is given, on the other hand, it must exist"))
    _conffilesonly = option("-c", "--conffiles_only", is_flag=True, default=False,
                            help=("Copy (remove and copy) only sphinx configuration files "
                                  "(conf dir + conf.py). Useful for updating an already created "
                                  "directory without changing the .rst report and its "
                                  "data files, if any. If given, all options related to data files "
                                  "and the report .rst creation (e.g., -m) will be skipped"))
    _mvdatafiles = option("-m", "--mv_datafiles", is_flag=True, default=False,
                          help=("Move all specified data files (-n and -i options) instead of "
                                "copying them (default False when missing)"))
    _noprompt = option("--noprompt", is_flag=True, default=False,
                       help=("Do not ask before proceeding. The default, when this flag is "
                             "missing, is False (always ask before writing)"))

    # copied from click.core.Group.command:
    def decorator(f):
        # add default options (common to all templates clis):
        f = _destpath(_conffilesonly(_mvdatafiles(_noprompt(f))))
        cmd = command(*args, **kwargs)(f)
        # add custom help:
        cmd.help += "\n%s" % doc_append
        template.add_command(cmd)
        return cmd

    return decorator


@templatecommand(short_help="Generates the report folder for the given network and year",
                 context_settings=dict(max_content_width=TERMINAL_HELP_WIDTH))
@option("-n", '--network', required=True, help="the network name, e.g.: ZE")
@option("-s", '--start_after', required=True, help="the start year, e.g.: 2012")  # , type=int)
@option('-a', '--area_margins', default='0.5',  callback=_validate_margins,
        help=("The search margins (in degrees) relative to the bounding box calculated "
              "from the network station locations. The new square area (bbox + margins) "
              "will be used to search for non-network stations to be displayed on the "
              "map and will set the map image margins (later editable in the .rst file). "
              "Specify 1 to 4 values separated by commas (no spaces allowed) denoting "
              "top,left,bottom,right (4 values), "
              "top,left_and_right, bottom (3 values), "
              "top_and_bottom, left_and_right (2 values), "
              "or a single value that will be applied to all directions. "
              "Negative values will shrink the box, positive will "
              "expand it"))
@option('-p', '--noise_pdf', default=None, multiple=True,
        help=("The path (directory, file, glob pattern) of the "
              "Noise Probability Density function images. "
              "This option can be given multiple times. All images will be collected "
              "from the given option(s) and displayed on a grid "
              "(rows=stations, columns=channels). "
              "Files should be preferably have extension .png or .jpeg. "
              "The file names, after removing the extension, must be in the format: "
              "[station]-[channel] "
              "or, for stations with the same [station] name: "
              "[station]-[channel]-1, [station]-[channel]-2, ... "
              "where 1 is associated to the station with the oldest start-time, 2 "
              "is associated to th station with the second oldest start-time, and so on. "
              "Actually, '-' can be any sequence of one or more alphanumeric characters. "
              "Example: AM01.HHZ, AM01__BH1, MSM01_HHN_1, MSM01_HHN-2"))
@option('-i', '--inst_uptimes', default=None, multiple=True,
        help=('The path (directory, file, glob pattern) '
              'of the instrument uptimes image(s). If multiple files '
              'are provided, the images will be displayed in a grid of one column '
              'sorted alphabetically by name'))
@option('-nm', '--network_station_marker', default="^", type=str,
        help=('The marker used to display network stations on the map. Defaults to ^ '
              '(Triangle)'))
@option('-NM', '--nonnetwork_station_marker', default="^", type=str,
        help=('The marker used to display non-network stations (within the network bbox) on '
              'the map. Defaults to ^ (Triangle)'))
@option('-nc', '--network_station_color', default="#ffef10", type=str,
        help=('The color used to display network stations on the map. Defaults to "#ffef10" '
              '(yellow-like color)'))
@option('-NC', '--nonnetwork_station_color', default="#dddddd", type=str,
        help=('The color used to display  non-network stations (within the network bbox) on '
              'the map. Defaults to "#dddddd" (gray-like color)'))
def n(out_path, conffiles_only, mv_datafiles, noprompt,
      network, start_after, area_margins, noise_pdf, inst_uptimes, network_station_marker,
      nonnetwork_station_marker, network_station_color, nonnetwork_station_color):
    """
    Generates the report folder for the given network and year. The destination
    directory will be a sub-directory of out_path with name [network]_[start_after].
    The data files are specified by the -p and -i options.

    NOTE: Data files specified by 'noise_pdf' and 'inst_uptimes' must denote one or
    more files or directories. They can be typed ONE OR MORE TIMES, where each file path is
    a local system path (with or without wildcards). They will be copied recursively in the
    relative output directory under 'data' (see above)

    Example:

    [program_name] --noise_pdf /home/my_images/myfile.png --noise_pdf /home/other_images/*.jpg
    """
    # remember: the doc above is shown when calling --help. Arguments DO NOT ACCEPT HELP,
    # BUT IN ANY CASE template commands do not have arguments

    # should i delete this? I do not understand what I said:
    # FIXME: IMPORTANT: unix shell expands wildcards automatically, so we might avoid the glob
    # module. Fine, BUT CLICK DOES NOT SUPPORT MULTIPLE (UNDEFINED) OPTIONS
    # So for the moment we DISABLE that option
    #
    # Moreover, if we ever re-implement it in the future, remember that windows does not expand
    # wildcards
    # (http://stackoverflow.com/questions/12501761/passing-multple-files-with-asterisk-to-python-shell-in-windows)

    # Note also that area margins are in degree because we want to make life easier
    # If you want to support 'm' and 'km', be aware that we need to convert margins back to string
    # to pass these to the initial map settings (supporting only degrees makes life easier,
    # just write in the map figure rst option:
    # ", ".join(str(m) for m in area_margins)
    try:
        runner = NetworkTemplater(out_path, conffiles_only, mv_datafiles, not noprompt)
        sys.exit(runner(network, start_after, area_margins, noise_pdf, inst_uptimes,
                        network_station_marker, nonnetwork_station_marker, network_station_color,
                        nonnetwork_station_color))
    except Exception as exc:
        print("Aborted: %s" % str(exc))
        sys.exit(1)


if __name__ == '__main__':
    main()  # pylint:disable=no-value-for-parameter
