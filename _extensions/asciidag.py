# -*- coding: utf-8 -*-

# Copyright (c) 2012-2013 by Christoph Reller. All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

#    1. Redistributions of source code must retain the above copyright notice,
#       this list of conditions and the following disclaimer.

#    2. Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.

# THIS SOFTWARE IS PROVIDED BY CHRISTOPH RELLER ''AS IS'' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL CHRISTOPH RELLER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT,
# INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# The views and conclusions contained in the software and documentation are
# those of the authors and should not be interpreted as representing official
# policies, either expressed or implied, of Christoph Reller.

"""sphinxcontrib.asciidag
    ~~~~~~~~~~~~~~~~~~~~~

    Draw pictures with dagmatic and the TikZ/PGF LaTeX package.

    Based on sphinxcontrib.tikz by Christoph Rellerq
    <christoph.reller@gmail.com>

    Author: Sean Farley <sean@farley.io>
    Version: 0.0.1

"""

import dagmatic
import tempfile
import posixpath
import shutil
import sphinx
import os

from subprocess import Popen, PIPE
from docutils import nodes, utils, core
from docutils.statemachine import ViewList
from sphinx.util.compat import Directive

from sphinx.errors import SphinxError

try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

try:
    from sphinx.util.osutil import ensuredir, ENOENT
except ImportError:
    from sphinx.util import ensuredir, ENOENT

class DagExtError(SphinxError):
    category = 'ASCII DAG extension error'

class daginline(nodes.Inline, nodes.Element):
    pass

def dag_role(role, rawtext, text, lineno, inliner, option={}, content=[]):
    dag = utils.unescape(text, restore_backslashes=True)
    return [daginline(dag=dag)], []

class dag(nodes.Part, nodes.Element):
    pass

class DagDirective(Directive):
    has_content = True
    required_arguments = 0
    optional_arguments = 1
    final_argument_whitespace = True

    def run(self):
        node = dag()
        node['dag'] = '\n'.join(self.content)
        node['caption'] = '\n'.join(self.arguments)
        if not self.content:
            node['caption'] = ''
            node['dag'] = '\n'.join(self.arguments)

        node['bugfixed'] = False
        try:
            if sphinx.version_info[0] >= 1 and sphinx.version_info[1] >= 4:
                node['bugfixed'] = True
        except AttributeError:
            pass

        if node['bugfixed'] and node['caption']:
            figure_node = nodes.figure('', node)
            parsed = nodes.Element()
            self.state.nested_parse(ViewList([node['caption']], source=''),
                                    self.content_offset, parsed)
            caption_node = nodes.caption(parsed[0].rawsource, '',
                                         *parsed[0].children)
            caption_node.source = parsed[0].source
            caption_node.line = parsed[0].line
            figure_node += caption_node
            node = figure_node

        return [node]

DOC_HEAD = r'''
\documentclass[tikz]{standalone}
\usetikzlibrary{%s}
'''

DEFAULT_TIKZ = r'''
\tikzset{
  changeset/.style={
    draw=#1,
    thick,
    minimum width=3em,
    minimum height=2em
  },
  changeset/.default={black},
%%
  obschangeset/.style={
    draw=#1,
    thick,
    dashed,
    minimum width=3em,
    minimum height=2em
  },
  obschangeset/.default={black},
%%
  upperT/.style={
    fill=white,
    minimum width=0,
    minimum height=0,
  },
%%
  tmpchangeset/.style={
    obschangeset,
    postaction={
      decorate,
      decoration={
        markings,
        mark=at position 0.5 with {\node[upperT] {\tiny{\textbf{T}}};},
      },
    },
  },
  tmpchangeset/.default={black},
%%
  nodenote/.style={
    fill=red!20,
    line width=2mm
  },
%%
  edge/.style={
    draw=#1,
    latex-,
    thick
  },
  edge/.default={black},
%%
  obsedge/.style={
    draw=#1,
    latex-,
    thick
  },
  obsedge/.default={black},
%%
  markeredge/.style={
    draw=#1,
    latex-,
    thick,
    dotted
  },
  markeredge/.default={black},
%%
  poof/.style={
    draw,
    starburst,
    line width=1pt,
    starburst points=11,
    starburst point height=0.35cm,
    inner sep=0.05cm,
  },
}
'''

