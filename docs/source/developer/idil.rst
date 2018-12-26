Parts Implemented by Idil
================================


User Class
-----------

 In this class, we implement insertion of a user to the user_table, update operation of the values of a user in the table, deletion of the user.

   .. code-block:: python

        class User(UserMixin):
          def __init__(self, first_name , surname, username , email, password, id):
              self.id = id
              self.username = username
              self.first_name = first_name
              self.surname = surname
              self.email = email
              self.password = password

          def __repr__(self):
              return "<User {}>".format(self.username)

          def save_to_db(self):
              with ConnectionPool() as cursor:
                  cursor.execute('INSERT INTO user_table(first_name, surname, username, email, passwrd) VALUES(%s,%s,%s,%s,%s);'
                                 ,(self.first_name, self.surname, self.username, self.email, self.password))
          @classmethod
          def get_with_email(cls,mail):
              with ConnectionPool() as cursor:
                  cursor.execute('SELECT * FROM user_table WHERE email = %s', (mail,))
                  user_data = cursor.fetchone()
                  if user_data:
                      return cls(id = user_data[0], username = user_data[1], first_name = user_data[2], surname = user_data[3], email = user_data[4] , password= user_data[5])
                  else:
                      return

          def check_password(self,passwrd):
              if self.password == passwrd:
                  return 1
              else:
                  return 0

          def get_id(self):
              with ConnectionPool() as cursor:
                  cursor.execute('SELECT userid FROM user_table WHERE userid = %s', (self.id,))
                  user = cursor.fetchone()
                  if user is None:
                      return
                  else:
                      return self.id

          def delete_account(self):
              with ConnectionPool() as cursor:
                  cursor.execute('DELETE FROM user_table WHERE userid = %s',(self.id,))


          def update_password(self, pswrd):
              # burada bir sikinti var duzelt
              with ConnectionPool() as cursor:
                  cursor.execute('UPDATE user_table set passwrd = %s WHERE userid = %s' , (pswrd, self.id))
              self.password = pswrd

          def update_username(self, usern):
              with ConnectionPool() as cursor:
                  cursor.execute('UPDATE user_table set username = %s WHERE userid = %s' , (usern, self.id))
              self.username = usern

          def update_email(self, mail):
              with ConnectionPool() as cursor:
                  cursor.execute('UPDATE user_table set email = %s WHERE userid = %s' , (mail, self.id))
              self.email = mail

          def check_participant_event(self,event_id):
              with ConnectionPool() as cursor:
                  cursor.execute('SELECT COUNT(*) FROM event_user where user_id = %s AND event_id = %s' , (self.id , event_id))
                  result = cursor.fetchone()
              return result[0]

          def check_owned(self, event):
              with ConnectionPool() as cursor:
                  cursor.execute('SELECT owner FROM event_table WHERE event_id = %s' , (event,))
                  owner = cursor.fetchone()
                  if owner[0] == self.id:
                      return True
                  else:
                      return False

          def remove_event(self, event_id):
              myevent = Event(None,None,None,None,None,None,None)
              myevent.read_with_id(event_id)
              for participant in myevent.participant_arr:
                  new = New(None, self.username, participant, myevent.group_id, myevent.event_id, None, 'event' , 'deleted', False, None, None )
                  new.save_to_db()
              with ConnectionPool() as cursor:
                  cursor.execute('DELETE FROM event_table where event_id = %s', (event_id,))
                  cursor.execute('UPDATE news_table SET link = %s WHERE event_id IS NULL AND link IS NOT NULL ' , (None,))


Profile Class
-------------

 This class is implemented to get, alter and maintain user profile information.

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

           def read_from_db(self):
               with ConnectionPool() as cursor:
                   cursor.execute('select email, username, first_name, surname, age, gender, country, city, hobbies, description from user_table where username = %s ', (self.username,))
                   profile_inf = cursor.fetchone()
                   self.email = profile_inf[0]
                   self.name = profile_inf[2]
                   self.surname = profile_inf[3]
                   self.gender = profile_inf[5]
                   self.age = profile_inf[4]
                   self.country = profile_inf[6]
                   self.city = profile_inf[7]
                   self.hobbies = profile_inf[8]
                   self.description = profile_inf[9]

           def get_unread_message_no(self):
               with ConnectionPool() as cursor:
                   cursor.execute('SELECT COUNT(*) FROM news_table WHERE receiver = %s AND seen = %s' , (self.username, False))
                   number = cursor.fetchone()[0]


