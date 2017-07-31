'''
Created on Jan 9, 2017

Core utilities for the network-generator program

@author: riccardo
'''

import sys
import os
import shutil
# import threading
from multiprocessing.pool import ThreadPool
import csv
from datetime import datetime
import re
from collections import defaultdict, OrderedDict
import urllib2
from cStringIO import StringIO
from itertools import product, cycle, izip
from lxml import etree
from lxml.etree import XMLSyntaxError
from glob import glob
from urllib2 import URLError, HTTPError

import numpy as np
import pandas as pd
# from obspy import read_inventory
from jinja2 import Environment
# from lxml.etree import XMLSyntaxError
from gfzreport.templates.network.core.utils import relpath, read_geofonstations, read_stations, todf,\
    get_query, iterdcurl
from gfzreport.sphinxbuild.map import getbounds


def geofonstations_df(network, start_after_year):
    """
        Returns the dataframe representing the network stations table in rst.
        :param network: string. The network name (e.g., 'ZE')
        :param start_after_year (string or integer) The year denoting the network start time
        Only stations after that time will be displayed
    """

    geofon_inventory = read_geofonstations(network, start_after_year)

    def int_(val):
        ival = int(val)
        return ival if ival == val else val

    def func(net, sta):
        retdict = defaultdict(OrderedDict)
        strfrmt = "%0.4d-%0.2d-%0.2d"
        for cha in sta.channels:
            start = strfrmt % (cha.start_date.year, cha.start_date.month, cha.start_date.day)
            end = strfrmt % (cha.end_date.year, cha.end_date.month, cha.end_date.day)
            # identify each row by its channel tuple:
            id_ = (sta.code, start, end)
            mydic = retdict[id_]  # add if does not exist
            mydic['Label'] = sta.code
            mydic['Lat'] = sta.latitude
            mydic['Lon'] = sta.longitude
            mydic['Ele'] = int_(cha.elevation)
            mydic['Azi'] = int_(max(mydic['Azi'], cha.azimuth) if 'Azi' in mydic else cha.azimuth)
            mydic['Rate'] = int_(cha.sample_rate)
            mydic['Sensor'] = cha.sensor.model
            mydic['ID'] = cha.sensor.serial_number
            mydic['Logger'] = cha.data_logger.model
            mydic['Id'] = cha.data_logger.serial_number
            mydic['Start'] = start
            mydic['End'] = end
            mydic['Channels'] = "%s %s" % (mydic['Channels'], cha.code) \
                if 'Channels' in mydic else cha.code

        return retdict.itervalues()

    dframe = todf(geofon_inventory, func, funclevel='station', sortkey=lambda val: val['Label'])

    # add metadata:
    dframe.metadata = {'start_date': None, 'end_date': None, 'desc': ''}
    for net in geofon_inventory:
        if net.code == network:
            dframe.metadata['start_date'] = net.start_date
            dframe.metadata['end_date'] = net.end_date
            dframe.metadata['desc'] = net.description
            break

    return dframe


