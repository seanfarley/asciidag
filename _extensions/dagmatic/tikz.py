#!/usr/bin/env python

from __future__ import print_function

import dagmatic

tikzdoc = r'''
\documentclass[tikz]{standalone}

\usetikzlibrary{arrows.meta, fadings, graphs, shapes,
                decorations.markings, calc}

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
}

\begin{document}

\begin{tikzpicture}

%s

\end{tikzpicture}
\end{document}
'''

if __name__ == '__main__':
    asciidag = r'''
  a-b

  || hg commit --amend
  || (safe, using evolve)

  a-b-c^T
   \:>
    d
'''

    dag = dagmatic.parse(asciidag)
    print(tikzdoc % dag.tikz_string())