MyProfile Class
-------------

 This class is implemented mainly to demonstrate user profile information on the website in several places and situations.

    .. code-block:: python

       class MyProfile(Profile):
           def __init__(self, username):
               Profile.__init__(self, username)
               self.read_from_db()

           def update_my_profile(self, email, name, surname, gender, age, country, city, hobbies, description):
               print(self.gender)
               self.name = name
               self.surname = surname
               self.gender = gender
               self.age = age
               self.country = country
               self.city = city
               self.hobbies = hobbies
               self.email = email
               self.description = description
               #self.check_empty()
               self.__update_profile_at_db()


           def __update_profile_at_db(self):
               with ConnectionPool() as cursor:
                   cursor.execute('UPDATE user_table set  email = %s, first_name = %s, surname = %s, gender = %s, age = %s , country = %s ,'
                                  'city = %s, hobbies = %s, description = %s WHERE username = %s', (self.email, self.name, self.surname, self.gender, self.age, self.country, self.city, self.hobbies, self.description, self.username))

New Class
---------

 This class is implemented to create notifications in news_table, alter their seen information and if necessary delete them.

    .. code-block:: python

        class New():
            def __init__(self, news_id, sender, receiver, group_id, event_id, time, type, action, seen ,link,message):
                self.news_id = news_id
                self.sender = sender
                self.receiver = receiver
                self.group_id = group_id
                self.event_id = event_id
                self.time = time
                self.type = type
                self.action = action
                self.seen = seen
                self.link = link
                self.message = message
                if message is None:
                    self.formulate_message()
                if link is None:
                    self.formulate_link()

            def formulate_message(self):
                if self.type == 'event':
                    with ConnectionPool() as cursor:
                        cursor.execute('SELECT event_name FROM event_table where event_id = %s' , (self.event_id,))
                        eventname = cursor.fetchone()[0]
                    self.message = str(self.sender) + ' ' + str(self.action) + ' event '+  str(eventname)
                elif self.type == 'group':
                    with ConnectionPool() as cursor:
                        cursor.execute('SELECT group_name FROM group_table where group_id = %s' , (self.group_id,))
                        groupname = cursor.fetchone()[0]
                    self.message = str(self.sender) + ' ' + str(self.action) + ' group '+  str(groupname)


            def formulate_link(self):
                if(self.type == 'event'):
                    if(self.action == 'deleted'):
                        self.link = None
                    elif(self.action == 'updated' or self.action == 'commented' or self.action == 'updated the comment'):
                        self.link = '/event/' + str(self.event_id)
                else:
                    if(self.action == 'deleted'):
                        self.link = None
                    elif(self.action == 'updated' or self.action == 'created request in' or self.action == 'joined' or self.action == 'request_fulfilled' or self.action =='deleted you from' or self.action =='left'):
                        self.link = '/group/' + str(self.group_id)
                    elif(self.action == 'created event in' or self.action == 'updated event in'):
                        self.link = '/groupevents/' + str(self.group_id)

            def save_to_db(self):
                ts = time.time()
                self.time = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                with ConnectionPool() as cursor:
                    cursor.execute('INSERT INTO news_table(sender,receiver,group_id,event_id,time,type,action,seen,link,message) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)',
                                    (self.sender, self.receiver, self.group_id, self.event_id, self.time, self.type, self.action, self.seen, self.link, self.message))
                    if self.sender is not None:
                        cursor.execute('SELECT news_id FROM news_table WHERE sender = %s AND time = %s AND receiver = %s  AND type = %s',
                                    (self.sender, self.time, self.receiver, self.type))
                    else:
                        cursor.execute('SELECT news_id FROM news_table WHERE sender is null AND time = %s AND receiver = %s  AND type = %s',
                                    (self.time, self.receiver, self.type))
                    self.news_id = cursor.fetchone()[0]

            def is_seen(self):
                with ConnectionPool() as cursor:
                    cursor.execute('UPDATE news_table SET seen = %s WHERE news_id = %s', (True, self.news_id))

            def delete_new(self):
                with ConnectionPool() as cursor:
                    cursor.execute('DELETE FROM news_table WHERE news_id = %s' , (self.news_id,))


