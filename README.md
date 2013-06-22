EPFL MyEdu Course Catalog
=========================

The MyEdu course catalog is a searchable database of courses offered
at EPFL.  The catalog features a minimalist interface that can be used
to filter courses based on both basic and advanced search criteria.

This document presents the steps involved in deploying the service on
the Google App Engine infrastructure, as well as updating the course
database.

Note: The code has not been thoroughly tested and may crash.  Contact
stefan.bucur@epfl.ch for any questions or problems.

Deploying on Google App Engine
------------------------------

The following instructions assume basic knowledge of Google App
Engine.  For a good introductory material, check out the official App
Engine tutorial for Python.

The catalog application code resides under the ``app/`` directory in
the repository.

1. Create a new Google App Engine project.  The project must use the
High Replicated Datastore (which is by default for new projects).  In
the rest of the document, we assume the project name is ``[app id]``.

2. Edit the ``app.yaml`` file and change the name of the application
to ``[app id]``.

3. Deploy the application code (including the backends).  From the
command line, you can run ``appcfg.py update`` and ``appcfg.py
backends update``.

At this point, the application should be accessible at http://[app
id].appspot.com, but the database is empty.  In order to populate it,
perform the following steps:

1. Visit http://admin.[app id].appspot.com/admin/reinit/all to import
all courses in the database.

2. Visit http://admin.[app id].appspot.com/admin/index/all to index
all courses in the database using App Engine's search facility.

Using Google Site Search
------------------------

The feature is optional, can be disabled in code.  Otherwise, it
requires a (paid) subscription to Google Site Search, which must be
configured to index the domain where the application is serving from.
The indexing is not immediate, it typically takes a few days until the
crawling is complete.


Updating the Course Information
-------------------------------

The official EPFL course information is offered on IS-Academia. To
avoid straining the ISA servers, the crawling scripts were design to
fetch one request at a time.  Crawling all courses of ISA typically
takes a few hours when ran on a connection with fast access to the
EPFL servers. Moreover, once fetched, all the web pages are cached
locally, so any modification of the crawling scripts would not trigger
a recrawl.
