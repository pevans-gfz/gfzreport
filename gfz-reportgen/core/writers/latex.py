'''
Created on Apr 4, 2016

@author: riccardo
'''
from docutils.nodes import SkipNode
from sphinx.writers.latex import LaTeXTranslator as LT, FOOTER, HEADER
from collections import OrderedDict as odict
from sphinx.builders import latex

class LatexTranslator(LT):
#     default_elements = LT.default_elements.copy()
#     default_elements.update({'postamble': ''})

    def __init__(self, document, builder):
        LT.__init__(self, document, builder)  # FIXME: check why new style super call does not work
        self.elements.update({'latex_epilog': builder.config.latex_elements.get("epilog", "")})
        self.field_list = odict()  # preserves order
        self.field_list_start = []
        self.rst_bib_fields = {}

    def visit_field_list(self, node):
        self.field_list_start = len(self.body)
        LT.visit_field_list(self, node)

    def depart_field_list(self, node):
        LT.depart_field_list(self, node)
        # remove all biblio fields, they are handled below
        self.body = self.body[:self.field_list_start]
#         if len(self.body) == self.field_list_start+2:
#             # remove field list stuff
#             self.body = self.body[:-2]

        if hasattr(self, "abstract_text_reminder"):
            self.body.extend([r'\begin{abstract}', '\n',
                              self.abstract_text_reminder, '\n', r'\end{abstract}'])

#     def visit_field_old(self, node):
#         field_name = node.children[0].rawsource.lower().strip()
#         field_text = node.children[1].rawsource.strip()  # FIXME: remove strip below!!!
# 
#         # add biblioraphic fields to be put in the latex preamble
#         # as newcommand. Note, we replace nwelines with latex counterpart
#         self.rst_bib_fields[field_name] = field_text.strip()
# 
#         if field_name in ("author", "authors"):
#             self.elements.update({'author': field_text.strip()})
#             raise SkipNode()  # do not call the children node rendering, and do not call depart node
# 
#         if field_name == "revision":
#             self.elements.update({'release': field_text.strip()})
#             raise SkipNode()  # do not call the children node rendering, and do not call depart node
# 
#         if field_name == "abstract":
#             self.abstract_text_reminder = field_text.strip()
#             raise SkipNode()  # do not call the children node rendering, and do not call depart node
# 
#         LT.visit_field(self, node)
#         h = 9
# 
#     def visit_field(self, node):
# 
#         field_name = node.children[0].rawsource.lower().strip()
# 
#         len_ = len(self.body)
#         LT.visit_field(self, node)
#         return
#         field_text = "".join(self.body[len_:]).strip()
#         self.body = self.body[len_:]
# 
#         # add biblioraphic fields to be put in the latex preamble
#         # as newcommand. Note, we replace nwelines with latex counterpart
#         self.rst_bib_fields[field_name] = field_text
# 
#         if field_name in ("author", "authors"):
#             self.elements.update({'author': field_text})
#             # raise SkipNode()  # do not call the children node rendering, and do not call depart node
# 
#         if field_name == "revision":
#             self.elements.update({'release': field_text})
#             # raise SkipNode()  # do not call the children node rendering, and do not call depart node
# 
#         if field_name == "abstract":
#             self.abstract_text_reminder = field_text
#             # raise SkipNode()  # do not call the children node rendering, and do not call depart node
# 
#     def depart_field(self, node):
#         LT.depart_field(self, node)  # superclass simply passes
# 
#     def visit_field_body(self, node):
#         LT.visit_field_body(self, node)
#         h = 9
#         str(node.parent.children[0].children[0])

    def depart_field_name(self, node):
        LT.depart_field_name(self, node)
        field_name = str(node.children[0])  # be consistent with depart field_body (use the same method!)
        self.rst_bib_fields[field_name] = len(self.body)
        
    def depart_field_body(self, node):
        LT.depart_field_body(self, node)
        field_name = str(node.parent.children[0].children[0])
        start = self.rst_bib_fields[field_name]
        field_value = "".join(self.body[start:]).strip()
        self.rst_bib_fields[field_name] = field_value
        if field_name in ("author", "authors"):
            self.elements.update({'author': field_value})  # FIXME: raw text or field value??
            # raise SkipNode()  # do not call the children node rendering, and do not call depart node

        if field_name == "revision":
            self.elements.update({'release': field_value})
            # raise SkipNode()  # do not call the children node rendering, and do not call depart node

        if field_name == "abstract":
            self.abstract_text_reminder = field_value
        h = 9

    def visit_figure(self, node):
        # set here the actual length of the body
        if 'source_imggrid_directive' in node['classes']:
            self._tmp_swap_method = self.depart_table
            self.depart_table = self.depart_table_inside_gridfigure
        LT.visit_figure(self, node)

    def depart_figure(self, node):
        LT.depart_figure(self, node)
        if 'source_imggrid_directive' in node['classes']:
            # restore the normal depart table method:
            self.depart_table = self._tmp_swap_method

    def depart_table_inside_gridfigure(self, node):
        # we have an imagesgrid, which must be rendered as figure
        # the code below is copied from the super-method for the case at hand
        # (\begin{tabulary}{\linewidth}{LLL})
        # removing all the cases for longtable, which we do not want here
        self.popbody()

        if self.table.has_verbatim:
            self.body.append('\n\\begin{tabular}')
            endmacro = '\\end{tabular}\n\n'
        elif self.table.has_problematic and not self.table.colspec:
            # if the user has given us tabularcolumns, accept them and use
            # tabulary nevertheless
            self.body.append('\n\\begin{tabular}')
            endmacro = '\\end{tabular}\n\n'
        else:
            self.body.append('\n\\begin{tabulary}{\\linewidth}')
            endmacro = '\\end{tabulary}\n\n'
        if self.table.colspec:  # FIXME: what's that??
            self.body.append(self.table.colspec)
        else:
            if self.table.has_problematic:
                colwidth = 0.95 / self.table.colcount
                colspec = ('p{%.3f\\linewidth}' % colwidth) * \
                    self.table.colcount
                self.body.append('{' + colspec + '}\n')
            else:
                self.body.append('{' + ('L' * self.table.colcount) + '}\n')
        if self.table.caption is not None:
            self.body.append(u'\\caption{')
            for caption in self.table.caption:
                self.body.append(caption)
            self.body.append('}')
            for id_ in self.next_table_ids:
                self.body.append(self.hypertarget(id_, anchor=False))
            self.next_table_ids.clear()
            self.body.append(u'\\\\\n')

        self.body.extend(self.tableheaders)
        for line in self.tablebody:
            if line != "\\hline":  # remove horizontal lines
                self.body.append(line)
        self.body.append(endmacro)
        self.unrestrict_footnote(node)
        self.table = None
        self.tablebody = None

