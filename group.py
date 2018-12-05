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
