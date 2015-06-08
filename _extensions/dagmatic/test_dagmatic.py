import nose.tools as nt

import dagmatic


def test_readme_1_simple():
    input = r'''
   a-b-c
      \
       d-e
'''
    dag = _parse_one(input)
    nt.assert_items_equal(dag.nodes, ['a', 'b', 'c', 'd', 'e'])
    _assert_parents(dag, 'a', [])
    _assert_parents(dag, 'b', ['a'])
    _assert_parents(dag, 'c', ['b'])
    _assert_parents(dag, 'd', ['b'])
    _assert_parents(dag, 'e', ['d'])


def test_readme_2_obsolescence():
    input = r'''
  a-b-c
   \: :
    d-e
'''
    dag = _parse_one(input)
    nt.assert_items_equal(dag.nodes, ['a', 'b', 'c', 'd', 'e'])
    _assert_parents(dag, 'd', ['a'])
    _assert_precursors(dag, 'a', [])
    _assert_precursors(dag, 'b', [])
    _assert_precursors(dag, 'c', [])
    _assert_precursors(dag, 'd', ['b'])
    _assert_precursors(dag, 'e', ['c'])


def test_merge():
    input = r'''
a-b-3-x
 \ \
  7-1-f-5
'''
    dag = _parse_one(input)
    _assert_parents(dag, '1', ['b', '7'])


def test_multiple_roots():
    input = r'''
1-2-3
     \
  4-5-6-7
'''
    dag = _parse_one(input)
    _assert_parents(dag, '1', [])
    _assert_parents(dag, '4', [])
    _assert_parents(dag, '6', ['3', '5'])


def test_the_whole_enchilada():
    # a merge! multiple roots! obsolescence!
    input = r'''
a-b-3-x
 \ \
  c-1-f-5
        :
        6-7-8
'''
    dag = _parse_one(input)
    _assert_parents(dag, 'a', [])
    _assert_parents(dag, 'c', ['a'])
    _assert_parents(dag, 'b', ['a'])
    _assert_parents(dag, '1', ['c', 'b'])
    _assert_parents(dag, '6', [])
    _assert_precursors(dag, 'x', [])
    _assert_precursors(dag, '6', ['5'])
    _assert_precursors(dag, '7', [])

def test_text_transition():
    input = r'''
  a-b

  || hg commit --amend
  || (safe, using evolve)

  a-b.c
   \:
    b'
'''
    dag = _parse_one(input)
    _assert_parents(dag, 'a', [])
    _assert_parents(dag, 'b', ['a'])
    _assert_parents(dag, "b'", ['a'])
    _assert_parents(dag, 'c', [])
    _assert_precursors(dag, 'a', [])
    _assert_precursors(dag, "b'", ['b'])
    _assert_precursors(dag, 'c', ['b'])


def test_diagonal_obsolete_markers():
    input = r'''
      f
      |
    d-e
   /
  a-b-c^T
   <:>
    b'
'''
    dag = _parse_one(input)
    _assert_parents(dag, 'a', [])
    _assert_parents(dag, 'b', ['a'])
    _assert_parents(dag, 'c', ['b'])
    _assert_parents(dag, "b'", [])
    _assert_precursors(dag, "b'", ['a', 'b', 'c'])
    _assert_obsolete(dag, ['a', 'b', 'c'])


def _parse_one(text):
    return dagmatic.parse(text)


def _assert_parents(dag, name, expect):
    actual = dag.get_parent_names(name)
    nt.assert_items_equal(actual, expect)


def _assert_precursors(dag, name, expect):
    actual = dag.get_precursor_names(name)
    nt.assert_items_equal(actual, expect)

def _assert_obsolete(dag, name):
    for i in name:
        nt.assert_items_equal([dag[i].obsolete], [True])
