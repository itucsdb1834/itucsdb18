import psycopg2

class User:
    def __init__(self, first_name , surname, username , email, password, id):
        self.first_name = first_name
        self.surname = surname
        self.username = username
        self.email = email
        self.password = password
        self.id = id
    
    def __repr__(self):
        return "<User {}>".format(self.username)
    
    def save_to_db(self):
        with psycopg2.connect(user = 'postgres' , password = '1234' , database = 'RapidEvent' , host = 'localhost') as connection:
            with connection.cursor() as cursor:
                cursor.execute('INSERT INTO user_table(first_name, surname, username, email, passwrd) VALUES(%s,%s,%s,%s,%s)',
                (self.first_name, self.surname , self.username , self.email, self.password))

    @classmethod
    def load_from_db_with_email(cls, email):
        cls(None, 'class' , 'classs' ,'claclas' , 'class@class.com', 1234)
        with psycopg2.connect(user = 'postgres' , password = '1234' , database = 'RapidEvent' , host = 'localhost') as connection:
            with connection.cursor() as cursor:
                cursor.execute('SELECT * FROM users WHERE email= %s' , (email,))
                user_data = cursor.fetchone()
                return cls(email = user_data[4] ,  first_name = user_data[1] , surname = user_data[2], username = user_data[3], password = user_data[4], id = user_data[0])