News Class
---------

 This class is implemented in order to get the notifications from news_table and print them on each users notification page. 

    .. code-block:: python

        class News():
            def __init__(self):
                self.news_arr = []

            def print_news(self,username):
                with ConnectionPool() as cursor:
                    cursor.execute('SELECT * FROM news_table WHERE receiver = %s ORDER BY time DESC' , (username,))
                    news = cursor.fetchall()
                for new in news:
                    mynew = New(new[0], new[1], new[2], new[3], new[4],new[5], new[6], new[7], True, new[9],new[10])
                    mynew.is_seen()
                    self.news_arr.append(mynew)

Event Class
-----------

 This class is implemented to create events, update them and delete them if desired.
It also manages the addition and deletion of participants in each event.

    .. code-block:: python

        class Event():
            def __init__(self, name , place, owner , date, time, explanation, group_id):
                self.group_id = group_id
                self.group_name = None
                self.name = name
                self.place = place
                self.owner = owner
                self.date = date
                self.time = time
                self.explanation = explanation
                self.event_id = None
                self.owner_username = None
                self.participant_arr = []
                self.no_of_participants = None

            def initialization(self):
                with ConnectionPool() as cursor:
                    cursor.execute('SELECT event_id FROM event_table WHERE event_name = %s AND owner = %s AND date = %s AND time = %s',
                                    (self.name, self.owner, self.date, self.time))
                    result = cursor.fetchone()
                    self.event_id = result[0]
                    if self.group_id is not None:
                        cursor.execute('SELECT group_name FROM group_table WHERE group_id = %s', (self.group_id,))
                        result = cursor.fetchone()
                        self.group_name = result[0]
                    cursor.execute('SELECT username FROM user_table WHERE userid = %s ', (self.owner,))
                    result = cursor.fetchone()
                    self.owner_username = result[0]


            def find_participants(self):
                count = 0
                with ConnectionPool() as cursor:
                    cursor.execute('SELECT username FROM user_table WHERE userid in(SELECT user_id FROM event_user WHERE event_id = %s)', (self.event_id,))
                    participants = cursor.fetchall()
                    for participant in participants:
                        self.participant_arr.append(participant[0])
                        count += 1
                self.no_of_participants = count

            def read_with_id(self,id):
                with ConnectionPool() as cursor:
                    cursor.execute('SELECT * FROM event_table WHERE event_id = %s ', (id,))
                    result = cursor.fetchone()
                    self.group_id = result[1]
                    self.name = result[2]
                    self.place = result[3]
                    self.owner = result[4]
                    self.date = result[5]
                    self.time = result[6]
                    self.explanation = result[7]
                    self.event_id = result[0]
                    self.initialization()
                    self.find_participants()



            def __repr__(self):
                return "<User {}>".format(self.name)

            def save_to_db(self):
                with ConnectionPool() as cursor:
                    cursor.execute('INSERT INTO event_table(event_name, place, owner, date, time, explanation, group_id ) VALUES(%s,%s,%s,%s,%s,%s,%s)'
                                    ,(self.name, self.place , self.owner , self.date, self.time, self.explanation, self.group_id))
                    cursor.execute('SELECT event_id FROM event_table WHERE event_name = %s AND owner = %s AND date = %s and time = %s', (self.name, self.owner, self.date, self.time))
                    result = cursor.fetchone()
                    self.event_id = result[0]
                    cursor.execute('INSERT INTO event_user(event_id,user_id) VALUES(%s,%s);' , (self.event_id , self.owner))
                if self.group_id is not None:
                    with ConnectionPool() as cursor:
                        cursor.execute('SELECT username FROM user_table WHERE userid = %s' , (self.owner,))
                        username = cursor.fetchone()[0]
                        group = Group(None,None,None,None,None,self.group_id,None)
                        group.read_with_id()
                        for participant in group.participants:
                            new = New(None, username, participant, self.group_id, self.event_id, None, 'group' , 'created event in', False, None,None )
                            new.save_to_db()

            def add_participant(self,userid):
                with ConnectionPool() as cursor:
                    cursor.execute('INSERT into event_user values(%s,%s)' ,    (self.event_id, userid))
                    cursor.execute('SELECT username FROM user_table WHERE userid = %s' , (userid,))
                    participant = cursor.fetchone()
                    self.participant_arr.append(participant[0])

            def delete_participant(self, userid):
                with ConnectionPool() as cursor:
                    cursor.execute('DELETE FROM event_user WHERE user_id = %s' ,(userid,))
                    cursor.execute('SELECT username FROM user_table WHERE userid = %s' , (userid,))
                    participant = cursor.fetchone()
                self.participant_arr.remove(participant[0])

            def update_event(self,location, date, time, explanation):
                self.place = location
                self.date = date
                self.time = time
                self.explanation = explanation
                with ConnectionPool() as cursor:
                    cursor.execute('UPDATE event_table SET place = %s , date = %s, time = %s, explanation = %s WHERE event_id = %s' ,(location, date, time,explanation, self.event_id))
                    cursor.execute('SELECT username FROM user_table WHERE userid = %s' , (self.owner,))
                    username = cursor.fetchone()[0]
                    if self.group_id is not None:
                        group = Group(None,None,None,None,None,self.group_id,None)
                        group.read_with_id()
                        for participant in group.participants:
                            new = New(None, username, participant, self.group_id, self.event_id, None, 'group' , 'updated event in', False, None,None )
                            new.save_to_db()
                    else:
                        for participant in self.participant_arr:
                            new = New(None, username, participant, self.group_id, self.event_id, None, 'event' , 'updated', False,None,None )
                            new.save_to_db()

