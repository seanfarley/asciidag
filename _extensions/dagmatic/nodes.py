from __future__ import print_function


class DAGSyntaxError(Exception):
    def __init__(self, row, col, msg):
        self.row = row
        self.col = col
        self.msg = msg
        msg = 'Syntax error at (%d, %d): %s' % (row, col, msg)
        super(DAGSyntaxError, self).__init__(msg)


class Node(object):
    def __init__(self, name):
        self.name = name
        self._text = None
        self.parents = []               # list of Node
        self.precursors = []            # list of Node
        self.annotation = ''
        self.row = -1
        self.col = -1
        self.obsolete = False
        self._style = {}

        if '^' in name:
            self.name, self.annotation = name.split('^', 1)

        if self.annotation in ('O', 'T'):
            self.obsolete = True

    def __str__(self):
        return self.name + str(self.row * 10 + self.col)

    def __repr__(self):
        return '<Node: %s>' % (self.name,)

    @property
    def text(self):
        if self._text is None:
            self._text = self.name
            if 'text' in self._style:
                self._text = self._style['text']
        return self._text

    def parse(self, nodes, grid, row, col):
        # set the grid location into the node, if not already set
        if self.row == -1:
            self.row = row
        if self.col == -1:
            self.col = col
        if self not in nodes:
            nodes.append(self)

    def tikz(self, outfile):
        obs = ''
        if self.obsolete:
            obs = 'obs'
        if self.annotation == 'T':
            obs = 'tmp'

        cls = self._style.get('class') or obs + 'changeset'

        print(r'\node[%s] at (%d,%d) (%s) {%s};' % (cls, self.col, -self.row,
                                                    self, self.text),
              file=outfile)


class TransitionText(Node):
    def __init__(self, text):
        super(TransitionText, self).__init__('t')
        self._text = text

    def __repr__(self):
        return '<TransitionText: %s>' % (self.text,)

    def append(self, tnode):
        self._text += '\n' + tnode.text

    def parse(self, nodes, grid, row, col):
        super(TransitionText, self).parse(nodes, grid, row, col)
        try:
            # currently transition texts must be next to each other (no extra
            # new lines)
            prevtext = grid[row - 1][col]
            if isinstance(prevtext, TransitionText):
                prevtext.append(self)
                # remove from dag list since we're appending
                if self in nodes:
                    nodes.remove(self)
        except IndexError:
            # find the previous, longest row of nodes so that we can center the
            # double down arrow
            longrow = prevrow = []
            for r in xrange(row - 1, -1, -1):
                prevrow = [e for e in grid[r] if e]
                if len(prevrow) > len(longrow):
                    longrow = prevrow
            c = len(longrow)
            self.middle = [longrow[c / 2]]
            if not isinstance(self.middle, Node):
                self.middle = [longrow[c / 2 - 1], longrow[c / 2 + 1]]

    def tikz(self, outfile):
        anchor = r'($(%s.south)$)' % self.middle[0]
        if len(self.middle) > 1:
            anchor = r'$.5*(%s.south) + .5*(%s.south)$' % (self.middle[0],
                                                           self.middle[1])

        lines = self.text.splitlines()
        # the first line is a command, the rest are subtexts
        lines[0] = r'\small{\texttt{%s}}' % lines[0]
        for i in xrange(1, len(lines)):
            lines[i] = r'\scriptsize\emph{%s}' % lines[i]
        print('\\draw[double, double equal sign distance, -Implies] '
              '(%s,%d) -- node[anchor=west, align=left] (%s) {%s} '
              '++(0,%d);' % (anchor, -(self.row - 1), self,
                             '\\\\'.join(lines), -(len(lines) + 1)),
              file=outfile)


class Style(dict):
    def __repr__(self):
        return '<Style: %s>' % (dict.__repr__(self),)

    def parse(self, dag, grid, row, col):
        if 'node' not in self:
            raise DAGSyntaxError(row, col, 'style found but no node specified')

        for n in dag:
            if self['node'] == 'global' or n.name == self['node']:
                n._style = self
