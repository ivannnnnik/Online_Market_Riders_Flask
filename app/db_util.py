import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash

class Database:
    def __init__(self):
        self.con = psycopg2.connect(
            dbname="Riders",
            user="postgres",
            password="evanngog",
            host="localhost",
            port=5432
        )
        self.cur = self.con.cursor()

    def create_user(self, user_name, email, password):
        role = 'client'
        self.cur.execute(f"SELECT count(email) as count_email FROM users WHERE email='{email}'")
        result = self.cur.fetchall()
        print(result)
        if result[0][0] > 0:
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
            data = self.prepare_data(self.cur.fetchall())

            if len(data) == 1:
                data = data[0]

            return data
        else:
            print('Пользователь не найден!')
            return False

    def is_authenticated(self, email, password):
        self.cur.execute(f"SELECT email, password  FROM users WHERE email='{email}'")
        result = self.cur.fetchall()
        print(result)
        if not result:
            return False
        email_user = result[0][0]
        pass_user = result[0][1]
        if email_user and email_user == email:
            if check_password_hash(pass_user, password):
                return True
            else:
                return False
        else:
            return False

    def update_role(self, user_id):
        role = 'admin'
        pass

    def insert(self, query):
        self.cur.execute(query)
        self.con.commit()
        return

    def select(self, query):
        self.cur.execute(query)
        data = self.prepare_data(self.cur.fetchall())

        if len(data) == 1:
            data = data[0]

        return data

    # --> JSON
    def prepare_data(self, data):
        films = []
        if len(data):
            column_names = [desc[0] for desc in self.cur.description]
            for row in data:
                films += [{c_name: row[key] for key, c_name in enumerate(column_names)}]

        return films