#     @staticmethod
#     def latexise(text):
#         text_ = text.replace("\\", "\\textbackslash").\
#              replace("^", "\\textasciicircum").\
#              replace("~", "\\textasciitilde")  # .\
#              # replace("\n", "\\newline ")
# 
#         escaped = ["&", "%", "$", "#", "_", "{", "}"]
#         return "".join("\\" + a if a in escaped else a for a in text_)
    def visit_Text(self, node):
        """
            Calls the super method, and then replaces invalid characters
            For the moment, it just replaces the tilde operator with 
            \texttildelow
        """
        len_ = len(self.body)
        LT.visit_Text(self, node)
        for i in xrange(len_, len(self.body)):
            bdy = self.body[i]
            for bchar in bdy:
                # NOTE: the tilde we are interested in, and for which latex complains, is not the
                # ASCII TILDE, but a tilde operator whose ordinal is 8764
                # that's why this cumbersome way to do it:
                if ord(bchar) == 8764:
                    self.body[i] = self.body[i].replace(bchar, "\\texttildelow" )
                    break
        
    def astext(self):
        # build a dict of bibliographic fields, and inject them as newcommand 
        # in the latex header

        commands = ("%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                    "%% AUTO-GENERATED COMMANDS FROM BIBLIOGRAPHIC FIELDS IN THE SOURCE RST:\n" +
                    "\n".join("\\newcommand{\\rst" + name + "}{" + definition + "}"
                              for name, definition in self.rst_bib_fields.iteritems()) +
                    "\n%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                    "%% CUSTOM PREAMBLE DEFINED IN THE SOURCE RST CONFIG FILE:\n" +
                    "%(preamble)s\n"
                    "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%\n"
                    )
        HEADER_ = HEADER.replace(r"%(preamble)s", commands)

        FOOTER_ = FOOTER.replace("\\end{document}", "%(latex_epilog)s\n\\end{document}")

        return (HEADER_ % self.elements +
                self.highlighter.get_stylesheet() +
                u''.join(self.body) +
                '\n' + self.elements['footer'] + '\n' +
                self.generate_indices() +
                FOOTER_ % self.elements)


