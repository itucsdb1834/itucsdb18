Parts Implemented by Cagla
================================

Group Class
-----------

  .. code-block:: python
    class Group():
      def __init__(self, name, isprivate, owner, description, give_permission ,group_id,max_number):
        self.name = name
        self.isprivate = isprivate
        self.owner= owner
        self.description = description
        self.give_permission = give_permission
        self.group_id = group_id
        self.owner_name = None
        self.participants = []
        self.participant_no = 0
        self.max_number = max_number

      def read_with_id(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM group_table WHERE group_id = %s' , (self.group_id,))
            result = cursor.fetchone()
            self.name = result[1]
            self.isprivate = result[3]
            self.owner = result[4]
            self.description = result[6]
            self.give_permission = result[2]
            self.max_number = result[5]
            self.get_owner_name()
            self.get_participants()

      def get_owner_name(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT username FROM user_table WHERE userid = %s' , (self.owner,))
            self.owner_name = cursor.fetchone()[0]

      def add_participant(self, username):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT userid FROM user_table WHERE username = %s ' , (username, ))
            userid = cursor.fetchone()[0]
            if userid is None:
                return False
            if self.max_number > self.participant_no:
                cursor.execute('INSERT INTO group_user VALUES(%s,%s)' , (userid, self.group_id))
                self.participant_no += 1
                self.participants.append(username)
                self.get_owner_name()
                new = New(None, username ,self.owner_name, self.group_id,None, None, 'group' , 'joined', False, None,None )
                new.save_to_db()
                new_2 = New(None, username ,username, self.group_id,None, None, 'group' , 'joined', False, None,None )
                new_2.save_to_db()
            else:
                raise Exception('Group is already full no more place!')

      def check_participant(self, userid):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM group_user WHERE user_id = %s AND group_id=%s' , (userid, self.group_id ))
            if cursor.fetchone():
                return True
            else:
                return False

      def delete_group(self):
        self.get_owner_name()
        for participant in self.participants:
            new = New(None, self.owner_name, participant, self.group_id,None, None, 'group' , 'deleted', False, None,None )
            new.save_to_db()
        with ConnectionPool() as cursor:
            cursor. execute('DELETE FROM group_table WHERE group_id = %s' , (self.group_id,))
            cursor.execute('UPDATE news_table SET link = %s WHERE group_id IS NULL AND link IS NOT NULL ' , (None,))


      def update_group(self, name,isprivate,description,give_permission, max_number):
        if max_number < self.participant_no:
            raise Exception('You cannot decrease max_number for this group because there are already more participants. ')
        with ConnectionPool() as cursor:
            cursor. execute('UPDATE group_table SET group_name=%s, isprivate=%s, description=%s, max_number = %s, give_permission=%s WHERE group_id = %s' ,
                            (name, isprivate, description, max_number, give_permission, self.group_id,))
            self.name=name
            self.give_permission=give_permission
            self.isprivate=isprivate
            self.description=description
            self.max_number = max_number
        self.get_owner_name()
        for participant in self.participants:
            new = New(None, self.owner_name, participant,self.group_id,None, None, 'group' , 'updated', False, None,None )
            new.save_to_db()

      def get_participants(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT user_table.username FROM user_table RIGHT OUTER JOIN group_user ON group_user.user_id = user_table.userid WHERE group_user.group_id = %s ' , (self.group_id,))
            participants = cursor.fetchall()
        for participant in participants:
            self.participants.append(participant[0])
            self.participant_no = self.participant_no +1

      def save_to_db(self):
        with ConnectionPool() as cursor:
            cursor.execute('INSERT INTO group_table(group_name, isprivate, owner, description, give_permission,max_number) VALUES(%s,%s,%s,%s,%s,%s);',(self.name, self.isprivate , self.owner , self.description, self.give_permission,self.max_number))
            cursor.execute('SELECT group_id FROM group_table WHERE group_name = %s AND owner = %s', (self.name, self.owner))
            result = cursor.fetchone()
            self.group_id = result[0]
            cursor.execute('INSERT INTO group_user(group_id,user_id) VALUES(%s,%s);' , (self.group_id , self.owner))

   
    


Groups Class
-------------



.. code-block:: python
  class Groups():
    def __init__(self):
        self.arr = []

    def owned_groups(self,id):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM group_table WHERE owner = %s ' , (id,))
            groups = cursor.fetchall()
        for group in groups:
            group = Group(group[1] , group[3] , id , group[6] , group[2],group[0],group[5])
            self.arr.append(group)

    def my_groups(self,id):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT group_table.* FROM group_user LEFT OUTER JOIN group_table ON group_user.group_id=group_table.group_id '
                           'WHERE group_user.user_id = %s ', (id,))
            groups = cursor.fetchall()
        for group in groups:
            group = Group(group[1] , group[3] , id , group[6] , group[2],group[0],group[5])
            self.arr.append(group)

    def filtered_groups(self, option, input, userid):
        input = "%" + input + "%"
        if option == "Name":
            with ConnectionPool() as cursor:
                cursor.execute('SELECT * FROM group_table WHERE LOWER (group_name) LIKE LOWER (%s) AND '
                               '(isprivate=%s OR group_id IN (SELECT group_id FROM group_user WHERE user_id=%s))',
                               (input, False, userid))
                groups = cursor.fetchall()

        elif option == "Owner":
            with ConnectionPool() as cursor:
                cursor.execute(
                    'SELECT * FROM group_table WHERE owner IN (SELECT userid FROM user_table WHERE LOWER (username) LIKE LOWER (%s)) '
                    'AND (isprivate=%s OR group_id IN (SELECT group_id FROM group_user WHERE user_id=%s)) ',
                    (input, False))
                groups = cursor.fetchall()

        for group in groups:
            add_group = Group(group[1], group[3], id, group[6], group[2], group[0], group[5])
            self.arr.append(add_group)

Request Class
---------------



.. code-block:: python
  class Request():
    def __init__(self, request_id, name , owner, min_people, up_vote, explanation, group_id):
        self.request_id = request_id
        self.owner = owner
        self.name = name
        self.time_created = None
        self.min_people = min_people
        self.up_vote = up_vote
        self.explanation = explanation
        self.group_id = group_id
        self.upvoters = []


    def __repr__(self):
        return "<User {}>".format(self.name)

    def get_group_name(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT group_name FROM group_table WHERE group_id = %s' , (self.group_id,))
            return cursor.fetchone()[0]

    def save_to_db(self):
        self.time_created = datetime.datetime.now()
        with ConnectionPool() as cursor:
            cursor.execute('INSERT INTO request_table(owner, name, min_people, time_created, up_vote, explanation, group_id) VALUES(%s,%s,%s,%s,%s,%s,%s);',(self.owner, self.name , self.min_people , self.time_created, self.up_vote, self.explanation, self.group_id))
            cursor.execute('SELECT request_id FROM request_table WHERE name = %s AND owner = %s', (self.name, self.owner))
            self.request_id = cursor.fetchone()[0]
        group = Group(None,None,None,None,None,self.group_id,None)
        group.read_with_id()
        for participant in group.participants:
            new = New(None, self.owner, participant, self.group_id, None, None, 'group' , 'created request in', False,None,None )
            new.save_to_db()

    def get_upvoters(self):
        with ConnectionPool() as cursor:
            cursor.execute("SELECT username FROM user_table WHERE userid IN (SELECT user_id FROM upvote_table WHERE request_id = %s) ", (self.request_id,))
            upvoters = cursor.fetchall()
        for upvoter in upvoters:
            self.upvoters.append(upvoter[0])

    def read_with_id(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM request_table WHERE request_id = %s ', (self.request_id,))
            result = cursor.fetchone()
            self.owner = result[2]
            self.name = result[3]
            self.time_created = result[5]
            self.min_people = result[4]
            self.up_vote = result[6]
            self.explanation = result[7]
            self.group_id = result[1]
            self.get_upvoters()

    def is_upvoted(self,username):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT userid FROM user_table WHERE username = %s' , (username,))
            userid = cursor.fetchone()[0]
            cursor.execute('SELECT COUNT(*) FROM upvote_table WHERE request_id = %s AND user_id = %s' , (self.request_id, userid))
            upvote = cursor.fetchone()[0]
        if upvote:
            return True
        return False

User Class (methods about request)
----------------------------------


.. code-block:: python
    def remove_request(self, reqid):
        with ConnectionPool() as cursor:
            cursor.execute('DELETE FROM request_table where request_id = %s' , (reqid,))

    def upvote(self, reqid, vote):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT up_vote FROM request_table WHERE request_id = %s' , (reqid,))
            upvote = cursor.fetchone()[0]
            #for upvoting
            if vote == 1:
                cursor.execute('BEGIN TRANSACTION;'
                                'UPDATE request_table SET up_vote = %s where request_id = %s;'
                                'INSERT INTO upvote_table VALUES(%s ,%s);'
                                'COMMIT;'
                                 , (upvote + 1, reqid, reqid, self.id ))
                request = Request(reqid, None, None,None, 0, None,None)
                request.read_with_id()
                if request.up_vote == request.min_people:
                    message = 'Request ' + str(self.username) + ' in group ' + str(request.get_group_name()) + ' is fulfilled!'
                    for upvoter in request.upvoters:
                        if upvoter != request.owner:
                            new = New(None, None, upvoter, request.group_id, None, None, 'group' , 'request_fulfilled', False , None,message)
                            new.save_to_db()
                    cursor.execute('SELECT group_name FROM group_table WHERE group_id = %s' , (request.group_id,))
                    name = cursor.fetchone()[0]
                    message = 'Request ' + str(self.username) + ' in group ' + str(name) + ' is fulfilled!'
                    new = New(None, None, request.owner, request.group_id, None, None, 'group' , 'request_fulfilled', False, None,message )
                    new.save_to_db()

            else:
                cursor.execute('BEGIN TRANSACTION;'
                                'UPDATE request_table SET up_vote = %s where request_id = %s;'
                                'DELETE FROM upvote_table WHERE user_id = %s AND request_id = %s;'
                                'COMMIT;'
                                 , (upvote -1, reqid, self.id, reqid ))


    def is_upvoted(self,reqid):
            with ConnectionPool() as cursor:
                cursor.execute('SELECT COUNT(*) FROM upvote_table WHERE request_id = %s AND user_id = %s' , (reqid, self.id))
                upvote = cursor.fetchone()[0]
            if upvote:
                return True
            return False


Requests Class
---------------


.. code-block:: python
  class Requests():
    def __init__(self):
        self.arr = []

    def print_requests(self, groupid):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM request_table WHERE group_id = %s' , (groupid,))
            requests = cursor.fetchall()
        for request in requests:
            newrequest = Request(request[0], request[3], request[2], request[4], request[6], request[7], request[1])
            newrequest.read_with_id()
            self.arr.append(newrequest)



Comment Class
--------------


.. code-block:: python
  class Comment():
    def __init__(self, comment_id, owner, comment, subject, event_id, is_edited, send_notification ):
        self.comment_id = comment_id
        self.owner = owner
        self.time = None
        self.comment = comment
        self.subject = subject
        self.event_id = event_id
        self.is_edited = is_edited
        self.send_notification = send_notification

    def save_to_db(self):
        self.time = datetime.datetime.now()
        with ConnectionPool() as cursor:
            cursor.execute('INSERT INTO comment_table(owner,time,comment,subject,event_id,is_edited,send_notification) VALUES(%s,%s,%s,%s,%s,%s,%s)',
             (self.owner, self.time, self.comment, self.subject, self.event_id, self.is_edited, self.send_notification))
        if self.send_notification:
            event =  Event(None,None,None,None,None,None,None)
            event.read_with_id(self.event_id)
            for participant in event.participant_arr:
                new = New(None, self.owner, participant, event.group_id, self.event_id, None, 'event' , 'commented', False, None , None)
                new.save_to_db()


    def delete_comment(self):
        with ConnectionPool() as cursor:
            cursor.execute('DELETE FROM comment_table WHERE comment_id = %s' , (self.comment_id,))

    def update_comment(self, comment, subject, notif):
        self.comment = comment
        self.subject = subject
        self.send_notification = notif
        self.time = datetime.datetime.now()
        with ConnectionPool() as cursor:
            cursor.execute('UPDATE comment_table SET comment = %s, subject = %s, send_notification = %s, is_edited = %s, time = %s' , (self.comment, self.subject, self.send_notification, True, self.time))

        if self.send_notification:
            event =  Event(None,None,None,None,None,None,None)
            event.read_with_id(self.event_id)
            for participant in event.participant_arr:
                new = New(None, self.owner, participant, event.group_id, self.event_id, None, 'event' , 'updated the comment', False, None )
                new.save_to_db()

    def get_eventid(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT event_id FROM comment_table WHERE comment_id = %s' , (self.comment_id,))
            id = cursor.fetchone()[0]
        return id

Comments Class
---------------


.. code-block:: python
  class Comments():
    def __init__(self):
        self.comments = []

    def print_comments(self,event):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM comment_table WHERE event_id = %s' ,(event,))
            comments = cursor.fetchall()
        for comment in comments:
            temp = Comment(comment[0], comment[1], comment[3], comment[4], comment[5], comment[6], comment[7])
            temp.time = comment[2]
            self.comments.append(temp)




Database Table Diagrams
------------------------

Group Table
------------------------
  .. figure:: pics/group_table.jpeg
     :scale: 50 %
     :alt: Database Relation

Request Table
------------------------
  .. figure:: pics/request_table.jpeg
     :scale: 50 %
     :alt: Database Relation

Upvote Table
------------------------
  .. figure:: pics/upvote_table.jpeg
     :scale: 50 %
     :alt: Database Relation

Comment Table
------------------------
  .. figure:: pics/comment_table.jpeg
     :scale: 50 %
     :alt: Database Relation
