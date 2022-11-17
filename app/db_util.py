import psycopg2
from werkzeug.security import generate_password_hash, check_password_hash
from psycopg2.extras import DictCursor
import psycopg2.errors
import json
from psycopg2 import Timestamp
from datetime import datetime
import dateutil.parser


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
        # print(result)
        if result[0]['count_email'] > 0:
            return False

        query = f"INSERT INTO users (name, email, password, role) VALUES ('{user_name}','{email}','{password}','{role}')"
        self.cur.execute(query)
        self.con.commit()
        return True

    def get_user_products(self, user_id):
        query = f"SELECT * FROM products WHERE user_id={user_id} and status=True"
        self.cur.execute(query)
        result = self.cur.fetchall()
        # print(result)
        if result:
            return self.prepare_data(result)
        else:
            print('Пользователь не найден!')
            return False

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

    def create_product(self, name, text, price, user_id, type_product, photo):
        try:
            self.cur.execute("INSERT INTO products (name, text, price, user_id, type, photo, status) "
                             "VALUES (%s, %s, %s, %s, %s, %s, %s)",
                             (name, text, price, user_id, type_product, photo, True))
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
        self.cur.execute("SELECT * FROM products WHERE status = True")
        result = self.cur.fetchall()
        if result:
            return self.prepare_data(result)
        else:
            print(f'Товары не найдены !')
            return False

    def last_id(self):
        self.cur.execute('SELECT max(id) FROM products')
        result = self.cur.fetchall()
        # print(result)
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

    def update_product(self, product_id, name, text, price, type_product, photo):
        try:
            if name != '':
                sql_query = "UPDATE products SET name=%s WHERE id=%s;"
                self.cur.execute(sql_query, (name, product_id))
                self.con.commit()
            if text != '':
                sql_query = "UPDATE products SET text=%s WHERE id=%s;"
                self.cur.execute(sql_query, (text, product_id))
                self.con.commit()
            if price != '':
                sql_query = "UPDATE products SET price=%s WHERE id=%s;"
                self.cur.execute(sql_query, (price, product_id))
                self.con.commit()
            if type_product != '':
                sql_query = "UPDATE products SET type=%s WHERE id=%s;"
                self.cur.execute(sql_query, (type_product, product_id))
                self.con.commit()
            if photo != '':
                sql_query = "UPDATE products SET photo=%s WHERE id=%s;"
                self.cur.execute(sql_query, (photo, product_id))
                self.con.commit()
            print(f'Товар: {name} обновлен')
            return True
        except Exception as err:
            print("cursor.execute() ERROR:", err)

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

    def add_product_in_order(self, user_id, list_products: list):
        # Проверка на orders_id [ [ [{}], 1, true], [ [{}], 1, false] ] ]
        # print('--------------------------------------------------------------------------')
        sql_check_last_order = "SELECT max(order_id) FROM orders"
        self.cur.execute(sql_check_last_order)
        check_id = self.cur.fetchone()[0]
        # print(check_id)
        status = 'Принят'
        check_product = 1
        if check_id is None:
            order_id = 0
        else:
            order_id = check_id + 1
        for i in range(len(list_products)):
            product_id = list_products[i][0][0]['id']
            count = int(list_products[i][1])
            check = list_products[i][2]
            if check == 'true':
                check = 1
            else:
                check = 0

            sql_check_product_user_in_order = "SELECT product_id, count, check_product FROM orders WHERE product_id=%s and status=%s and user_id=%s"
            self.cur.execute(sql_check_product_user_in_order, (product_id, status, user_id))
            check_product_in_order = self.cur.fetchone()
            if not check_product_in_order:
                # print(f'check: {check_product_in_order}')
                sql_query_1 = "INSERT INTO orders (user_id, product_id, status, order_id, count, check_product) VALUES (%s, %s,%s,%s,%s,%s) RETURNING order_id"
                self.cur.execute(sql_query_1, (user_id, product_id, status, order_id, count, check))
                self.con.commit()

            else:
                if check_product_in_order[1] != count:
                    # print(check_product_in_order[1], count)
                    sql_query_1 = "UPDATE orders SET count=%s WHERE user_id=%s and product_id=%s and status=%s RETURNING count"
                    self.cur.execute(sql_query_1, (count, user_id, product_id, status))
                    result = self.cur.fetchall()
                    # print(result)
                    self.con.commit()
                    print(f'данные изменил: id: {product_id}, count: {count}')
                if check_product_in_order[2] != check:
                    sql_query_1 = "UPDATE orders SET check_product=%s WHERE user_id=%s and product_id=%s and status=%s RETURNING count"
                    self.cur.execute(sql_query_1, (check, user_id, product_id, status))
                    result = self.cur.fetchall()
                    # print(result)
                    self.con.commit()
                    print(f'Измени статус продукта {product_id}')
        return True

    def get_products_in_order(self, user_id):
        sql_query = "SELECT product_id, count, order_id FROM orders WHERE user_id = %s and check_product=%s"
        self.cur.execute(sql_query, (user_id, 1))
        result = self.cur.fetchall()
        list_order_product = []
        if result != []:
            list_order_products = self.prepare_data(result)
            for i in range(len(list_order_products)):
                product_data = self.get_product_by_id(list_order_products[i]['product_id'])[0]
                data_product = {'id': product_data['id'],
                                'count': list_order_products[i]['count'],
                                'name': product_data['name'],
                                'photo': product_data['photo'],
                                'price': product_data['price'],
                                'order_id': list_order_products[i]['order_id']}
                list_order_product.append(data_product)
            return list_order_product
        else:
            return False

    def del_product_in_order(self, user_id, product_id):
        sql_query = "SELECT product_id, user_id FROM orders WHERE user_id = %s and product_id = %s"
        self.cur.execute(sql_query, (user_id, product_id))
        result = self.cur.fetchall()
        if result:
            sql_query_1 = "DELETE FROM orders WHERE user_id = %s and product_id = %s"
            self.cur.execute(sql_query_1, (user_id, product_id))
            self.con.commit()

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
        self.del_product_in_order(user_id, product_id)
        result = True
        return result

    def del_product_in_favourite(self, user_id, product_id):
        sql_query = "DELETE FROM favourites WHERE user_id = %s and product_id=%s"
        self.cur.execute(sql_query, (user_id, product_id))
        self.con.commit()
        result = True
        return result

    def delete_product(self, product_id):
        sql_query = "UPDATE products SET status=%s WHERE id=%s RETURNING id"
        self.cur.execute(sql_query, (False, product_id))
        self.con.commit()
        result = self.cur.fetchall()
        # print(result)
        if result:
            print(f'Удален : {product_id}')
            return True
        else:
            return False

    def user_payment_products(self, user_id):
        # sql_query = "SELECT product_id, count FROM orders WHERE user_id = %s and check_product = %s"
        sql_query = "DELETE FROM orders WHERE user_id = %s and check_product = %s RETURNING product_id, count"
        self.cur.execute(sql_query, (user_id, 1))
        result = self.cur.fetchall()
        list_products = [{'id': result[i][0], 'count': result[i][1]} for i in range(len(result))]
        self.con.commit()
        list_purchases = []

        sql_query = "SELECT max(number_purchase) FROM purchases WHERE user_id=%s"
        self.cur.execute(sql_query, (user_id,))
        result = self.cur.fetchall()
        # print(result)
        if result[0][0] is not None:
            number_purchase = int(result[0][0]) + 1
            # print(number_purchase)
        else:
            number_purchase = 0

        for i in range(len(list_products)):
            count_product = list_products[i]['count']
            product_id = list_products[i]['id']
            sql_query = "INSERT INTO purchases (user_id, product_id, count_product, number_purchase) VALUES (%s, %s, %s, %s) RETURNING purchases.date;"
            self.cur.execute(sql_query, (user_id, product_id, count_product, number_purchase))
            self.con.commit()
            result = self.cur.fetchall()
            format_date_month = '%m'
            format_date_day = '%d'
            format_time = '%H:%M'
            result = result[0][0]
            result = result.replace(' ', 'T')
            result = result.replace('+03', '')

            data_order = dateutil.parser.isoparse(result)
            data_date_month = data_order.strftime(format_date_month)
            data_date_day = data_order.strftime(format_date_day)
            data_date_time = data_order.strftime(format_time)

            product = self.get_product_by_id(product_id)
            product = product[0]
            context = {
                'id': product['id'],
                'name': product['name'],
                'final_price': product['price'] * count_product,
                'photo': product['price'],
                'count': count_product,
                'date_month': data_date_month,
                'date_day': data_date_day,
                'date_time': data_date_time
            }
            list_purchases.append(context)

        return list_purchases

    def get_product_price(self, product_id):
        sql_query = "SELECT price FROM products WHERE id=%s "
        self.cur.execute(sql_query, (product_id,))
        result = self.cur.fetchall()
        return result[0][0]

    def get_user_purchases(self, user_id):
        sql_query = "SELECT product_id, count_product, number_purchase, date FROM purchases WHERE user_id=%s "
        self.cur.execute(sql_query, (user_id,))
        result = self.cur.fetchall()
        # print(result)
        if result:
            list_products = self.prepare_data(result)
            # print(list_products)
            dict_products = {}
            for i in range(len(list_products)):
                if list_products[i]['number_purchase'] in dict_products:
                    dict_products[list_products[i]['number_purchase']].append(list_products[i])
                else:
                    dict_products[list_products[i]['number_purchase']] = [list_products[i]]
            # print(dict_products)
            list_out = []
            for key_i in dict_products:
                list_out.append(dict_products[key_i])

            # print(list_out)

            list_purchases_output = []
            for i in range(len(list_out)):
                second_list = []
                second_sum = 0
                for j in range(len(list_out[i])):
                    product_price = self.get_product_price(list_out[i][j]['product_id'])
                    format_date_month = '%m'
                    format_date_day = '%d'
                    format_time = '%H:%M'
                    date_product = list_out[i][j]['date']
                    date_product = date_product.replace('+03', '')
                    date_product = date_product.replace(' ', 'T')
                    # print(date_product)
                    data_order = dateutil.parser.isoparse(date_product)
                    data_date_month = data_order.strftime(format_date_month)
                    data_date_day = data_order.strftime(format_date_day)
                    data_date_time = data_order.strftime(format_time)

                    product = self.get_product_by_id(list_out[i][j]['product_id'])
                    product = product[0]
                    second_sum += int(product['price']) * list_out[i][j]['count_product']
                    context = {
                        'id': product['id'],
                        'name': product['name'],
                        'final_price': product['price'] * list_out[i][j]['count_product'],
                        'photo': product['photo'],
                        'count': list_out[i][j]['count_product'],
                        'date_month': data_date_month,
                        'date_day': data_date_day,
                        'date_time': data_date_time,
                    }
                    second_list.append(context)
                second_list.append(second_sum)
                list_purchases_output.append(second_list)
                # print(f'second: {second_sum}')
            return list_purchases_output
        else:
            return False

    def user_purchases(self, user_id):
        sql_query = "SELECT product_id, count_product, number_purchase FROM purchases WHERE user_id = %s"
        self.cur.execute(sql_query, (user_id,))
        result = self.cur.fetchall()
        # print(result)
        if result:
            pass
        else:
            return False

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

    def get_products_purchase_by_id(self, user_id,  purchase_id):
        sql_query = "SELECT max(number_purchase) FROM purchases WHERE user_id=%s;"
        self.cur.execute(sql_query, (user_id,))
        max_id = self.cur.fetchone()[0]
        print(max_id)
        purchase_id = max_id - purchase_id
        sql_query = "SELECT user_id, product_id, count_product FROM purchases WHERE user_id=%s and number_purchase=%s;"
        self.cur.execute(sql_query, (user_id, purchase_id,))
        result = self.cur.fetchall()
        result = self.prepare_data(result)
        print(result)
        list_products = []
        for i in range(len(result)):
            product = self.get_product_by_id(result[i]['product_id'])
            product[0]['count_product'] = result[i]['count_product']
            list_products.append(product[0])
        return list_products

    def get_products_filter(self, filter):
        products = self.get_products_all()
        list_product = []
        for i in range(len(products)):
            search = products[i]['name']
            if filter.lower() in search.lower():
                list_product.append(products[i])
        if len(list_product) != 0:
            return list_product
        else:
            return False

    def delete_profile_user(self, user_id):
        sql_query = "DELETE FROM users WHERE id=%s;"
        self.cur.execute(sql_query, (user_id,))
        self.con.commit()
        return True

    def update_name_user(self, user_id, name_user):
        if len(name_user) > 2:
            if len(name_user) < 25:
                sql_query = "UPDATE users SET name=%s WHERE id=%s;"
                self.cur.execute(sql_query, (name_user, user_id,))
                self.con.commit()
                return True
            else:
                return False
        else:
            return False

    def update_password_user(self, user_id, password):
        sql_query = "UPDATE users SET password=%s WHERE id=%s;"
        self.cur.execute(sql_query, (password, user_id,))
        self.con.commit()
        return True


# sql_query = "ALTER TABLE products DROP COLUMN count;"
# sql_query = "ALTER TABLE products ADD status BOOLEAN NOT NULL;"

# a = Database()
# print(a.insert(sql_query))
# print(a.get_products_purchase_by_id(22, 0))
