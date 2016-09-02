Repo-Monger is a first attempt at making a lightweight yum repo manager.

I find myself needing to create clones of existing repos, with one or two
changes for testing, then blow them away and update the main repo.  This is a
pain to do manually, thus bringing us to Repo-monger.  It is an attempt to make
a lightweight yum repo manager, with the features I need, but lacking the
breadth of toolsets such as pulp, or Spacewalk.  Those are good tools, but they
have a lot more features than I need, and do a whole lot more than mere repo
management. (And require a fair bit more in the way of setup and support)

The goals for repo-monger are as follows.

Assemble yum repos based on simple list of packages and location, using soft
links to point to the files in question, without wasting space (and time)
copying them around. Each repo is configured by a simple text file, that can be
machine generated from sources such as koji. Repo-monger will create the
directory structure, and link the relevant files, then run createrepo on the
resultant tree.  Producing a yum repo that can be served with any decent http
server.

Alternatively, clone an existing repo in a new location, useful when doing
cascade style updates, but you want to be able to freeze the original repo
while you work on issues.

[TODO] Mongo backend?


usage: repomonger.py [-h] [-n] [-d] [-C] [-c CONFIG] [-R REPO]
                     [-S SOURCE_REPO] [-D DESTDIR] [-l LINKTYPE]

Time to build a yum repo
```
optional arguments:
  -h, --help            show this help message and exit
  -n, --dry-run         Dry run, do not actually perform action
  -d, --debug           Enable debugging during execution.
  -C, --clone           clone existing repo rather than create from a list of
                        pkgs
  -c CONFIG, --config CONFIG
                        Specify a path to an alternate config file
  -R REPO, --repo REPO  Name of repo to build. See definition in config
  -S SOURCE_REPO, --src SOURCE_REPO
                        Repo to clone.
  -D DESTDIR, --dst DESTDIR
                        Topdir of cloned repo
  -l LINKTYPE, --linktype LINKTYPE
                        symlink, hardlink, or copy
```
