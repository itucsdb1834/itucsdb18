 Guide
===============

Database Design
---------------

We have 9 tables in this Web Project and you can see the distribution below.

Database Table Distribution
^^^^^^^^^^^^^^^^^^^

:Idil Ugurnal:

   * news_table
   * user_table
   * event_table
   * group_user

:Cagla Kaya:

   * group_table
   * comment_table
   * request_table
   * upvote_table
   * event_user

Developer

Code
----

Profile DB initialization:

   .. code-block:: python

      class Profile(object):
    def __init__(self, username):
        self.username = username
        self._profileID =  None
        self.name =  None
        self.surname =  None
        self.age =  None
        self.gender =  None
        self.country =  None
        self.city = None
        self.hobbies =  None
        self.description =  None
        self.email =  None
        self.unread_messages = None
        self.get_unread_message_no()



::

   .. code-block:: python

      class Profile(object):
    def __init__(self, username):
        self.username = username
        self._profileID =  None
        self.name =  None
        self.surname =  None
        self.age =  None
        self.gender =  None
        self.country =  None
        self.city = None
        self.hobbies =  None
        self.description =  None
        self.email =  None
        self.unread_messages = None
        self.get_unread_message_no()



.. toctree::

   Idil
   Cagla
