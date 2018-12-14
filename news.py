import psycopg2
from dbconn import ConnectionPool
import datetime
import time

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
