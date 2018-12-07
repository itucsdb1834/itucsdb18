import psycopg2
from dbconn import ConnectionPool

class Group():
    def __init__(self, name, isprivate, owner, description, give_permission ,group_id):
        self.name = name
        self.isprivate = isprivate
        self.owner= owner
        self.description = description
        self.give_permission = give_permission
        self.group_id = group_id
        self.owner_name = None
        self.participants = []
        self.participant_no = 0

    def read_with_id(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM group_table WHERE group_id = %s' , (self.group_id,))
            result = cursor.fetchone()
            self.name = result[1]
            self.isprivate = result[2]
            self.owner = result[3]
            self.description = result[4]
            self.give_permission = result[5]
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

            cursor.execute('INSERT INTO group_user VALUES(%s,%s)' , (userid, self.group_id))
            self.participant_no += 1
            self.participants.append(username)

    def delete_group(self):
        with ConnectionPool() as cursor:
            cursor. execute('DELETE FROM group_table WHERE group_id = %s' , (self.group_id,))

    def update_group(self, name,isprivate,description,give_permission):
        with ConnectionPool() as cursor:
            cursor. execute('UPDATE group_table SET group_name=%s, isprivate=%s, description=%s, give_permission=%s WHERE group_id = %s' ,
                            (name, isprivate, description, give_permission, self.group_id,))
            self.name=name
            self.give_permission=give_permission
            self.isprivate=isprivate
            self.description=description

    def get_participants(self):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT user_table.username FROM user_table RIGHT OUTER JOIN group_user ON group_user.user_id = user_table.userid WHERE group_user.group_id = %s ' , (self.group_id,))
            participants = cursor.fetchall()
        for participant in participants:
            self.participants.append(participant[0])
            self.participant_no = self.participant_no +1

    def save_to_db(self):
        with ConnectionPool() as cursor:
            cursor.execute('INSERT INTO group_table(group_name, isprivate, owner, description, give_permission) VALUES(%s,%s,%s,%s,%s);',(self.name, self.isprivate , self.owner , self.description, self.give_permission))
            cursor.execute('SELECT group_id FROM group_table WHERE group_name = %s AND owner = %s', (self.name, self.owner))
            result = cursor.fetchone()
            self.group_id = result[0]
            cursor.execute('INSERT INTO group_user(group_id,user_id) VALUES(%s,%s);' , (self.group_id , self.owner))


class Groups():
    def __init__(self):
        self.arr = []

    def owned_groups(self,id):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM group_table WHERE owner = %s ' , (id,))
            groups = cursor.fetchall()
        for group in groups:
            group = Group(group[1] , group[2] , id , group[4] , group[5],group[0])
            self.arr.append(group)

    def my_groups(self,id):
        with ConnectionPool() as cursor:
            cursor.execute('SELECT * FROM group_table WHERE group_id IN(SELECT group_id FROM group_user WHERE user_id = %s) ' , (id,))
            groups = cursor.fetchall()
        for group in groups:
            group = Group(group[1] , group[2] , id , group[4] , group[5],group[0])
            self.arr.append(group)
