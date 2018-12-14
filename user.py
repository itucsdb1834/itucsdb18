import psycopg2
from dbconn import ConnectionPool
from flask_login import UserMixin
from event import Event
from request import Request
from news import New


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