#
#
#         if self.table.rowcount > 30:
#             self.table.longtable = True
#         self.popbody()
#         if not self.table.longtable and self.table.caption is not None:
#             # this is the part of code I modified for gfz-reportgen:
#             # add catpion at the end
#             self.body.append('\n\n\\begin{table}[h!]\n'
#                              '\\capstart\n')
# 
#             for id in self.next_table_ids:
#                 self.body.append(self.hypertarget(id, anchor=False))
#             if node['ids']:
#                 self.body.append(self.hypertarget(node['ids'][0], anchor=False))
#             self.next_table_ids.clear()
#         if self.table.longtable:
#             self.body.append('\n\\begin{longtable}')
#             endmacro = '\\end{longtable}\n\n'
#         elif self.table.has_verbatim:
#             self.body.append('\n\\begin{tabular}')
#             endmacro = '\\end{tabular}\n\n'
#         elif self.table.has_problematic and not self.table.colspec:
#             # if the user has given us tabularcolumns, accept them and use
#             # tabulary nevertheless
#             self.body.append('\n\\begin{tabular}')
#             endmacro = '\\end{tabular}\n\n'
#         else:
#             self.body.append('\n\\begin{tabulary}{\\linewidth}')
#             endmacro = '\\end{tabulary}\n\n'
#         if self.table.colspec:
#             self.body.append(self.table.colspec)
#         else:
#             if self.table.has_problematic:
#                 colwidth = 0.95 / self.table.colcount
#                 colspec = ('p{%.3f\\linewidth}|' % colwidth) * \
#                     self.table.colcount
#                 self.body.append('{|' + colspec + '}\n')
#             elif self.table.longtable:
#                 self.body.append('{|' + ('l|' * self.table.colcount) + '}\n')
#             else:
#                 self.body.append('{|' + ('L|' * self.table.colcount) + '}\n')
#         if self.table.longtable and self.table.caption is not None:
#             self.body.append(u'\\caption{')
#             for caption in self.table.caption:
#                 self.body.append(caption)
#             self.body.append('}')
#             for id in self.next_table_ids:
#                 self.body.append(self.hypertarget(id, anchor=False))
#             self.next_table_ids.clear()
#             self.body.append(u'\\\\\n')
#         if self.table.longtable:
#             self.body.append('\\hline\n')
#             self.body.extend(self.tableheaders)
#             self.body.append('\\endfirsthead\n\n')
#             self.body.append('\\multicolumn{%s}{c}%%\n' % self.table.colcount)
#             self.body.append(r'{{\textsf{\tablename\ \thetable{} -- %s}}} \\'
#                              % _('continued from previous page'))
#             self.body.append('\n\\hline\n')
#             self.body.extend(self.tableheaders)
#             self.body.append('\\endhead\n\n')
#             self.body.append(r'\hline \multicolumn{%s}{|r|}{{\textsf{%s}}} \\ \hline'
#                              % (self.table.colcount,
#                                 _('Continued on next page')))
#             self.body.append('\n\\endfoot\n\n')
#             self.body.append('\\endlastfoot\n\n')
#         else:
#             self.body.append('\\hline\n')
#             self.body.extend(self.tableheaders)
#         self.body.extend(self.tablebody)
#         self.body.append(endmacro)
#         if not self.table.longtable and self.table.caption is not None:
#             # add captions NOW:
#             self.body.append('\\caption{')
#             for caption in self.table.caption:
#                 self.body.append(caption)
#             self.body.append('}')
# 
#             self.body.append('\\end{table}\n\n')
#         self.unrestrict_footnote(node)
#         self.table = None
#         self.tablebody = None
                
                
                