def otherstations_df(geofonstations_df, margins_in_deg):
    tonum = pd.to_numeric
    _, _, minlon, minlat, maxlon, maxlat = getbounds(tonum(geofonstations_df['Lon']).min(),
                                                     tonum(geofonstations_df['Lat']).min(),
                                                     tonum(geofonstations_df['Lon']).max(),
                                                     tonum(geofonstations_df['Lat']).max(),
                                                     margins_in_deg)

    meta = geofonstations_df.metadata
    kwargs_live_stations = dict(minlat=minlat, maxlat=maxlat, minlon=minlon, maxlon=maxlon,
                                starttime=meta['start_date'].isoformat(),
                                endtime=meta['end_date'].isoformat(),
                                level='station')
                                # format='xml')

    kwargs_dead_stations = dict(kwargs_live_stations)
    kwargs_dead_stations['endbefore'] = kwargs_dead_stations.pop('starttime')
    kwargs_dead_stations.pop('endtime')

    invs = []
    # use standard python process pool thread:
    # see second post here:
    # https://stackoverflow.com/questions/16181121/a-very-simple-multithreading-parallel-url-fetching-without-queue
    timeout = 240

    def fetch_inv(tup):
        querystr = 'unknown url'
        try:
            dc, kwargs = tup
            querystr = get_query(dc, **kwargs)
            return read_stations(querystr, timeout=timeout), querystr, None
        except Exception as exc:
            return None, querystr, exc

    # Note: we could remove lon and lat args (minlat, maxlat,...) from kwargs_live_stations and
    # kwargs_dead_stations, as we passed it to iterdcurl
    # but iterdcurl for IRIS returns the url ignoring the arguments (eida routing service "bug")
    # so so we need to forward them also to fetch_inv above
    fetch_inv_args = (args for args in product(iterdcurl(minlon=minlon, minlat=minlat,
                                                         maxlon=maxlon, maxlat=maxlat),
                                               [kwargs_live_stations, kwargs_dead_stations])
                      if "geofon" not in args[0])

    results = ThreadPool(20).imap_unordered(fetch_inv, fetch_inv_args)
    for inv, url, error in results:
        if error is None:
            invs.append(inv)
        else:
            print("Warning: error fetching inventory (%s)\n   url: %s" % (error, url))

    symbols = cycle([
                     # '.',  # point
                     # ',',  # pixel
                     'o',  # circle
                     '^',  # triangle_up
                     'v',  # triangle_down
                     '<',  # triangle_left
                     '>',  # triangle_right
                     # '1',  # tri_down
                     # '2',  # tri_up
                     # '3',  # tri_left
                     # '4',  # tri_right
                     '8',  # octagon
                     # 's',  # square
                     'p',  # pentagon
                     '*',  # star
                     'h',  # hexagon1
                     'H',  # hexagon2
                     # '+',  # plus
                     # 'x',  # x
                     'D',  # diamond
                     'd',  # thin_diamond
                     # '|',  # vline
                     # '_',  # hline
    ])

    net2markers = defaultdict(lambda: next(symbols))

    # parse all inventories and return dataframes
    def func(net, sta):
        retdict = defaultdict(OrderedDict)
        # Code: # net.code
        if net.code == 'SY':  # ignore synthetic data
            return retdict

        # get symbols (cycle iterates on infinity and returns to top)
        marker = net2markers[net.code]
        # get caption (using restricted, year range and network code):
        if net.restricted_status == 'open':
            restricted = ""
        else:
            restricted = " (restr.)"
        # for temporary networks additional quote years of operation
        if net.code[0] in 'XYZ0123456789':
            yearrng = " %d-%d" % (net.start_date.year, net.end_date.year)
        else:
            yearrng = ""
        caption = "%s%s%s" % (net.code, yearrng, restricted)

        nooverlap = net.end_date < geofonstations_df.metadata['start_date'] or \
            net.start_date > geofonstations_df.metadata['end_date']

        color = '#FFFFFF00' if nooverlap else '#FFFFFF'

        mydic = OrderedDict()
        mydic['Label'] = sta.code
        mydic['Lat'] = sta.latitude
        mydic['Lon'] = sta.longitude
        mydic['Network'] = net.code
        mydic['Marker'] = marker
        mydic['Legend'] = caption
        mydic['Color'] = color
        return mydic

    dfs = []
    for inv in invs:
        dframe = todf(inv, func, funclevel='station')  # , sortkey=lambda val: val['Name'])
        if not dframe.empty:
            dfs.append(dframe)

    # return stations active in the relative timespan:
    return pd.concat(dfs, axis=0, ignore_index=True, copy=False)


