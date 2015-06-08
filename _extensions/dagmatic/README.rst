dagmatic
========

dagmatic is a tool to parse a custom ASCII-art representation of Mercurial
repositories and render them in a variety of forms (none implemented yet, but
SVG is the primary goal).

The input language looks like this::

   a-b-c
      \
       d-e

meaning:

  * ``a`` is the parent of ``b``
  * ``b`` is the parent of ``c`` and ``d``
  * ``d`` is the parent of ``e``

History goes left-to-right and top-to-bottom. Currently, there are a few ways
to express a parent-child relationship: horizontal (``-``), vertical (``|``)
lower diagonal (``\``), upper diagonal (``/``). This might change in future.

dagmatic also lets you express changeset obsolescence (ie.
precursor/successor relationships)::

  a-b-c
   \: :
    d-e

Here, ``d`` is the successor of ``b`` and ``e`` is the successor of ``c``. You
can also specify diagonal markers::

  a-b-c
   \:>
    d

Now, ``d`` is the successor of both ``b`` and ``c``. The current ways to
express a precursor-successor relationship are: horizontal (``.``), vertical
(``:``), lower diagonal (``<``) and upper diagonal (``>``) (think of just the
lower part of the angle bracket). This might change in the future.

dagmatic will also let you describe a series of DAGs using a
transition marker::

  a-b

   || hg commit

  a-b-c


Usage
-----

Too early to document. See the source code.


TODO
----

  * use visitor pattern insteatd of tikz() method
  * use state pattern for parsing


Credits, contacts
-----------------

Written by Greg Ward and Sean Farley, based on an idea by Matt Mackall.

The canonical source repository is

  https://bitbucket.org/gward/dagmatic

with mirrors:

  http://hg.gerg.ca/dagmatic


License
-------

Copyright © 2015, Greg Ward and Sean Farley.
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are
met:

1. Redistributions of source code must retain the above copyright
   notice, this list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright
   notice, this list of conditions and the following disclaimer in the
   documentation and/or other materials provided with the
   distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

