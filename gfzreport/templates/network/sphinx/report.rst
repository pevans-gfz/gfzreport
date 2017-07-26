.. Network report template. Please fill your custom text here below.
   This is a RsT (ReStructuredText) file and also a comprehensive tutorial
   which might help you during editing. RsT is a lightweight markup language designed to be both
   easily readable/editable and processable by documentation-processing software (sphinx) to
   produce html, latex or pdf output

   This portion of text (".. " followed by INDENTED text) is a comment block and will not
   be rendered. The comment block ends at the first non-indented line found


.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. TITLE:
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Section titles are set by decorating a SINGLE line of text with under- (and optionally over-)
   line characters WHICH MUST BE AT LEAST AS LONG AS the section title length.
   There is no rule about which decoration characters to use, but equal decorations are interpreted
   as same "level": thus two chapter titles must have the same decorations, a chapter and a section
   must not

{{ title }}

.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. FIELDS:
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Here below the document "fields" (authors, revision, etcetera): they are used as special
   variables for latex output and rendered according to templating rules you don't have to care about.
   They are in the form:
   :fieldname: fieldbody
   The ":fieldname: " part (including the trailing whitespace) is called the field marker:
   Please NEVER MODIFY (or DELETE) field markers. The field body on the other hand can contain:
   - newlines, indented relative to the field marker
   - colons, if they are escaped with a backslash: "\:"
   - multiple body elements, but note that raw text and raw urls only have been tested succesfully.

.. authors (AUTHOR INPUT). Provide the authors as comma separated items (affiliation still to be implemented):

:authors: Author1, author2, author3

.. subtitle. Filled automatically by default with the network description. Note: you
   should not specify newlines in it (same for subSubtitle below)

:subtitle: {{ network_description }}

.. sub-sub-title: this this is the (optional) sub-sub-subtitle (below the subtitle)

:subSubtitle: 

.. a revision mechanism from within the rst is currently not implemented,
   this field can be left as it is:

:revision: 1.0

.. the Scientific Technical Report (STR) number (LIBRARY INPUT). Fill in if you know it

:strNum: 

.. the doi (AUTHOR OR GIPP/GEOFON INPUT). Fill in if you know it. For info on the doi format see
   https://en.wikipedia.org/wiki/Digital_object_identifier#Nomenclature
   Example: http://doi.org/10.2312/GFZ.b103-xxxxx
      
:doi: 

.. The urn (LIBRARY INPUT). Fill in if you know it.
   Example: urn\:nbn:de\:kobv\:b103-xxxxx (remember to escape colons with backslash)
   Just a side-note for developers the sphinx builder will raise a
   warning as rst interprets it urn as URL. Please ignore the warning

:urn: 

.. the issn (LIBRARY INPUT). Fill in if you know it (e.g.: 2190-7110)

:issn: 

.. the publication year (LIBRARY INPUT). Fill in if you know it (e.g., 2016)

:publicationYear: 

.. the publication month (LIBRARY INPUT). Fill in if you know it (e.g., October)

:publicationMonth: 

.. (OPTIONAL AUTHOR INPUT) this field is optional and will be rendered (in latex only) under the section
   "Supplementary datasets:" in the back of the cover page. Fill it with
   a bibliographic citation to a publication (if any)

:supplDatasets: 

.. this field is OPTIONAL and will be rendered (in latex only) under the section
   "Recommended citation for chapter:" in the back of the cover page. Fill it with
   a bibliographic citation to a publication (if any)

:citationChapter: 

.. this field is optional and will be rendered (in latex only) under the section
   "The report and the datasets are supplements to:" in the back of the cover page.
   Fill it with a bibliographic citation to a publication (if any)

:supplementsTo: 

.. this is the abstract (AUTHOR INPUT) and will be rendered in latex within the 
   abstract environment (\begin{abstract} ... \end{abstract}):

:abstract: write your abstract here, you can add newlines but remeber:
           you should indent
           any new line


.. From here on the document content. Section titles are underlined (or under+overlined)
   Provide always at least an empty line above and below each section title


Introduction
============

.. (AUTHOR INPUT) Describe the overall motivation for the experiment, its scientific objectives, and general statements
   about the conduct of the experiment, overall evaluation etc. 


