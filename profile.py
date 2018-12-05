from dbconn import ConnectionPool


class Profile(object):
    def __init__(self, username):
        self.username = username
        self._profileID = -1
        self.name = ' '
        self.surname = ' '
        self.age = 0
        self.gender = ' '
        self.country = ' '
        self.city = ' '
        self.hobbies = ' '
        self.description = ' '
        self.email = ' '
    
    def read_from_db(self):
        with ConnectionPool() as cursor:
            cursor.execute('select email, username, first_name, surname, age, gender, country, city, hobbies, description from user_table where username = %s ', (self.username,))
            profile_inf = cursor.fetchone()
            self.email = profile_inf[0]
            self.name = profile_inf[2]
            self.surname = profile_inf[3]
            self.gender = profile_inf[5]
            self.age = profile_inf[4]
            self.country = profile_inf[6]
            self.city = profile_inf[7]
            self.hobbies = profile_inf[8]
            self.description = profile_inf[9]



class MyProfile(Profile):
    def __init__(self, username):
        Profile.__init__(self, username)
        self.read_from_db()
    
    def update_my_profile(self, email, name, surname, gender, age, country, city, hobbies, description):
        print(self.gender)
        self.name = name
        self.surname = surname
        self.gender = gender
        self.age = age
        self.country = country
        self.city = city
        self.hobbies = hobbies
        self.email = email
        self.description = description
        self.check_empty()
        self.__update_profile_at_db()
    
    def check_empty(self):
        if (self.gender == '' or self.gender is None):
            self.gender = None
        if(self.age == '' or self.age is None):
            self.age = None
        if(self.country == ''):
            self.country = None
        if(self.city == ''):
            self.city = None
        if(self.hobbies == ''):
            self.hobbies = None
        if(self.description == ''):
            self.description = None

    
    
    def __update_profile_at_db(self):
        with ConnectionPool() as cursor:
            cursor.execute('UPDATE user_table set  email = %s, first_name = %s, surname = %s, gender = %s, age = %s , country = %s ,'
                           'city = %s, hobbies = %s, description = %s WHERE username = %s', (self.email, self.name, self.surname, self.gender, self.age, self.country, self.city, self.hobbies, self.description, self.username))









