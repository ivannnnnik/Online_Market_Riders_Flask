import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.extras import DictCursor
import psycopg2.errors
import json


class Database:
    def __init__(self):
        self.con = psycopg2.connect(
            dbname="Riders",
            user="postgres",
            password="evanngog",
            host="localhost",
            port=5432
        )
        self.cur = self.con.cursor(cursor_factory=DictCursor)

    def create_user(self, user_name, email, password):
        role = 'client'
        self.cur.execute(f"SELECT count(email) as count_email FROM users WHERE email='{email}'")
        result = self.prepare_data(self.cur.fetchall())
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
            return self.prepare_data(result)
        else:
            print('Пользователь не найден!')
            return False

    def get_user_by_email(self, user_email):
        self.cur.execute(f"SELECT * FROM users WHERE email=%s LIMIT 1", (user_email,))
        result = self.cur.fetchall()
        if result:
            return self.prepare_data(result)
        else:
            print('Пользователь не найден!')
            return False

    def create_product(self, name, text, price, user_id, count, type_product, photo):
        try:
            self.cur.execute("INSERT INTO products (name, text, price, user_id, count, type, photo) "
                             "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                             (name, text, price, user_id, count, type_product, photo))
            print(f'Товар: {name} создан')
            self.con.commit()
            return True
        except Exception as err:
            print("cursor.execute() ERROR:", err)

    def update_role(self, user_email):
        try:
            role_admin = 'admin'
            self.cur.execute("UPDATE users SET role=%s WHERE email=%s", (role_admin, user_email))
            print(f'Статус пользователя {user_email}: {role_admin}')
            self.con.commit()
            return True
        except Exception as err:
            print("cursor.execute() ERROR:", err)

    def get_product_by_id(self, product_id):
        self.cur.execute(f"SELECT * FROM products WHERE id=%s LIMIT 1", (product_id,))
        result = self.cur.fetchall()
        if result:
            return self.prepare_data(result)
        else:
            print(f'Товар с id: {product_id} не найден !')
            return False

    def get_products_all(self):
        self.cur.execute("SELECT * FROM products")
        result = self.cur.fetchall()
        if result:
            return self.prepare_data(result)
        else:
            print(f'Товары не найдены !')
            return False

    def last_id(self):
        self.cur.execute('SELECT max(id) FROM products')
        result = self.cur.fetchall()
        print(result)
        if result[0][0] is None:
            return 0
        result = self.prepare_data(result)
        return result[0]['max'] + 1

    def add_product_in_cart(self, user_id, product_id):
        sql_query_1 = "SELECT product_id FROM cart WHERE user_id=%s and product_id=%s"
        self.cur.execute(sql_query_1, (user_id, product_id))
        in_cart = self.cur.fetchone()
        if in_cart:
            return False

        sql_query_2 = "INSERT INTO cart (user_id, product_id) VALUES (%s, %s) RETURNING user_id;"
        self.cur.execute(sql_query_2, (user_id, product_id))
        result = self.cur.fetchone()[0]
        self.con.commit()
        if result:
            return True
        else:
            print(f'Товар не добавлен!')
            return False

    def user_cart(self, user_id):
        sql_query = "SELECT product_id FROM cart WHERE user_id = %s"
        self.cur.execute(sql_query, (user_id,))
        result = self.cur.fetchall()
        if result != []:
            list_products = [result[i][0] for i in range(len(result))]
            list_cart_products = []
            for i in range(len(list_products)):
                sql_query = "SELECT * FROM products WHERE id = %s"
                self.cur.execute(sql_query, (list_products[i],))
                result = self.cur.fetchall()
                list_cart_products.append(result)
            list_cart_products = [list_cart_products[i][0] for i in range(len(list_cart_products))]
            list_cart_products = self.prepare_data(list_cart_products)
            return list_cart_products
        else:
            return False

    def final_price_cart(self, list_product):
        final_price = [list_product[i]['price'] for i in range(len(list_product))]
        return sum(final_price)


    def add_product_in_favourite(self, user_id, product_id):
        sql_query_1 = "SELECT product_id FROM favourites WHERE user_id=%s and product_id=%s"
        self.cur.execute(sql_query_1, (user_id, product_id))
        in_fav = self.cur.fetchone()
        if in_fav:
            return False

        sql_query_2 = "INSERT INTO favourites (user_id, product_id) VALUES (%s, %s) RETURNING user_id;"
        self.cur.execute(sql_query_2, (user_id, product_id))
        result = self.cur.fetchone()[0]
        self.con.commit()
        if result:
            return True
        else:
            print(f'Товар не добавлен!')
            return False

    def user_favourites(self, user_id):
        sql_query = "SELECT product_id FROM favourites WHERE user_id = %s"
        self.cur.execute(sql_query, (user_id,))
        result = self.cur.fetchall()
        if result:
            list_products = [result[i][0] for i in range(len(result))]
            list_cart_products = []
            for i in range(len(list_products)):
                sql_query = "SELECT * FROM products WHERE id = %s"
                self.cur.execute(sql_query, (list_products[i],))
                result = self.cur.fetchall()
                list_cart_products.append(result)
            list_cart_products = [list_cart_products[i][0] for i in range(len(list_cart_products))]
            list_cart_products = self.prepare_data(list_cart_products)
            return list_cart_products
        else:
            return False

    def del_product_in_cart(self, user_id, product_id):
        sql_query = "DELETE FROM cart WHERE user_id = %s and product_id=%s"
        self.cur.execute(sql_query, (user_id, product_id))
        self.con.commit()
        result = True
        return result

    def del_product_in_favourite(self, user_id, product_id):
        sql_query = "DELETE FROM favourites WHERE user_id = %s and product_id=%s"
        self.cur.execute(sql_query, (user_id, product_id))
        self.con.commit()
        result = True
        return result

    def insert(self, query):
        self.cur.execute(query)
        self.con.commit()
        return

    def select(self, query):
        self.cur.execute(query)
        return query

    def prepare_data(self, data):
        output_data = []
        if len(data):
            column_names = [desc[0] for desc in self.cur.description]
            for row in data:
                output_data += [{c_name: row[key] for key, c_name in enumerate(column_names)}]

        return output_data


a = Database()
print(a.user_cart(22))