Data Acquisition
================

Experimental Design and Schedule
--------------------------------

.. (AUTHOR INPUT) Describe here the overall design and design goals, the schedule of deployment, recovery and service 
   trips, any major reorganisations of array geometry 

The station distribution is shown in :numref:`stations_figure`, and :numref:`stations_table`
summarises the most important information about each station.

Site Descriptions
-----------------

.. (AUTHOR INPUT) Describe in what environments stations were deployed (free field, urban etc., in houses or outside etc). 
   Upload pictures of a typical installation. 

Instrumentation
---------------

.. (AUTHOR INPUT) What instruments were used in the experiment, to whom do they belong. Any special issues? 
   What version of firmware did they run.  Any particular technical issues (malfunctioning equipment)

Sensor orientation
------------------

.. (AUTHOR INPUT) Were stations aligned to magnetic north or true north.  How were
   they aligned (in case of true north Gyrocompass or magnetic compass
   with correction). If magnetic compass was used, what was the magnetic
   declination at the time of the experiment and how was it
   determined. Note that GFZ provides a declination calculator at
   http://www.gfz-potsdam.de/en/section/earths-magnetic-field/data-products-services/igrf-declination-calculator/
   Please verify that the sensor orientation in the GEOFON database (see table below)
   matches the actual orientation. (If not please send an email to geofon@gfz-potsdam.de to correct this)


Data Description
================

Data Completeness
-----------------

.. (AUTHOR INPUT) What proportion of the data were recovered. What were the reasons for data loss

:numref:`inst_uptimes_figure` shows the uptime of each stations.

Data Processing
---------------

.. (AUTHOR INPUT) Describe the steps resulting in generating the miniseed file finally submitted to GEOFON
 
Data quality and Noise Estimation
---------------------------------