BITBUCKET_TIKZ = r'''
\definecolor{bbblue}{RGB}{86,175,228}
\definecolor{bbgreen}{RGB}{158,198,28}
\definecolor{bbpurple}{RGB}{172,116,176}
\tikzset{
  changeset/.style={
    draw=#1!60,
    fill=#1!30,
    line width=1mm,
    minimum width=3em,
    minimum height=2em,
    circle,
    outer sep=1.5mm,
  },
  changeset/.default={gray},
%%
  obschangeset/.style={
    changeset,
    dashed,
  },
  obschangeset/.default={black},
%%
  upperT/.style={
    fill=white,
    minimum width=0,
    minimum height=0,
  },
%%
  tmpchangeset/.style={
    obschangeset,
    postaction={
      decorate,
      decoration={
        markings,
        mark=at position 0.1 with {\node[upperT] {\tiny{\textbf{T}}};},
      },
    },
  },
  tmpchangeset/.default={black},
%%
  nodenote/.style={
    rounded corners,
    draw=#1!80,
    fill=#1!20,
    line width=2pt,
    inner sep=6pt,
  },
  nodenote/.default={bbgreen},
  bugnode/.style={
    changeset=bbblue,
  },
  masternote/.style={
    nodenote=bbpurple,
  },
  masternode/.style={
    changeset=bbpurple,
  },
%%
  edge/.style={
    draw=#1,
    to-,
    line width=3pt,
  },
  edge/.default={gray!80},
%%
  obsedge/.style={
    edge,
  },
  obsedge/.default={gray!80},
%%
  markeredge/.style={
    edge,
    dotted
  },
  markeredge/.default={gray!80},
%%
  poof/.style={
    draw=gray!80,
    fill=gray!20,
    line width=2pt,
    starburst,
    starburst points=11,
    starburst point height=0.35cm,
    inner sep=0.05cm,
  },
}
'''

DOC_BODY = r'''
\begin{document}
\begin{tikzpicture}
%s
\end{tikzpicture}
\end{document}
'''

DEFAULT_LIBS = ('arrows.meta, fadings, graphs, shapes, '
                'decorations.markings, calc')

def dag_style(self):
    if not self.builder.config.dag_latex_preamble:
        self.builder.config.dag_latex_preamble = DEFAULT_TIKZ
    elif self.builder.config.dag_latex_preamble == 'bitbucket':
        self.builder.config.dag_latex_preamble = BITBUCKET_TIKZ
    return self.builder.config.dag_latex_preamble

def render_dag(self, dag, libs=''):
    hashkey = dag.encode('utf-8')
    fname = 'asciidag-%s.png' % (sha(hashkey).hexdigest())
    # if we're converting to svg, then we use a different extension
    if 'svg' in self.builder.config.dag_proc_suite:
        fname = 'dag-%s.svg' % (sha(hashkey).hexdigest())
    relfn = posixpath.join(self.builder.imgpath, fname)
    outfn = os.path.join(self.builder.outdir, '_images', fname)

    if os.path.isfile(outfn):
        return relfn

    if hasattr(self.builder, '_dag_warned'):
        return None

    ensuredir(os.path.dirname(outfn))
    curdir = os.getcwd()

    if not libs:
        libs = DEFAULT_LIBS
    latex = DOC_HEAD % libs
    latex += dag_style(self)
    latex += DOC_BODY % dag
    if isinstance(latex, unicode):
        latex = latex.encode('utf-8')

    if not hasattr(self.builder, '_dag_tempdir'):
        tempdir = self.builder._dag_tempdir = tempfile.mkdtemp()
    else:
        tempdir = self.builder._dag_tempdir

    os.chdir(tempdir)

    tf = open('asciidag.tex', 'wb')
    tf.write(latex)
    tf.close()

    def run_cmd(cmd, *args):
        cmds = [cmd] + list(args)
        procs = []
        prev = None
        stdout = None

        for cmd in cmds:
            try:
                os.chdir(tempdir)
                proc = Popen(cmd, stdin=prev, stdout=PIPE, stderr=PIPE)
                prev = proc.stdout
                procs += [proc]
            except OSError, e:
                if e.errno != ENOENT:  # No such file or directory
                    raise
                msg = '%s command cannot be run' % cmd[0]
                self.builder.warn(msg)
                self.builder._dag_warned = True
                raise DagExtError(msg)
            finally:
                os.chdir(curdir)

        for p, cmd in reversed(zip(procs, cmds)):
            dummy, stderr = p.communicate()
            if stdout is None:
                stdout = dummy
            if p.returncode != 0:
                msg = ('Error (asciidag extension): %s exited with\n'
                       '[stderr]\n%s\n'
                       '[stdout]\n%s\n'
                       '[tmpdir]\n%s')
                raise DagExtError(msg % (cmd[0], stderr, stdout, tempdir))
        return stdout

    run_cmd(['pdflatex', '--interaction=nonstopmode', 'asciidag.tex'])
    run_cmd(['pdftoppm', '-r', '120', 'asciidag.pdf', 'asciidag'])

    os.chdir(tempdir)
    if self.builder.config.dag_proc_suite == 'ImageMagick':
        convert_args = []
        if self.builder.config.dag_transparent:
            convert_args = ['-fuzz', '2%', '-transparent', 'white']

        run_cmd(['convert', '-trim'] + convert_args + ['asciidag-1.ppm', outfn])

    elif self.builder.config.dag_proc_suite == 'pdf2svg':
        run_cmd(['pdf2svg', 'asciidag.pdf', outfn])

    elif self.builder.config.dag_proc_suite == 'Netpbm':
        pnm_args = []
        if self.builder.config.dag_transparent:
            pnm_args = ['-transparent', 'white']

        pngdata = run_cmd(['pnmcrop', 'dag-1.ppm'], ['pnmtopng'] + pnm_args)

        f = open(outfn, 'wb')
        f.write(pngdata)
        f.close()

    else:
        self.builder._dag_warned = True
        os.chdir(curdir)
        raise DagExtError('Error (asciidag extension): Invalid configuration '
                          'value for dag_proc_suite')

    os.chdir(curdir)
    return relfn

