import sqlite3

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

command = "CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR(100) NOT NULL UNIQUE, email VARCHAR(100) NOT NULL UNIQUE, password VARCHAR(100) NOT NULL, admin INT(11), cart JSON, wishlist JSON)"

command_produit = "CREATE TABLE IF NOT EXISTS items (id INTEGER PRIMARY KEY AUTOINCREMENT, name VARCHAR(100), description VARCHAR(100), prix FLOAT(20), image VARCHAR(100))"

command_com = "CREATE TABLE IF NOT EXISTS comments (id INTEGER PRIMARY KEY AUTOINCREMENT,description VARCHAR(100), product_id INT,user_id INT, FOREIGN KEY(product_id) REFERENCES items(id), FOREIGN KEY(user_id) REFERENCES users(id))"

command_orders = "CREATE TABLE IF NOT EXISTS orders (id INTEGER PRIMARY KEY AUTOINCREMENT, date VARCHAR(100), status VARCHAR(100), prix FLOAT(20), user_id, FOREIGN KEY(user_id) REFERENCES users(id))"


cursor.execute(command)
cursor.execute(command_produit)
cursor.execute(command_com)
cursor.execute(command_orders)

