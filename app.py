from flask import Flask, render_template, redirect, request, url_for
from flask_login import *
from flask_wtf import FlaskForm
from wtforms.validators import *
from model import *
import sqlite3, os, hashlib
import string, random, json
from datetime import datetime

# Connection Base de données
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///"+os.path.join(basedir, 'database.db')
db.init_app(app)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# Login Manager
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'
@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

# Liste des routes 
@app.route('/')
def home():
    all_items = Items.query.all()
    return render_template('home.html', items = all_items)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form['name']
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        user = Users.query.filter_by(username=name).first()
        if user != None:
            if user.check_password(password):
                login_user(user)
                return redirect(url_for('home'))
        else:
            print("no user")

    return render_template('login.html')

@app.route('/logged')
@login_required
def logged():
    return render_template('logged.html', )

@app.route('/account')
@login_required
def account():
    orders = Orders.query.filter_by(user_id=current_user.id).all()
    return render_template("account.html", orders=orders)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/register', methods=['GET', 'POST'])
def register(): 
    if request.method == 'GET':
        return render_template("register.html")
    else:
        name = request.form['name']
        email = request.form["email"]
        password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        confirm_password = hashlib.sha256(request.form['confirm_password'].encode()).hexdigest()
        if password != confirm_password:
            return render_template('register.html', error=True)
        
        check_user = Users.query.filter_by(username=name, email=email).first()
        if check_user != None:
            return render_template('register.html', error=True)

        user = Users(username = name, email = email, password=password, admin=0, cart="[]", wishlist="[]")
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))

@app.route('/modify_account/<int:id>', methods=['POST'])
@login_required
def modify_account(id):
    account = Users.query.get(id)
    if request.form["name"] != "":
        account.username = request.form["name"]
    if request.form["email"] != "":
        account.email = request.form["email"]
    if request.form["password"] and request.form["confirm_password"] != "":
        account.password = hashlib.sha256(request.form['password'].encode()).hexdigest()
        account.confirm_password = hashlib.sha256(request.form['confirm_password'].encode()).hexdigest()
        if account.password != account.confirm_password:
            return redirect(url_for("account", error = True))
        
    db.session.commit()         
    return redirect(url_for("account"))

@app.route('/backend')
@login_required
def backend():
    all_items = Items.query.all()
    return render_template('backend.html', all_items = all_items)

@app.route('/additem', methods=['POST'])
@login_required
def additem():
    if current_user.admin == 1:
        name = request.form["name"]
        prix = request.form["prix"]
        description = request.form["description"]
        image = request.files["image"]
        extension = image.filename.split('.')[-1]
        image.filename = str(''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))+"."+extension
        image.save("static/asset/"+image.filename)
        item = Items(name = name, description = description, prix = prix, image = image.filename)
        db.session.add(item)
        db.session.commit()
        return redirect(url_for("backend"))
    else:
        return redirect(url_for('/'))

@app.route('/modify_item/<int:id>', methods=['POST'])
@login_required
def modify_item(id):
    if current_user.admin == 1:
        item = Items.query.get(id)
        item.name = request.form["name"]
        item.prix = request.form["price"]
        item.description = request.form["description"]
        if 'pic' in request.files and request.files["pic"].filename != "":
            image = request.files["pic"]
            extension = image.filename.split('.')[-1]
            image.filename = str(''.join(random.choices(string.ascii_uppercase + string.digits, k=6)))+"."+extension
            image.save("static/asset/"+image.filename)
            item.image = image.filename
        
        db.session.commit()
        return redirect(url_for("backend"))
    else:
        return redirect(url_for('/')) 
    
@app.route('/delete_item/<int:id>')
@login_required
def delete_item(id):
    if current_user.admin == 1:
        item = Items.query.get(id)
        db.session.delete(item)
        db.session.commit()
        return redirect(url_for("backend"))
    else:
        return redirect(url_for('/')) 
    
@app.route('/item_info/<int:id>')
def item_info(id):
    selected_item = Items.query.get(id)
    comments = Comments.query.filter_by(product_id = id).all()
    for comment in comments:
        user = Users.query.get(comment.user_id)
        comment.user_name = user.username
    return render_template('item_info.html', item = selected_item, comments = comments)