def get_map_df(geofonstations_df, otherstations_df):
    """Returns a DataFrame representing the stations map of an rst mapfigure directive.
       ```
        map_df = get_map_df(...)
        # return the csv content:
        map_df.to_csv(sep=" ", quotechar='"', index=False)

        :param geofonstations_df: the dataframe representing the stations of the network 
        :param otherstations_df: the dataframe representing all other stations which need to be
        shown on the map
    """
    # current captions are:
    columns = ['Label', 'Lat', 'Lon', 'Marker', 'Color', 'Legend']
    # The first three are common to both dataframes. otherstations_df has all five columns

    # make a new geofonstations_df, it will be a view of the original geofonstations_df.
    # But this way we do not pollute the original
    _sta_df = geofonstations_df[columns[:3]]
    # avoid pandas settingwithcopy warnings (we know what we are doing):
    _sta_df.is_copy = False

    _sta_df['Marker'] = 's'  # square
    _sta_df['Legend'] = ''
    sensors = pd.unique(geofonstations_df['Sensor'])

    # create a variable color scale (red scale)
    # set first a min val of the red component (0=black, 255 full_red): we want to avoid
    # full black colors
    MIN_RED = 50
    # set the step of the scale in order to maximize the distance
    step = (255.0 - MIN_RED) / (len(sensors)-1) if len(sensors) > 1 else 1
    # set the colors. The first will be full red, then darker until
    colors = ["#%s0000" % hex(int(255-step*i))[2:].upper().zfill(2) for i in xrange(len(sensors))]

    _sta_df['Color'] = ''
    for sens, col in izip(sensors, colors):
        _sta_df.loc[geofonstations_df['Sensor'] == sens, 'Color'] = col
        _sta_df.loc[geofonstations_df['Sensor'] == sens, 'Legend'] = sens

    ret_df = pd.concat([_sta_df, otherstations_df], axis=0, ignore_index=True, copy=False)[columns]
    # mark all duplicated Legends as empty except the first(s):
    ret_df.loc[ret_df['Legend'].duplicated(), 'Legend'] = ''
    return ret_df


def get_noise_pdfs_content(dst_dir, regex="^(?P<row>.*)_(?P<col>[A-Z][A-Z][A-Z]).*$",
                           delimiter=" ",
                           columns=["HHZ", "HHN", "HHE"]):

    # Provide a default value DEF_VAL for non-found files. Do not provide empty strings as DEF_VAL
    # if the delimiter is the space as this is not rendered properly in the csv content
    # (for safety, do not provide empty strings as DEF_VAL in any case):
    DEF_VAL = 'WARNING: file not found'
    lineterminator = '\n'
    quotechar = '"'
    reg = re.compile(regex)
    dct = defaultdict(lambda: [DEF_VAL] * len(columns))
    for fl in os.listdir(dst_dir):
        mat = reg.match(fl)
        if mat and len(mat.groups()) == 2:
            row = mat.group('row')
            col = mat.group('col')
            if col in columns:
                dct[row][columns.index(col)] = fl

    ret = [columns] + [dct[k] for k in sorted(dct)]

    sio = StringIO()
    spamwriter = csv.writer(sio, delimiter=delimiter, quotechar=quotechar,
                            lineterminator=lineterminator,
                            quoting=csv.QUOTE_MINIMAL)
    for line in ret:
        spamwriter.writerow(line)
    ret = sio.getvalue()
    sio.close()
    return ret


def get_figdirective_vars(src_path, src_rst_path):
    """
    Returns a dict D with keys
    'directive', 'arg', 'options', 'content'
    to be used in a jinja template:
    The returned dict directive will be 'figure' or 'gridfigure' if only one
    file is found in `src_rst` or more, repsectively (if no file, ValueError is raised).
    """
    filenames = [f for f in os.listdir(src_path)]

    if len(filenames) == 0:
        raise ValueError("No file found in '%s' while building figure directive" % src_path)
    elif len(filenames) == 1:
        dic = {'directive': 'figure',
               'arg': relpath(os.path.join(src_path, filenames[0]), src_rst_path),
               'content': ''  # not used, but jinja won't complain. Supply a string not None
               }
    elif len(filenames) > 1:
        filenames = sorted(filenames)
        dic = {'directive': 'gridfigure',
               'content': "\n".join('"%s"' % f if " " in f else f for f in filenames),
               'options': {'dir': relpath(src_path, src_rst_path), 'delim': 'space'},
               'arg': ''  # not used, but jinja won't complain. Supply a string not None
               }
    return dic


def gen_title(networkname, geofonstations_df):
    """Generates the title for the .rst file from a pandas DataFrame returned by
    get_network_stations"""
    # template:
    # =============================================================
    # {{ network_code }} {{ network_start_date }}-{{ network_end_date }}
    # =============================================================
    meta = geofonstations_df.metadata
    start = meta['start_date'].year if 'start_date' in meta else None
    end = meta['end_date'].year if 'end_date' in meta else None
    timerange = " %d-%d" % (start, end) if start and end else ""
    title = "%s%s" % (networkname, timerange)
    decorator = "=" * len(title)
    return "%s\n%s\n%s" % (decorator, title, decorator)


def get_net_desc(stations_df):
    """Returns the network description for the .rst file from a pandas DataFrame returned by
    get_network_stations"""
    return stations_df.metadata['desc']
