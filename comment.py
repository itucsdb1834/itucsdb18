import psycopg2
from dbconn import ConnectionPool
import datetime
from news import New
from event import Event

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
