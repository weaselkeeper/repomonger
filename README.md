Repo-Monger is a first attempt at making a lightweight yum repo manager.

I find myself needing to create clones of existing repos, with one or two
changes for testing, then blow them away and update the main repo.  This is a 
pain to do manually, thus bringing us to Repo-monger.  It is an attempt to make
a lightweigh yum repo manager, with the features I need, but lacking the breadth
of toolsets such as pulp, or Spacewalk.  Those are good tools, but they have a
lot more features than I need, and do a whole lot more than mere repo management.

The goals for repo-monger are as follows.

Assemble yum repos based on simple key=value list of package name and location, 
using soft links to point to the files in question, without wasting space (and time)
copying them around. Each repo is configured by a simple text file, that can 
be machine generated from sources such as koji. Repo-monger will create the directory
structure, and link the relevant files, then run createrepo on the resultant tree.
Producing a yum repo that can be served with any decent http server.

Alternatively, clone an existing repo in a new location, useful when doing cascade
style updates, but you want to be able to freeze the original repo while you
work on issues.

Alternatively, each repo can be a document in a mongodb instance, but that's
for the future



