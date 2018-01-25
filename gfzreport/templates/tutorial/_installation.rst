
Installation
============


Install a python virtual environment
------------------------------------

Activate the virtual environment:

   * `python virtualenv <http://docs.python-guide.org/en/latest/dev/virtualenvs/>`_
   
   * `python virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/en/latest/index.html>`_
   
Install this python package
---------------------------

Download the reportgen git repository in a local folder, cd into it and install this package:

.. code-block:: bash

   pip install -r ./requirements.txt

(or if you want to install also test packages (recommended):

.. code-block:: bash

   pip install -r ./requirements.dev.txt

and then:

.. code-block:: bash

   pip install -e .

(you can remove the -e option if the package has not to be installed as editable, if desired)

Now you should have all python packages installed, *except*
`basemap <https://github.com/matplotlib/basemap>`_
(python library to plot on map projections with coastlines and political boundaries using ``matplotlib``):

Package installation notes
^^^^^^^^^^^^^^^^^^^^^^^^^^

- for problems installing the required python package ``lxml``, ``libxml2-dev libxslt-dev`` are required
  (see here: http://lxml.de/installation.html)

- for problems installing scipy, you might want to execute first (this worked in ubuntu 14.04):

  .. code-block:: bash
  
     sudo apt-get install libblas-dev liblapack-dev libatlas-base-dev gfortran
    
     pip install scipy
   
- Matplotlib:

  On Mac, you could have the following issue:
  
  .. code-block:: bash
  
     RuntimeError: Python is not installed as a framework. The Mac OS X backend will not be able to function 
     correctly if Python is not installed as a framework. See the Python documentation for more information 
     on installing Python as a framework on Mac OS X. Please either reinstall Python as a framework, or try 
     one of the other backends. If you are Working with Matplotlib in a virtual enviroment see 'Working with 
     Matplotlib in Virtual environments' in the Matplotlib FAQ
  
  On Ubuntu, we had another type of issue:
  
  .. code-block:: bash
  
     Exception occurred:
       File "/usr/lib/python2.7/lib-tk/Tkinter.py", line 1767, in __init__
         self.tk = _tkinter.create(screenName, baseName, className, interactive, wantobjects, useTk, sync, use)
     TclError: no display name and no $DISPLAY environment variable
  
  
  Fortunately, it seems that for both problems the solution is to set 'Agg' as matplotlib backend.
  You can edit the `matplotlibrc file <http://matplotlib.org/users/customizing.html#the-matplotlibrc-file>`_
  in your virtual environment, which you can also locate by typing 
  
  .. code-block:: bash
  
     python -c "import matplotlib;print matplotlib.matplotlib_fname()"
  
  in the terminal. Then open it, locate the line
  
  .. code-block:: bash
  
     backend: ...
  
  Replace it with (or add the following if no such line was found):
  
  .. code-block:: bash
  
     backend: Agg
  
  (To avoid coupling between code and configuration, we removed the matplotlibrc that was previously shipped
  with this program)

- Matplotlib (not during installation but during *execution*, e.g., when typing ``gfzreport --help``):

  The following time-consuming and therefore annoying message might appear:
  
  .. code-block:: bash
  
     .../matplotlib/font_manager.py:273: UserWarning: Matplotlib is building the font cache using fc-list. This may take a moment.
     warnings.warn('Matplotlib is building the font cache using fc-list. This may take a moment.')
  
  To fix this, on Ubuntu14.04, we issued the following command:
  
  .. code-block:: bash
  
     rm ~/.cache/matplotlib/fontList.cache
     
  When executing again gfzreport, the message still appears but only the first time. For details see this
  `post <https://stackoverflow.com/questions/34771191/matplotlib-taking-time-when-being-imported>`_.   

 
Install basemap and dependencies
--------------------------------

According to `basemap requirements <https://github.com/matplotlib/basemap#requirements>`_:
you should first make sure, if your python was installed via a package management system,
that the corresponding ``python-dev`` package is also installed.
Otherwise, you may not have the python header (Python.h), which is required to build python
C extensions (see :ref:`basemapnotes`).

1. Download basemap-1.0.7.tar.gz (*approx 100 mb*) from
   `here (see source code links in the page) <https://github.com/matplotlib/basemap/releases/tag/v1.0.7rel>`_.
   Unpack and cd to basemap-1.0.7:

   .. code-block:: bash

      cd <where you downloaded basemap basemap-1.0.7rel.tar.gz>
      tar -zxvf basemap-1.0.7rel.tar.gz
      cd basemap-1.0.7

2. Install the GEOS library.

   * If you already have it on your system, just set the environment variable GEOS_DIR to point to
     the location of libgeos_c and geos_c.h (if libgeos_c is in /usr/local/lib and geos_c.h is in
     /usr/local/include, set GEOS_DIR to /usr/local):
 
     .. code-block:: bash
    
        export GEOS_DIR=<location of GEOS directory>

     Then go to next step.

   * If you don't have it, you can build it from the source code included with basemap by following
     these steps:

     .. code-block:: bash

        cd geos-3.3.3
        export GEOS_DIR=<where you want the libs and headers to go>
  
     A reasonable choice on a Unix-like system is /usr/local, or if you don't have permission to
     write there, your home directory. Then
     
     .. code-block:: bash
     
        ./configure --prefix=$GEOS_DIR 
        make; make install

3. cd back to the top level basemap directory (basemap-X.Y.Z) and run the usual

   .. code-block:: bash
    
      python setup.py install

   Check your installation by running at the python prompt:

   .. code-block:: bash

      from mpl_toolkits.basemap import Basemap
 
4. To test, cd to the examples directory and run
   
   .. code-block:: bash

      python simpletest.py
 
   To run all the examples (except those that have extra dependencies or require an internet connection),
   execute

   .. code-block:: bash
    
      python run_all.py

.. _basemapnotes:

Basemap installation notes
^^^^^^^^^^^^^^^^^^^^^^^^^^

- We skipped some of the basemap requirements `pyproj <https://github.com/jswhit/pyproj>`_ and `pyshp <https://github.com/GeospatialPython/pyshp>`_ as they do not seem to be mandatory for this program to run (keep it in mind in case of troubles though). Moreover, note that there are two optional packages which might be useful if you mean to use basemap outside this program:

  1 `OWSLib <https://github.com/geopython/OWSLib>`_ (optional) It is needed for the BaseMap.wmsimage function

  2 `Pillow <https://python-pillow.github.io/>`_ (optional)  It is needed for Basemap warpimage, bluemarble, shadedrelief, and etop methods. PIL should work on Python 2.x.  Pillow is a maintained fork of PIL

- On Mac El Capitan, after upgrading with ``homebrew`` we had this issue:

  .. code-block:: python
  
     ImportError: dlopen(/Users/riccardo/work/.virtualenvwrapper/envs/gfz-gfzreport/lib/python2.7/site-packages/_geoslib.so, 2): Library not loaded: /usr/local/opt/geos/lib/libgeos-3.5.0.dylib
     Referenced from: /Users/riccardo/work/.virtualenvwrapper/envs/gfz-gfzreport/lib/python2.7/site-packages/_geoslib.so
     Reason: image not found
  
  After googling a lot, re-installing several times ``basemap`` and ``geos`` without success,
  as there was a libgeos library named
  ``libgeos-3.6.2.dylib`` in the specified path, we tried this horrible hack which surprisingly worked:
  
  .. code-block:: python
  	 
  	 cp /usr/local/opt/geos/lib/libgeos-3.6.2.dylib /usr/local/opt/geos/lib/libgeos-3.5.0.dylib

Install tex packages
--------------------

|pdf| documents are built by means of ``pdflatex`` (As of mid 2016, dedicated python sphinx extensions/plugins
turned out to be buggy and not easily customizable)

Ubuntu
^^^^^^

Tex packages are required to run ``pdflatex`` for generating |pdf| output:

.. code-block:: bash
   
   sudo apt-get install texlive-latex-base texlive-bibtex-extra texlive-latex-extra texlive-fonts-extra texlive-fonts-recommended texlive-humanities texlive-publishers

Mac OsX
^^^^^^^

Installation of |latex| in Mac is quite complex compared to Ubuntu, you have two choices:

1. Install `MacTex <http://www.tug.org/mactex/index.html>`_ (either on the link provided or
   via ``brew cask install mactex``). This is by far the recommended way, although it might take times
   (gigabytes to be downloaded)

2. Install BasicTex via homebrew which is more lightweight:

   .. code-block:: bash
        
      brew install basictex tex-live-utility
      tlmgr install install basictex

   and then install texlive utilities:
  
   .. code-block:: bash

      sudo tlmgr install collection-fontsrecommended titlesec fncychap tabulary framed threeparttable wrapfig capt-of needspace multirow eqparbox varwidth environ trimspaces
  
   Remember that we cannot assure these are sufficient for all OS / BasicTex versions, so it is up to the user to keep things updated. If a package is missing, then the report generation will fail with unreported missing packages

Useful links
************

- `installing fontsrecommended in mac os <http://tex.stackexchange.com/questions/160176/usepackagescaledhelvet-fails-on-mac-with-basictex>`_

- `installing latex on linux and mac os <https://docs.typo3.org/typo3cms/extensions/sphinx/AdministratorManual/RenderingPdf/InstallingLaTeXLinux.html>`_

Run tests
---------

Run (from within the main gfzreport directory):

.. code-block:: bash

   py.test ./tests -xs --ignore=./tests/skip --cov=./gfzreport


Install the web application on a Server with Apache
---------------------------------------------------

A detailed explanation is beyond the scope of this tutorial. However, here the notes collected
when installing the web application on a server with apache:

.. code-block:: bash
   
   install package as editable.
   Git pull on the gfzreport package to refresh new updates (restart apache in case)
   
   Create a folder wsgis (currently in the same git dir, untracked)
   Create the wsgis file you need by copying example.wsgi (and changing the paths accordingly), edit them
   current data path: /data2/gfzreport/network
   current db path: /data2/gfzreport  (users.sqlite will be created there)
   
   create users.txt in db path (see example.users.txt)
   
   Add apache conf files pointing to those wsgis
   
   Debug apache2 from the terminal:
   
   tail -f /var/log/apache2/error.log
   
   RESTART APACHE SERVER:
   service apache2 restart
   
   Nvaigate to the web app url in a browser