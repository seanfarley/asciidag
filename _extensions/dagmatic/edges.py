import nodes


class Spacer(object):
    def __init__(self, edge):
        self.edge = edge

    def parse(self, nodes, grid, row, col):
        pass

    def __str__(self):
        return self.edge

    def __repr__(self):
        return '<Edge: %s>' % (self.edge,)


class Edge(Spacer):
    def checkbounds(self, grid, row, col):
        pass

    def checknodes(self, n1, n2, row, col):
        '''every edge needs to connect two nodes'''
        if not (isinstance(n1, nodes.Node) and isinstance(n2, nodes.Node)):
            raise nodes.DAGSyntaxError(row, col,
                                       '%s connected to garbage' % self)

    def parsenodes(self, grid, row, col):
        return None, None

    def connect(self, parent, child):
        child.parents.append(parent)
        return parent, child

    def parse(self, nodes, grid, row, col):
        self.checkbounds(grid, row, col)
        parent, child = self.parsenodes(grid, row, col)
        self.checknodes(parent, child, row, col)

        return self.connect(parent, child)


class Marker(Edge):
    def connect(self, parent, child):
        child.precursors.append(parent)
        parent.obsolete = True
        return parent, child


class HorizontalEdge(Edge):
    def __init__(self, edge='-'):
        super(HorizontalEdge, self).__init__(edge)

    def __str__(self):
        return 'horizontal edge'

    def __repr__(self):
        return '<HorizontalEdge>'

    def checkbounds(self, grid, row, col):
        if col == 0:
            raise nodes.DAGSyntaxError(row, col, '%s start of line' % self)
        elif col == len(grid[row]) - 1:
            raise nodes.DAGSyntaxError(row, col, '%s end of line' % self)

    def parsenodes(self, grid, row, col):
        return grid[row][col - 1], grid[row][col + 1]


class VerticalEdge(Edge):
    def __init__(self, edge='|'):
        super(VerticalEdge, self).__init__(edge)

    def __str__(self):
        return 'vertical edge'

    def __repr__(self):
        return '<VerticalEdge>'

    def checkbounds(self, grid, row, col):
        if row == 0:
            raise nodes.DAGSyntaxError(row, col,
                                       '%s start on first line' % self)
        elif row == len(grid) - 1:
            raise nodes.DAGSyntaxError(row, col,
                                       '%s start on last line' % self)

    def parsenodes(self, grid, row, col):
        return grid[row + 1][col], grid[row - 1][col]

    def connect(self, parent, child):
        if child.parents:
            parent.parents.append(child)
        else:
            child.parents.append(parent)
        return parent, child


class LowerDiagonalEdge(Edge):
    def __init__(self, edge='\\'):
        super(LowerDiagonalEdge, self).__init__('\\')

    def __str__(self):
        return 'lower diagonal edge'

    def __repr__(self):
        return '<LowerDiagonalEdge>'

    def checkbounds(self, grid, row, col):
        if row == 0:
            raise nodes.DAGSyntaxError(row, col,
                                       '%s start on first line' % self)
        elif row == len(grid) - 1:
            raise nodes.DAGSyntaxError(row, col,
                                       '%s start on last line' % self)
        elif col == 0:
            raise nodes.DAGSyntaxError(row, col, '%s start of line' % self)
        elif col >= len(grid[row + 1]):
            raise nodes.DAGSyntaxError(row, col,
                                       '%s points past end of next line'
                                       % self)

    def parsenodes(self, grid, row, col):
        return grid[row - 1][col - 1], grid[row + 1][col + 1]


class UpperDiagonalEdge(Edge):
    def __init__(self, edge='/'):
        super(UpperDiagonalEdge, self).__init__('/')

    def __str__(self):
        return 'upper diagonal edge'

    def __repr__(self):
        return '<UpperDiagonalEdge>'

    def checkbounds(self, grid, row, col):
        if row == 0:
            raise nodes.DAGSyntaxError(row, col,
                                       '%s start on first line' % self)
        elif row == len(grid) - 1:
            raise nodes.DAGSyntaxError(row, col,
                                       '%s start on last line' % self)
        elif col == 0:
            raise nodes.DAGSyntaxError(row, col,
                                       '%s start of line' % self)
        elif col >= len(grid[row - 1]):
            raise nodes.DAGSyntaxError(row, col,
                                       '%s points past end of next line'
                                       % self)

    def parsenodes(self, grid, row, col):
        return grid[row + 1][col - 1], grid[row - 1][col + 1]


class HorizontalMarker(HorizontalEdge, Marker):
    def __init__(self, edge='.'):
        super(HorizontalMarker, self).__init__('.')

    def __str__(self):
        return 'horizontal marker'

    def __repr__(self):
        return '<HorizontalMarker>'


class VerticalMarker(VerticalEdge, Marker):
    def __init__(self, edge=':'):
        super(VerticalMarker, self).__init__(':')

    def __str__(self):
        return 'vertical marker'

    def __repr__(self):
        return '<VerticalMarker>'

    def parsenodes(self, grid, row, col):
        return grid[row - 1][col], grid[row + 1][col]

    def connect(self, parent, child):
        child.precursors.append(parent)
        parent.obsolete = True
        return parent, child

class LowerDiagonalMarker(LowerDiagonalEdge, Marker):
    def __init__(self, edge='<'):
        super(LowerDiagonalMarker, self).__init__('<')

    def __str__(self):
        return 'lower diagonal marker'

    def __repr__(self):
        return '<LowerDiagonalMarker>'


class UpperDiagonalMarker(UpperDiagonalEdge, Marker):
    def __init__(self, edge='>'):
        super(UpperDiagonalMarker, self).__init__('>')

    def __str__(self):
        return 'upper diagonal marker'

    def __repr__(self):
        return '<UpperDiagonalMarker>'

    def parsenodes(self, grid, row, col):
        return grid[row - 1][col + 1], grid[row + 1][col - 1]

types = {
    '': Spacer(''),
    ' ': Spacer(' '),
    '||': Spacer('||'),
    '-': HorizontalEdge(),
    '|': VerticalEdge(),
    '\\': LowerDiagonalEdge(),
    '/': UpperDiagonalEdge(),
    '.': HorizontalMarker(),
    ':': VerticalMarker(),
    '<': LowerDiagonalMarker(),
    '>': UpperDiagonalMarker(),
}