@app.route('/panier')
@login_required
def panier():
    user = Users.query.get(current_user.id)
    cart = json.loads(user.cart)
    wishlist = json.loads(user.wishlist)
    products = []
    products_wishlist = []
    total = 0
    for product_id in cart:
        product = Items.query.get(product_id)
        if product is not None:
            products.append(product)
            total += product.prix

    for product_id in wishlist:
        product = Items.query.get(product_id)
        if product is not None:
            products_wishlist.append(product)
    
    return render_template('panier.html', products=products, total=total, whishlist_product=products_wishlist)

@app.route('/add_to_cart/<int:product_id>')
@login_required
def add_to_cart(product_id):
    user = Users.query.get(current_user.id)
    cart = json.loads(user.cart)
    print(cart)
    print(type(cart))
    cart.append(product_id)
    user.cart = json.dumps(cart)
    db.session.commit()
    return redirect(url_for('home'))

@app.route('/remove_from_cart/<int:product_id>')
@login_required
def remove_from_cart(product_id):
    user = Users.query.get(current_user.id)
    cart = json.loads(user.cart)
    cart.remove(product_id)
    user.cart = json.dumps(cart)
    db.session.commit()
    return redirect(url_for('panier'))

@app.route('/buy')
@login_required
def buy():
    user = Users.query.get(current_user.id)
    cart = json.loads(user.cart)
    prix = 0
    for product_id in cart:
        product = Items.query.get(product_id)
        if product is not None:
            prix += product.prix
    now = datetime.now()
    datenow = now.strftime("%d/%m/%Y, %H:%M:%S")
    order = Orders(user_id=current_user.id, prix=prix, status='pending', date=datenow)
    db.session.add(order)
    db.session.commit()
    user.cart = json.dumps([])
    db.session.commit()
    return redirect(url_for('account'))

@app.route('/add_to_wl/<int:product_id>')
@login_required
def add_to_wl(product_id):
    user = Users.query.get(current_user.id)
    wishlist = json.loads(user.wishlist)
    wishlist.append(product_id)
    user.wishlist = json.dumps(wishlist)
    db.session.commit()
    return redirect(url_for('panier'))

@app.route('/remove_from_wl/<int:product_id>')
@login_required
def remove_from_wl(product_id):
    user = Users.query.get(current_user.id)
    wishlist = json.loads(user.wishlist)
    wishlist.remove(product_id)
    user.wishlist = json.dumps(wishlist)
    db.session.commit()
    return redirect(url_for('panier'))

@app.route('/add_comment/<int:product_id>', methods=['POST'])
@login_required
def add_comment(product_id):
    content = request.form['content']
    comment = Comments(description=content, user_id=current_user.id, product_id=product_id)
    db.session.add(comment)
    db.session.commit()
    return redirect(url_for('item_info', id=product_id))

@app.route('/delete_comment/<int:id>')
@login_required
def delete_comment(id):
    comment = Comments.query.get(id)
    if comment is None:
        return redirect(url_for('index'))
    if (current_user.admin != 1) and (comment.user_id != current_user.id):
        return "You do not have the permissions to delete this comment."
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('item_info', id=comment.product_id))

@app.route('/modify_comment/<int:id>', methods=['POST'])
@login_required
def modify_comment(id):
    comment = Comments.query.get(id)
    print(comment.id)
    print(comment.description)
    if comment is None:
        return redirect(url_for('index'))
    if (current_user.admin != 1) and (comment.user_id != current_user.id):
        return "You do not have the permissions to modify this comment."
    comment.description = request.form['content']
    db.session.commit()
    return redirect(url_for('item_info', id=comment.product_id))

@app.route('/search', methods=['POST'])
def search():
    if request.method == 'POST':
        search = request.form['search']
        products = Items.query.filter(Items.name.like('%'+search+'%')).all()
        return render_template('home.html', items=products)

if __name__ == '__main__':
    app.run(debug=True, port=5003)
