import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.extras import RealDictCursor
import psycopg2.errors

class Database:
    def __init__(self):
        self.con = psycopg2.connect(
            dbname="Riders",
            user="postgres",
            password="evanngog",
            host="localhost",
            port=5432
        )
        self.cur = self.con.cursor(cursor_factory=RealDictCursor)

    def create_user(self, user_name, email, password):
        role = 'client'
        self.cur.execute(f"SELECT count(email) as count_email FROM users WHERE email='{email}'")
        result = self.cur.fetchall()
        print(result)
        if result[0]['count_email'] > 0:
            return False

        query = f"INSERT INTO users (name, email, password, role) VALUES ('{user_name}','{email}','{password}','{role}')"
        self.cur.execute(query)
        self.con.commit()
        return True

    def get_user(self, user_id):
        query = f"SELECT * FROM users WHERE id={user_id} LIMIT 1"
        self.cur.execute(query)
        result = self.cur.fetchall()
        if result:
            return result
        else:
            print('Пользователь не найден!')
            return False

    def get_user_by_email(self, user_email):
        self.cur.execute(f"SELECT * FROM users WHERE email=%s LIMIT 1", (user_email,))
        result = self.cur.fetchall()
        if result:
            return result
        else:
            print('Пользователь не найден!')
            return False

    def create_product(self):
        pass

    def update_role(self, user_email):
        try:
            role_admin = 'admin'
            self.cur.execute("UPDATE users SET role=%s WHERE email=%s", (role_admin, user_email))
            print(f'Статус пользователя {user_email}: {role_admin}')
            self.con.commit()
            return True
        except Exception as err:
            print("cursor.execute() ERROR:", err)

    def insert(self, query):
        self.cur.execute(query)
        self.con.commit()
        return

    def select(self, query):
        self.cur.execute(query)
        return query


a = Database()
a.update_role('admin@mail.ru')
