import os
import sys

import psycopg2 as dbapi2


INIT_STATEMENTS = [
                   "DROP TABLE IF EXISTS upvote_table CASCADE;",
                   "DROP TABLE IF EXISTS request_table CASCADE;",
                   "DROP TABLE IF EXISTS comment_table CASCADE;",
		   "DROP TABLE IF EXISTS event_user CASCADE;",
                   "DROP TABLE IF EXISTS group_user CASCADE;",
                   "DROP TABLE IF EXISTS event_table CASCADE;",
                   "DROP TABLE IF EXISTS group_table CASCADE;",
                   "DROP TABLE IF EXISTS user_table CASCADE;",
                   "DROP TABLE IF EXISTS news_table CASCADE;",
                   "CREATE TABLE user_table("
                                           "userid SERIAL NOT NULL UNIQUE,"
                                           "username varchar(255) NOT NULL UNIQUE,"
                                           "first_name varchar(255) NOT NULL,"
                                           "surname varchar(255) NOT NULL,"
                                           "email varchar(255) NOT NULL UNIQUE,"
                                           "passwrd varchar(255) NOT NULL,"
                                           "gender char(6),"
                                           "age integer,"
                                           "country varchar(50),"
                                           "city varchar(50),"
                                           "hobbies varchar(255),"
                                           "description varchar(255),"
                                           "PRIMARY KEY(userid)"
                                           ");",
                "CREATE TABLE group_table ( "
                                        	"group_id serial NOT NULL UNIQUE, "
                                        	"group_name varchar(255) NOT NULL, "
                                        	"give_permission boolean default false, "
                                        	"isprivate boolean default  false, "
                                        	"owner int NOT NULL, "
                                        	"max_number INT, "
                                        	"description varchar(255), "
                                        	"unique(group_name,owner), "
                                        	"primary key(group_id), "
                                        	"foreign key(owner) "
                                        		"references user_table(userid) "
                                        		"on delete cascade "
                                        		"on update cascade "
                ");",
		 "CREATE TABLE event_table ("
	                                       "event_id serial NOT NULL UNIQUE, "
	                                       "group_id INT, "
	                                       "event_name varchar(255)  NOT NULL, "
	                                       "place varchar(255) NOT NULL, "
	                                       "owner int NOT NULL, "
	                                       "date varchar(255) NOT NULL, "
	                                       "time varchar(255) NOT NULL, "
	                                       "explanation varchar(255) , "
    	                                   "unique(event_name,owner,date,time), "
	                                       "foreign key(owner) "
		                                         "references user_table(userid) "
		                                          "on delete cascade "
		                                          "on update cascade, "
	                                              "foreign key(group_id) "
		                                          "references group_table(group_id) "
		                                          "on delete cascade "
		                                          "on update cascade "
                                            ");",
                "CREATE TABLE event_user ( "
                                        	"event_id INT NOT NULL, "
                                        	"user_id INT NOT NULL, "
                                                    "primary key(user_id, event_id), "
                                        	"foreign key(event_id) "
                                        		"references event_table(event_id) "
                                        		"on delete cascade "
                                        		"on update cascade, "
                                        	"foreign key(user_id) "
                                        		"references user_table(userid) "
                                        		"on delete cascade "
                                        		"on update cascade "
                "); ",
                "CREATE TABLE group_user ( "
                                        	"user_id INT NOT NULL, "
                                        	"group_id INT NOT NULL, "
                                                    "primary key(user_id, group_id), "
                                        	"foreign key(user_id) "
                                        		"references user_table(userid) "
                                        		"on delete cascade "
                                        		"on update cascade, "
                                        	"foreign key(group_id) "
                                        		"references group_table(group_id) "
                                        		"on delete cascade "
                                        		"on update cascade "
                ");",
                "CREATE TABLE comment_table("
                                        	"comment_id SERIAL NOT NULL UNIQUE, "
                                        	"owner varchar(255) NOT NULL, "
                                        	"time varchar(255) NOT NULL, "
                                        	"comment varchar(255) NOT NULL, "
                                        	"subject varchar(255), "
                                        	"event_id INT NOT NULL, "
                                        	"is_edited Boolean DEFAULT FALSE, "
                                        	"send_notification Boolean Default False, "
                                        	"primary key(comment_id), "
                                        	"foreign key(event_id) "
                                        		"references event_table(event_id) "
                                        		"on delete cascade "
                                        		"on update cascade, "
                                        	"foreign key(owner )"
                                        		"references user_table(username) "
                                        		"on delete cascade "
                                        		"on update cascade "

                ");",
                "CREATE TABLE request_table( "
                                        	"request_id SERIAL NOT NULL UNIQUE, "
                                        	"group_id INT NOT NULL, "
                                        	"owner varchar(255) NOT NULL, "
                                        	"name varchar(255) NOT NULL, "
                                        	"min_people INT DEFAULT 0, "
                                        	"time_created varchar(255) NOT NULL, "
                                        	"up_vote INT DEFAULT 0, "
                                        	"explanation varchar(255), "
                                        	"unique(name,owner), "
                                        	"PRIMARY KEY(request_id), "
                                        	"FOREIGN KEY(owner) "
                                        		"references user_table(username) "
                                        		"on delete cascade "
                                        		"on update cascade, "
                                        	"FOREIGN KEY(group_id) "
                                        		"references group_table(group_id) "
                                        		"on delete cascade "
                                        		"on update cascade "
                ");",
                "CREATE TABLE upvote_table( "
                                        	"request_id INT NOT NULL, "
                                        	"user_id INT NOT NULL, "
                                        	"primary key(request_id, user_id), "
                                        	"foreign key(request_id) "
                                        		"references request_table(request_id) "
                                        		"on delete cascade "
                                        		"on update cascade, "
                                        	"foreign key(user_id) "
                                        		"references user_table(userid) "
                                        		"on delete cascade "
                                        		"on update cascade "
                ");",
                "CREATE TABLE news_table("
                                        	"news_id SERIAL NOT NULL UNIQUE, "
                                        	"sender  varchar(255), "
                                        	"receiver varchar(255) NOT NULL, "
                                        	"group_id INT, "
                                        	"event_id INT, "
                                        	"time varchar(255) NOT NULL, "
                                        	"type varchar(255), "
                                        	"action varchar(255), "
                                        	"seen boolean DEFAULT FALSE, "
                                        	"link varchar(255), "
                                        	"message varchar(255) NOT NULL, "
                                        	"UNIQUE(sender, receiver, time, type), "
                                        	"PRIMARY KEY(news_id), "
                                        	"FOREIGN KEY(sender) "
                                        		"references user_table(username) "
                                        		"on delete cascade "
                                        		"on update cascade, "
                                        	"FOREIGN KEY(receiver) "
                                        		"references user_table(username) "
                                        		"on delete cascade "
                                        		"on update cascade, "
                                        	"FOREIGN KEY(group_id) "
                                        		"references group_table(group_id) "
                                        		"on delete set null "
                                        		"on update cascade, "
                                        	"FOREIGN KEY(event_id) "
                                        		"references event_table(event_id) "
                                        		"on delete set null "
                                        		"on update cascade "
                "); ",
		"INSERT INTO user_table(username,first_name, surname, email,passwrd)"
		"VALUES('idilugurnal', 'Idil', 'Ugurnal', 'idilugurnal@gmail.com', '12345');",
		"INSERT INTO user_table(username,first_name, surname, email,passwrd)"
		"VALUES('caglakaya', 'Cagla, Kaya', 'caglakaya@gmail.com', '12345');"

                   ]


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)
        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)
