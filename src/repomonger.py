# Example config file for a repo.  Used by repomonger to assemble the repo
# and present it via an http server
# You can easily peel packages out of a koji build system, or a local repo copy
# for repomonger.

[reponame]
httpserver = 'http://yourhttpserver.com'
baseloc: %(httpserver)s/whatever
repo_dir = <Destdir for repo>
reponame: <Some name>
# RPM package location base

[backend]
#What db type used, flatfile, mongodb are currently the options
db_type: flatfile

database: <filename>
# where the list of packages is, file for flat, collection/db for mongo

