from dbconn import ConnectionPool
from news import New

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
