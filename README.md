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
the rest of the document, we assume the project name is ``[app_id]``.

2. Edit the ``app.yaml`` file and change the name of the application
to ``[app_id]``.

3. Deploy the application code (including the backends).  From the
command line, you can run ``appcfg.py update`` and ``appcfg.py
backends update``.

At this point, the application should be accessible at http://[app
id].appspot.com, but the database is empty.  In order to populate it,
perform the following steps:

1. Visit http://admin.[app_id].appspot.com/admin/reinit/en, followed
by http://admin.[app_id].appspot.com/admin/reinit/fr to import all
courses in the database.

2. Visit http://admin.[app_id].appspot.com/admin/index/erase, followed
by http://admin.[app_id].appspot.com/admin/index/rebuild to index all
courses in the database using App Engine's search facility.

At this point, the search function of the catalog should be
functional.  There are still some features missing, like
autocorrecting spelling mistakes, which are covered by an external
Google search service (see the next section).


Using Google Site Search
------------------------

For accurate search results, the MyEdu catalog combines results from
two search providers: the internal App Engine search API and an
external Google Site Search service.  If the former service yields no
results (e.g., because of a typo in the query), the second service is
used.

Here are the steps to set up Google Site Search with the MyEdu
catalog:

1. Obtain a Google Site Search account (it is a paid service).

2. Configure the service to index the pages following the pattern
``[app_id].appspot.com/*/course/*``.  The indexing will not be
immediate; it typically takes a few days until the crawling is
complete.

3. Update the ``SEARCH_ENGINE_ID`` variable in
``app/epfl/courses/config.py`` with your own Site Search ID, which you
can obtain from the Site Search configuration page.


Updating the Course Information
-------------------------------

The official EPFL course information is offered on IS-Academia pages.
The MyEdu course catalog obtains its information by downloading
(crawling) all the HTML pages of the courses available, and then
extracting the various pieces of information on each page (title,
semester, credits, description, etc.)

This process is automated through a set of Python scripts available in
the ``crawl/`` directory.  To avoid straining the ISA servers, the
crawling scripts are design to fetch one request at a time.  Crawling
all courses of ISA typically takes a few hours when ran on a
connection with fast access to the EPFL servers. Moreover, once
fetched, all the web pages are cached locally, so any modification of
the crawling scripts would not trigger a recrawl.

To crawl and update the course information on MyEdu:

1. Run on your local machine the
``crawl/2012-2013/parse_study_plans.py``, followed by
``crawl/2012-2013/consolidate_courses.py``.  The first script
downloads locally all course information and assembles it into a
single large JSON document, while the second script merges duplicate
course information into a final JSON document called
``consolidated_desc.json``.

2. Copy the generated ``consolidated_desc.json`` file to the
``app/data/`` directory.

3. Re-upload the application to Google App Engine.

4. Rebuild the existing course information by following the steps
presented in the first section.
