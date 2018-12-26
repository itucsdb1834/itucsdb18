Parts Implemented by Idil
================================


User Class
-----------

In this class, we save users to user_table, update the table or delete users. The implementation is below

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
