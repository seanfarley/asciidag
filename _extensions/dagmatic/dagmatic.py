#!/usr/bin/env python

from __future__ import print_function

import sys
import re
import cStringIO

from nodes import TransitionText, Node, Style
from edges import types

# We're looking for node labels (runs of alphanumeric chars) and the edges
# between them. E.g. given a line like "  \ a-b  :", the tokens of interest
# are \, a, -, b, :. This regex is a good place to start (but now we have
# two problems).
nodefind_re = re.compile(r'([a-zA-Z0-9\'^]+)')


def parse(text):
    '''Read a sequence of lines. Return a DAGList.
    '''
    # First step: turn input lines into a "grid" of character cells.
    # grid[i][j] tells us what is occupying cell (i,j): either a node
    # or a single non-node character.
    text = text.splitlines()
    grid = _read_grid(text)
    nodes = []

    # Now turn the grid into an AST-like thing: the DAGList.
    for (row, line) in enumerate(grid):
        for (col, ch) in enumerate(line):
            ch.parse(nodes, grid, row, col)

    nodemap = {str(node): node for node in nodes}
    return DAG(nodemap)


def _read_grid(infile):
    grid = []
    style = ''
    for line in infile:
        grid.append([])
        currow = grid[-1]
        if line.lstrip().startswith('||'):
            ws, text = line.split('||')
            currow += [types[c] for c in ws]
            currow += [types['||'], TransitionText(text.strip())]
        elif line.lstrip().startswith('{') or style:
            style += line.strip()
            if line.rstrip().endswith('}'):
                nodestyle = Style()
                # parse the dictionary
                style = style.strip('{')
                style = style.strip('}')
                for kv in style.split(','):
                    if not kv.strip():
                        continue
                    key, val = kv.split(':', 1)
                    nodestyle[key.strip()] = val.strip()
                currow += [nodestyle]

                style = ''
        else:
            chunks = nodefind_re.split(line.rstrip())

            for (idx, chunk) in enumerate(chunks):
                if idx % 2 == 1:  # must be a node (run of alphanumeric)
                    node = Node(chunk)
                    currow += [node] * len(chunk)
                else:
                    # Must preserve every input char because of the visual
                    # nature of the input language -- need grid[i][j] to be
                    # useful!
                    currow += [types[c] for c in chunk]
    return grid


class DAG(object):
    '''A graph of nodes. Actually this is two overlaid graphs: the traditional
    DAG of parent/child relationships, and the newfangled directed cyclic
    graph of obsolescence markers.
    '''
    def __init__(self, nodemap):
        self.nodemap = nodemap              # map node name to Node
        self._nodes = None

    @property
    def nodes(self):
        if self._nodes is None:
            self._nodes = [n.name for n in self.nodemap.values()]
        return self._nodes

    def __getitem__(self, name):
        '''a naive way to get a node: search for the exact name, fallback
        to searching through all the nodes
        '''
        ret = self.nodemap.get(name)
        if ret is None:
            for n in self.nodemap.values():
                if n.name == name:
                    ret = n
                    break
        return ret

    def get_parent_names(self, name):
        '''return parents of specified node as str (node names)'''
        return [parent.name
                for parent in self[name].parents]

    def get_precursor_names(self, name):
        '''return precursors of specified node as str (node names)'''
        return [precursor.name
                for precursor in self[name].precursors]

    def dump(self, outfile):
        for node in self.nodemap.values():
            parents = ','.join(str(p) for p in node.parents)
            obs = ''
            if node.precursors:
                precursors = ','.join(str(p) for p in node.precursors)
                obs = ' (obsoletes %s)' % (precursors,)
            print('%s[%d, %d] -> %s%s' % (node, node.row, node.col, parents,
                                          obs), file=outfile)

    def tikz(self, outfile):
        # need to do two passes so that all nodes are defined first
        for node in self.nodemap.values():
            node.tikz(outfile)

        for node in self.nodemap.values():
            # output the edges
            for p in node.parents:
                print(r'\draw[edge] (%s) -- (%s);' % (p, node), file=outfile)

            # output the obsolete edges
            for p in node.precursors:
                print(r'\draw[markeredge] (%s) -- (%s);' % (p, node),
                      file=outfile)

    def tikz_string(self):
        output = cStringIO.StringIO()
        self.tikz(output)
        return output.getvalue()

def main():
    dag = parse(sys.stdin.read())
    print('dag:')
    dag.dump(sys.stdout)


if __name__ == '__main__':
    main()
