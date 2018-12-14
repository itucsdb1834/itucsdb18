import psycopg2
from dbconn import ConnectionPool
import datetime
from group import Group
from news import New
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

class Requests():
    def __init__(self):
        self.arr = []

    def print_requests(self, groupid):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM request_table WHERE group_id = %s' , (groupid,))
            requests = cursor.fetchall()
        for request in requests:
            newrequest = Request(request[0], request[3], request[2], request[4], request[6], request[7], request[1])
            self.arr.append(newrequest)
