Developer Guide
===============

Database Design
---------------

**We have 9 tables in total. Among these tables, 6 have 5 non-key elements and 3 are intermediary tables. You can see the explanation of the tables and the distribution below.**

Database Distribution
---------------------

:Idil Ugurnal:

   * user_table --> User and profile information are stored in this table.
   * news_table --> Notifications are stored in this table.
   * event_table --> Events and their information are stored in this table.
   * group_user --> Users that are added in a particular group are stored in this table
   * event_user --> Users that are added in a particular event are stored in this table.


:Cagla Kaya:

   * group_table --> Groups, their information and their events are stored in this table.
   * comment_table --> Comments under events and their information are stored in this table.
   * request_table --> Requests under groups and their information are stored in this table.
   * upvote_table --> Upvoters for particular requests are stored in this table.


Code
----

**Below you can see the complete diagram of our Database Tables and their relations. **

.. figure:: pics/database_tables.png
   :scale: 50 %
   :alt: Database Relation

**Each members work is demonstrated on their own page. **

.. toctree::

   idil
   cagla
