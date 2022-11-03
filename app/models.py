import psycopg2

conn = psycopg2.connect(
    dbname="Riders",
    user="postgres",
    password="evanngog",
    host="localhost",
    port=5432
)
cur = conn.cursor()

# Create table user
cur.execute(''' CREATE TABLE users ( 
                id SERIAL PRIMARY KEY,
                name CHARACTER VARYING(100),
                email CHARACTER VARYING(100),
                password CHARACTER VARYING(200),
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at time with time zone DEFAULT CURRENT_TIMESTAMP,
                last_login time with time zone DEFAULT CURRENT_TIMESTAMP,
                role character varying(15),
                CONSTRAINT web_user_email_key UNIQUE (email),
                CONSTRAINT check_email_user CHECK(email !=''))'''
            )

# Create table product
cur.execute(''' CREATE TABLE products (
                id SERIAL PRIMARY KEY,
                created_at time with time zone DEFAULT CURRENT_TIMESTAMP,
                updated_at time with time zone DEFAULT CURRENT_TIMESTAMP,
                name character varying(200) NOT NULL,
                text text NOT NULL,
                price int NOT NULL,
                user_id BIGINT NOT NULL,
                photo character varying(100) DEFAULT NULL,
                count int, 
                type character varying(50) NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'''
            )

# Create table order
cur.execute(''' CREATE TABLE orders (
                id SERIAL PRIMARY KEY,
                user_id int,
                product_id int,
                date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
                status character varying(20),
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE ON UPDATE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON UPDATE CASCADE)'''
            )

# Create table purchases
cur.execute(''' CREATE TABLE purchases (
                id SERIAL PRIMARY KEY, 
                user_id int,
                list_products text[],
                date timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE)'''
            )
# Create table favourites
cur.execute(''' CREATE TABLE favourites (
                user_id int,
                product_id int,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE) '''
            )
# Create table cart
cur.execute(''' CREATE TABLE cart (
                user_id int,
                product_id int,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE CASCADE)'''
            )

conn.commit()
cur.close()
conn.close()
