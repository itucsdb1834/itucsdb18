import psycopg2
from dbconn import ConnectionPool
import datetime

class Event():
    def __init__(self, name , place, owner , day, month, year, explanation, group_id):
        self.group_id = group_id
        self.group_name = None
        self.name = name
        self.place = place
        self.owner = owner
        self.day = day
        self.month = month
        self.year = year
        self.explanation = explanation
        self.event_id = None
        self.owner_username = None
        self.participant_arr = []
        self.no_of_participants = None

    def initialization(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT event_id FROM event_table WHERE event_name = %s AND owner = %s AND day = %s AND month = %s AND year = %s', (self.name, self.owner, self.day, self.month, self.year))
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
            self.day = result[5]
            self.month = result[6]
            self.year = result[7]
            self.explanation = result[8]
            self.event_id = result[0]
            self.initialization()
            self.find_participants()



    def __repr__(self):
        return "<User {}>".format(self.name)
        
    def save_to_db(self):
        with ConnectionPool() as cursor:
            cursor.execute('INSERT INTO event_table(event_name, place, owner, day,month,year,explanation, group_id ) VALUES(%s,%s,%s,%s,%s,%s,%s,%s);',(self.name, self.place , self.owner , self.day, self.month, self.year, self.explanation, self.group_id))

            cursor.execute('SELECT event_id FROM event_table WHERE event_name = %s AND owner = %s AND day = %s AND month = %s AND year = %s', (self.name, self.owner, self.day, self.month, self.year))
            result = cursor.fetchone()
            self.event_id = result[0]
            cursor.execute('INSERT INTO event_user(event_id,user_id) VALUES(%s,%s);' , (self.event_id , self.owner))
        self.initialization()

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

    def update_event(self,location, day, month, year, explanation):
        self.place = location
        self.day = day
        self.month = month
        self.year = year
        self.explanation = explanation
        with ConnectionPool() as cursor:
            cursor.execute('UPDATE event_table SET place = %s , day = %s, month = %s, year = %s, explanation = %s WHERE event_id = %s' ,(location, day, month, year, explanation, self.event_id))

class Events():
    def __init__(self):
        self.arr = []

    def select_top_ten(self):
        currentDT = datetime.datetime.now()
        year = currentDT.year
        month = currentDT.month
        day = currentDT.day
        total = 10000*year + 100*month + day
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM event_table WHERE (10000*year + 100*month + day) >= (%s) ORDER BY (10000*year + 100*month + day) LIMIT 10', (total,))
            result = cursor.fetchall()
        for element in result:
            event = Event(element[2], element[3], element[4], element[5], element[6], element[7], element[8], element[1])
            event.initialization()
            self.arr.append(event)

    def owned_events(self,id):
        currentDT = datetime.datetime.now()
        year = currentDT.year
        month = currentDT.month
        day = currentDT.day
        total = 10000*year + 100*month + day
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM event_table WHERE owner = %s AND (10000*year + 100*month + day) >= (%s) ORDER BY (10000*year + 100*month + day)' , (id,total))
            events = cursor.fetchall()
        for event in events:
            event = Event(event[2], event[3], event[4], event[5], event[6], event[7], event[8], event[1])
            event.initialization()
            self.arr.append(event)

    def my_events(self,id):
        currentDT = datetime.datetime.now()
        year = currentDT.year
        month = currentDT.month
        day = currentDT.day
        total = 10000*year + 100*month + day
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM event_table WHERE event_id IN(SELECT event_id FROM event_user WHERE user_id = %s) AND (10000*year + 100*month + day) >= (%s) ORDER BY (10000*year + 100*month + day)' , (id,total))
            events = cursor.fetchall()
        for event in events:
            event = Event(event[2], event[3], event[4], event[5], event[6], event[7], event[8], event[1])
            event.initialization()
            self.arr.append(event)