.. (AUTHOR INPUT) Describe the noise levels, describe possible noise sources (day/night variability if this information is available 
   and describe any other issues with the data quality, e.g. stuck components

Fig. :numref:`noise_pdfs_figure` shows noise probability density functions for all channels.

Timing Accuracy
---------------

.. (AUTHOR INPUT) How well did the GPS clocks run. Are there any stations with significant GPS outages?
   Be specific by providing tables or figures showing exactly which stations are trustworthy.
   What is your best estimate for the timing accuracy - note that for EDL you can upload 
   plots 


Data Access
===========

File format and access tools
----------------------------

.. Normally nothing to be added by the PI here

The data are stored in the GEOFON database, and selected time windows can be requested by EIDA
access tools as documented on http://geofon.gfz-potsdam.de/waveform/ . Normally the data are delivered in miniseed format. 
The current data access possibilities can always be found by resolving the DOI of the dataset.

Structure and file formats of supplementary datasets
----------------------------------------------------

.. (OPTIONAL AUTHOR INPUT) Describe here briefly the supplementary datasets downloaded if applicable
 
Availability
------------
.. (AUTHOR INPUT) Are data open or restricted. Until what time does an embargo last (for GIPP experiments normally 4 years after the end of data acquisition)
 

Conclusions and recommendations
===============================

.. (AUTHOR INPUT) If a colleague were to do an experiment in the same or similar area, what recommendations would you 
   make to maximise data recovery. Are there any other general lessons learned on deployment procedures
   or data pre-processing worth passing on to other users or the instrument pool.
 
   
Acknowledgments
===============

.. (AUTHOR INPUT) 


References
==========

.. Example: [RYBERG14] Trond Ryberg. Cube timing errors introduced by long periods without gps reception, 
    2014. URL http://www.gfz-potsdam.de/fileadmin/gfz/sec22/pdf_doc/GIPP/cube/Cube_timing_errors_no_gps.pdf .


.. end of the document content. Below figures and tables added by means of rst directives

.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. DIRECTIVES:
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. Rst "directives" are explicit markup blocks for generating special document objects, like
   figures and tables. They are in the form ".. directivetype::" and includes all subsequent
   INDENTED lines (see e.g. the ".. math::" directive above). A typical example to include a figure is:
   
   .. _figure-label:
   
   .. figure:: ./larch.png
      :width: 33%
      :align: center

      caption
   
   ".. _figure-label:" is the figure label, used to reference the figure via :numerf:`figure_label`
   - "./larch.png" is called the directive argument
   - ":width: 33%" and ":align: center" are directive options in the form :name: value
   - "caption" is called the directive content
   (For details, see http://docutils.sourceforge.net/docs/ref/rst/directives.html#figure)

   **IMPORTANT**:
   1. In the following, with "directive block" (or simply block) we will denote the directive AND its
   label (if any).
   2. A directive block must be always preceeded and followed by a blank line. Always.
   3. Only a blank line, not even comments, can be input between a label and
   its directive
   4. From within the web application only, NEVER edit:
      - file paths as they are relative to this document path on the server.
      - option names, as they might break the document build.
      Everything else (non-file argument, non-file content, option values) can be editable
   
   You can always delete / move / copy a directive BLOCK anywhere in the text.
   Non-standard Rst directives (i.e., implemented and working in this program only) are marked as
   (NonStandard) below


.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
.. CUSTOM DIRECTIVES (FIGURES AND TABLES)
.. ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. 1) The first directive is the directive to display the stations information in a
   table. It's the so called 'csv-table' directive
   (http://docutils.sourceforge.net/docs/ref/rst/directives.html#id4):
   There are several ways to display tables in RsT. Curiously, none of them is free from drawbacks
   and limitations. Csv-tables have the advantage to be easily editable here.

.. first of all, we show the "raw" directive, which might comes handy to put
   html or latex specific commands: in this case we decrease the size of the table
   to avoid page horizontal overflow. Remove the directive or change '\scriptsize' if you need it.
   
.. raw:: latex

   \scriptsize
   
.. we use the tabularcolumns directive
   (http://www.sphinx-doc.org/en/latest/markup/misc.html#directive-tabularcolumns):
   this directive gives a “column spec” for the next table occurring in the source file.
   The spec is the second argument to the LaTeX tabulary package’s environment, although,
   sphinx might use different tabular environment:

.. tabularcolumns:: |@{\ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ \ }l@{\ \ }|


.. customize the table horizontal lines via the (NonStandard) tabularrows directive which applies to the next
   generated table (latex output only). You can remove the whole block to show all hlines (default in sphinx).
   The directive can have two options, 'hline-show' or 'hline-hide' (*either* one *or* the other) specifying
   the indices of the hlines to show/hide, separeted by spaces (first index is 0). You can also
   provide python slice notations in the format 'start:end' or 'start:end:step'
   (http://stackoverflow.com/questions/509211/explain-pythons-slice-notation).
   The command might not perfect as it is a hack around a poor sphinx implementation, and might
   need some trial-and-errors for for tables spanning over multiple pages. As an example, we want
   to show the first (0) and the last (-1) hlines, and each fourth hline starting from the second
   one (1::4 which means indices 1,5,9,...)
   
.. tabularrows::
   :hline-show: 0 1::4 -1

.. finally, the table directive (preceeded by its label so you can reference it via
   :numref:`stations_table`). In principle, you might want to edit the
   directive content as any csv file (the table content. To provide empty strings, quote them like this: "")
   or its argument (the table caption) which as you can see can spanning over several lines
   (providing as always the correct indentation)
   
.. _stations_table:

.. csv-table:: Station table. Note that start and end times represent the maximum validity of the
   corresponding configurations, not the actual data availability or time in the field.
   Azi: Azimuth of north or '1' component.
   :delim: space
   :quote: "
   :header-rows: 1
   
   {{ stations_table.content|indent(3) }}

.. restore normal size in latex only:

.. raw:: latex

   \normalsize


.. ==============================================================================   

.. 2) The second directive below is the (NonStandard) directive to display the station map figure.
   The syntax is similar to the csv-table directive (ses above) BUT produces an image instead.
   After the label definition (so you can reference the map figure via
   :numref:`stations_figure`), in the directive you can edit the argument (the map caption, keep
   indentation for newlines), the content as any csv file, or the directive option **values** 
   to customize the map: a full documentation of all option names is in preparation, we tried to make
   them as much self-explanatory as possible

.. _stations_figure:

.. mapfigure:: Station distribution in experiment (red symbols). If present, white-filled symbols
   show permanent stations and other temporary experiments archived at EIDA or IRIS-DMC,
   whose activity period overlapped at least partially with the time of the experiment.
   If present, open symbols show station sites which were no longer active at the time
   of the experiment, e.g. prior temporary experiments.
   :header-rows: 1
   :align: center
   :delim: space
   :quote: "
   {% for opt_name in stations_map.options -%}
   :{{ opt_name }}: {{ stations_map.options[opt_name] | safe }}
   {% endfor %}
   {{ stations_map.content|indent(3)  }}


.. ==============================================================================   

.. 3) The third directive is the (NonStandard) directive 'gridfigure' to display the noise pdfs.
   The syntax is similar to the csv-table directive (see above) BUT produces a grid of images.
   Note that in latex this will be rendered with a longtable followed by an
   empty figure with only the caption inside. This is a workaround to produce something that
   looks like a figure spanning over several pages (if needed) BUT it might need some arrangment
   as the figure caption might be placed on a different page. Being a table and a figure, all figure
   + table options, as well as all figure + table latex pre-customization (e.g. 'tabularcolumns',
   'includegraphics') apply also to a 'gridfigure'

.. first issue a raw latex command (You can remove the lines if the layout does not need a clear page):

.. raw:: latex

   \clearpage
   
.. customize latex tabularcolumns:
   
.. tabularcolumns::  @{}c@{}c@{}c@{}

.. customize the includegraphics options (only for latex output) for the next figure or image
   found (in the former case, applies the includegraphics options to all images of the figure):
   
.. includegraphics:: trim=8 30 76 0,width=0.33\textwidth,clip

.. customize also horizontal lines when rendering to latex. As usual, remove the block below to
   show all hlines. The block is mainly used as another example of the use of python slice
   notations: "a:b" means "from a until b-1". If a is missing it default to zero, if b is missing
   it defaults to the index after the last element. Thus ":" means all elements and the directive
   below hides all hlines:

.. tabularrows::
   :hline-hide: :

.. finally, the gridfigure directive (preceeded by its label so you can reference it via
   :numref:`noise_pdfs_figure`). The directive argument is the figure caption, the directive
   content holds the auto-generated pdfs placed on the server in the :dir: option (**do not change it!!**)

.. _noise_pdfs_figure:

.. gridfigure:: Noise probability density functions for all stations for database holdings
   :dir: {{ noise_pdfs.dirpath | safe  }}
   :delim: space
   :align: center
   :header-rows: 1

   {{ noise_pdfs.content|indent(3) }}
   

.. ==============================================================================   

.. 4) The fourth directive is the directive to display the instrumental uptimes.
   Depending on the number of files uploaded when generating this template, it's either a
   'figure' or a (NonStandard) 'gridfigure' directive, in any case it will be rendered as figure in
   html and latex).

