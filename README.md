EPFL MyEdu Course Catalog
=========================

The MyEdu course catalog is a searchable database of courses offered at EPFL.  The catalog features a clutter-free interface that can be used to filter courses based on both basic and advanced search criteria.  This document presents the steps involved in deploying the service on the Google App Engine infrastructure, as well as updating the course database. 

Deploying on Google App Engine
------------------------------

The following instructions assume basic knowledge of Google App Engine.  For a good introductory material, check out the official App Engine tutorial for Python.

The catalog application code resides under the ``app/`` directory in the repository.

1. Create a new Google App Engine project.  The project must use the High Replicated Datastore (which is by default for new projects).
2. Edit the ``app.yaml`` file and change the name of the application to the name of your project.
3. Deploy the application code (including the backends).  From the command line, you can run ``appcfg.py update`` and ``appcfg.py backends update``.

At this point, the application should be functional, but there is no course information to search.  Let us populate the database.


Using Google Site Search
------------------------


Updating the Course Information
-------------------------------