Events Class
-------------

 This class is implemented to demonstrate several events in designated pages.
 My events, owned events and group events view functionality is done through this class.

    .. code-block:: python

        class Events():
            def __init__(self):
                self.arr = []

            def select_top_ten(self):
                currentDT = datetime.datetime.now()
                year = currentDT.year
                month = currentDT.month
                day = currentDT.day
                if month < 10 and day < 10:
                    total = str(year) + '-0' + str(month) + '-0' + str(day)
                elif month < 10 and day > 10:
                    total = str(year) + '-0' + str(month) + '-' + str(day)
                if month > 10 and day < 10:
                    total = str(year) + '-' + str(month) + '-0' + str(day)
                else:
                    total = str(year) + '-' + str(month) + '-' + str(day)
                with ConnectionPool() as cursor:
                    cursor.execute('SELECT * FROM event_table WHERE group_id is null AND (date) >= (%s) ORDER BY (date) LIMIT 10', (total,))
                    result = cursor.fetchall()
                for element in result:
                    event = Event(element[2], element[3], element[4], element[5], element[6], element[7], element[1])
                    event.initialization()
                    self.arr.append(event)

            def owned_events(self,id):
                currentDT = datetime.datetime.now()
                year = currentDT.year
                month = currentDT.month
                day = currentDT.day
                if month < 10 and day < 10:
                    total = str(year) + '-0' + str(month) + '-0' + str(day)
                elif month < 10 and day > 10:
                    total = str(year) + '-0' + str(month) + '-' + str(day)
                if month > 10 and day < 10:
                    total = str(year) + '-' + str(month) + '-0' + str(day)
                else:
                    total = str(year) + '-' + str(month) + '-' + str(day)
                with ConnectionPool() as cursor:
                    cursor.execute('SELECT * FROM event_table WHERE owner = %s AND (date) >= (%s) ORDER BY (date , time)' , (id,total))
                    events = cursor.fetchall()
                for event in events:
                    event = Event(event[2], event[3], event[4], event[5], event[6], event[7], event[1])
                    event.initialization()
                    self.arr.append(event)

            def my_events(self,id):
                currentDT = datetime.datetime.now()
                year = currentDT.year
                month = currentDT.month
                day = currentDT.day
                if month < 10 and day < 10:
                    total = str(year) + '-0' + str(month) + '-0' + str(day)
                elif month < 10 and day > 10:
                    total = str(year) + '-0' + str(month) + '-' + str(day)
                if month > 10 and day < 10:
                    total = str(year) + '-' + str(month) + '-0' + str(day)
                else:
                    total = str(year) + '-' + str(month) + '-' + str(day)
                with ConnectionPool() as cursor:
                    cursor.execute('SELECT * FROM event_table WHERE event_id IN(SELECT event_id FROM event_user WHERE user_id = %s) AND (date) >= (%s) ORDER BY (date,time)' , (id,total))
                    events = cursor.fetchall()
                for event in events:
                    event = Event(event[2], event[3], event[4], event[5], event[6], event[7], event[1])
                    event.initialization()
                    self.arr.append(event)

            def group_events(self,userid,groupid):
                currentDT = datetime.datetime.now()
                year = currentDT.year
                month = currentDT.month
                day = currentDT.day
                if month < 10 and day < 10:
                    total = str(year) + '-0' + str(month) + '-0' + str(day)
                elif month < 10 and day > 10:
                    total = str(year) + '-0' + str(month) + '-' + str(day)
                if month > 10 and day < 10:
                    total = str(year) + '-' + str(month) + '-0' + str(day)
                else:
                    total = str(year) + '-' + str(month) + '-' + str(day)
                with ConnectionPool() as cursor:
                    cursor.execute('SELECT * FROM event_table WHERE group_id = %s AND date >= %s ORDER BY (date,time)' , ( groupid, total))
                    events = cursor.fetchall()
                for event in events:
                    event = Event(event[2], event[3], event[4], event[5], event[6], event[7], event[1])
                    event.initialization()
                    self.arr.append(event)

            def filtered_events(self, option, input):
                input = "%" + input + "%"
                currentDT = datetime.datetime.now()
                year = currentDT.year
                month = currentDT.month
                day = currentDT.day
                if month < 10 and day < 10:
                    total = str(year) + '-0' + str(month) + '-0' + str(day)
                elif month < 10 and day > 10:
                    total = str(year) + '-0' + str(month) + '-' + str(day)
                if month > 10 and day < 10:
                    total = str(year) + '-' + str(month) + '-0' + str(day)
                else:
                    total = str(year) + '-' + str(month) + '-' + str(day)

                if option == "Owner":
                    with ConnectionPool() as cursor:
                        cursor.execute(
                            'SELECT * FROM event_table WHERE owner IN (SELECT userid FROM user_table WHERE LOWER (username) LIKE LOWER (%s)) '
                            'AND group_id IS NULL AND (date) >= (%s) ORDER BY (date,time)',(input, total ))
                        events = cursor.fetchall()

                else:
                    if option == "Name":
                        with ConnectionPool() as cursor:
                            cursor.execute(
                                'SELECT * FROM event_table WHERE LOWER (event_name) LIKE LOWER (%s) AND group_id IS NULL AND (date) >= (%s) '
                                'ORDER BY (date,time)',(input, total))
                            events = cursor.fetchall()
                    elif option == "Location":
                        with ConnectionPool() as cursor:
                            cursor.execute(
                                'SELECT * FROM event_table WHERE LOWER (place) LIKE LOWER (%s) AND group_id  IS NULL AND (date) >= (%s) '
                                'ORDER BY (date,time)',(input, total))
                            events = cursor.fetchall()
                    elif option == "Date":
                        with ConnectionPool() as cursor:
                            cursor.execute(
                                 'SELECT * FROM event_table WHERE LOWER (date) LIKE LOWER (%s) AND group_id IS NULL AND (date) >= (%s) '
                                 'ORDER BY (date,time)',(input, total))
                            events = cursor.fetchall()

                for event in events:
                    event = Event(event[2], event[3], event[4], event[5], event[6], event[7], event[1])
                    event.initialization()
                    self.arr.append(event)

Database Table Diagrams
------------------------

User Table
-----------
  .. figure:: pics/user_table.jpg
     :scale: 50 %
     :alt: Database Relation

News Table
-----------
  .. figure:: pics/news_table.jpg
     :scale: 50 %
     :alt: Database Relation

Event Table
------------
  .. figure:: pics/event_table.jpg
     :scale: 50 %
     :alt: Database Relation

Event User Table
-----------------
  .. figure:: pics/event_user.jpg
     :scale: 50 %
     :alt: Database Relation

Group User Table
-----------------
  .. figure:: pics/group_user.jpg
     :scale: 50 %
     :alt: Database Relation
