.. Bitbucket Documentation documentation master file, created by
   sphinx-quickstart on Mon Jun  1 17:16:11 2015.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Using Git branches
==================

Now that you’ve got a local and remote repository, and learned how to push and
pull files, it’s time to learn how to do development using branches.

About branches
--------------

In Git, branches are an integral part of your everyday workflow. Unlike SVN
where branches are generally used to capture the occasional large-scale
development effort.

.. dag::
   
   a-b
    \
     c

   {node: a, text: foo}


.. dag::
   
         q
         |
   a-b-3-x
    \ \
     c-1-f-5
           :
           6-7-8
               |
               m
   {node: q, text: bug fix 1, class: nodenote}
   {node: x, class: bugnode}
   {node: 8, class: masternode}
   {node: m, text: master, class: masternote}


.. dag:: Figure 1: unsafe history modification with core Mercurial (not
   using ``evolve``): the original revision 1 is destroyed.
   
   0-1

   || hg commit --amend
   || (destructive, not using evolve)

   0-p
    \
     1'
   {node: p, class: poof, text: poof!}



.. dag:: Figure 2: safe history modification using ``evolve``: the original
   revision 1 is preserved as an obsolete changeset. (The "temporary amend
   commit", marked with T, is an implementation detail stemming from
   limitations in Mercurial's current merge machinery. Future versions of
   Mercurial will not create them.)

   0-1

   || hg commit --amend
   || (safe, using evolve)

   0-1-2^T
    \:
     3