def html_visit_dag(self, node):
    libs = self.builder.config.dag_tikzlibraries
    if node.get('libs'):
        libs += ',' + node.get('libs')
    libs = libs.replace(' ', '').replace('\t', '').strip(', ')
    fname = None
    dag = dagmatic.parse(node.get('dag', '')).tikz_string()
    caption = node.get('caption')
    bugfixed = node.get('bugfixed', False)

    try:
        fname = render_dag(self, dag, libs)
    except DagExtError, exc:
        info = str(exc)[str(exc).find('!'):-1]
        sm = nodes.system_message(info, type='WARNING', level=2,
                                  backrefs=[], source=dag)
        sm.walkabout(self)
        self.builder.warn('could not compile latex:\n'
                          '-----\n'
                          '%s\n'
                          '-----\n'
                          'Error message: %s' % (dag, str(exc)))
        raise nodes.SkipNode

    if fname is None:
        # something failed -- use text-only as a bad substitute
        self.body.append('<span class="math">%s</span>' %
                         self.encode(dag).strip())
    else:
        if node.tagname == 'dag':
            self.body.append(self.starttag(node, 'div', CLASS='figure'))
            self.body.append('<p>')
        self.body.append('<img src="%s" alt="%s" /></p>\n' %
                         (fname, self.encode(node['dag']).strip()))
        if caption and not bugfixed:
            # convert the caption to html
            caption = core.publish_parts(node['caption'],
                                         writer_name='html')['body']
            self.body.append('<p class="caption">%s</p>' %
                             caption.strip())
        if node.tagname == 'dag':
            self.body.append('</div>')
    raise nodes.SkipNode

def latex_visit_daginline(self, node):
    dag = dagmatic.parse(node.get('dag', '')).tikz_string()
    self.body.append(dag_style(self))
    self.body.append(r'\tikz{%s}' % dag)
    raise nodes.SkipNode

def latex_visit_dag(self, node):
    latex = dag_style(self)
    dag = dagmatic.parse(node.get('dag', '')).tikz_string()
    if node['caption']:
        caption = core.publish_parts(node['caption'],
                                     writer_name='latex')['body']
        latex += '\\begin{figure}[htp]\\centering\\begin{tikzpicture}' + \
                 dag + '\\end{tikzpicture}' + '\\caption{' + \
                 caption.strip() + '}\\end{figure}'
    else:
        latex += '\\begin{center}\\begin{tikzpicture}' + dag + \
                 '\\end{tikzpicture}\\end{center}'
    self.body.append(latex)

def depart_dag(self, node):
    pass

def cleanup_tempdir(app, exc):
    if exc:
        return
    if not hasattr(app.builder, '_dag_tempdir'):
        return
    try:
        shutil.rmtree(app.builder._dag_tempdir)
    except Exception:
        pass

def which(program):
    for path in os.environ["PATH"].split(":"):
        if os.path.exists(path + "/" + program):
            return path + "/" + program

    return None

def setup(app):
    app.add_node(dag,
                 html=(html_visit_dag, depart_dag),
                 latex=(latex_visit_dag, depart_dag))
    app.add_node(daginline,
                 html=(html_visit_dag, depart_dag),
                 latex=(latex_visit_daginline, depart_dag))
    app.add_role('dag', dag_role)
    app.add_directive('dag', DagDirective)
    app.add_config_value('dag_latex_preamble', '', 'env')
    app.add_config_value('dag_tikzlibraries', '', 'env')
    app.add_config_value('dag_transparent', True, 'env')

    # this needs to be set early; if the user specifies a preamble in conf.py
    # then this is overwritten
    latex = app.config['latex_elements']
    if not latex.get('preamble'):
        latex['preamble'] = r'\usepackage{tikz}'
        latex['preamble'] += r'\usetikzlibrary{%s}' % DEFAULT_LIBS

    # fallback to another value depending what is on the system
    suite = 'pdf2svg'
    if not which('pdf2svg'):
        suite = 'Netpbm'
        if not which('pnmcrop'):
            suite = 'ImageMagick'
    app.add_config_value('dag_proc_suite', suite, 'html')
    app.connect('build-finished', cleanup_tempdir)