.. customize the includegraphics options (only for latex output) for the next figure or image
   found (in the former case, applies the includegraphics options to all images of the figure):

{% if inst_uptimes.directive == 'gridfigure' -%}
.. includegraphics:: width=\textwidth
{% else -%}
.. includegraphics:: angle=-90,width=\textwidth
{% endif -%}

.. here the directive (preceeded by its label so you can reference it via
   :numerf:`inst_uptimes_figure`). Note that the directive type is dynamically auto generated:
   if it's a 'figure' type, you can change the directive content which is the figure
   caption. If it's a 'gridfigure' type, remember that the directive *argument*
   is the figure caption

.. _inst_uptimes_figure:

{% if inst_uptimes.directive == 'gridfigure' -%}
.. gridfigure:: Overview of uptimes of all stations generated with `obspy-scan`
   {% for opt_name in inst_uptimes.options -%}
   :{{ opt_name }}: {{ inst_uptimes.options[opt_name] | safe }}
   {% endfor -%}
   :align: center
   
   {{ inst_uptimes.content|indent(3)  }}
{% else -%}
.. figure:: {{ inst_uptimes.arg  }}
   {% for opt_name in inst_uptimes.options -%}
   :{{ opt_name }}: {{ inst_uptimes.options[opt_name] | safe }}
   {% endfor -%}
   :width: 100%
   :align: center
   
   Overview of uptimes of all stations generated with `obspy-scan`
{% endif %}