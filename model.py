from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

db = SQLAlchemy()

class Users(db.Model):

  id = db.Column(db.Integer, primary_key=True)
  username = db.Column(db.String(100), unique=True, nullable=False)
  email = db.Column(db.String(100), unique=True, nullable=False)
  password = db.Column(db.String(100), nullable=False)
  admin = db.Column(db.Integer, nullable=False)
  cart = db.Column(db.JSON)
  wishlist = db.Column(db.JSON)

  def check_password(self, password):
    if self.password == password:
      return True
    else:
      return False
    
  def is_authenticated(self):
    return True
  
  def is_admin(self):
    if self.admin == 1:
      return True
  
  def is_active(self):
    return True
  
  def is_anonymus(self):
    return False
  
  def get_id(self):
    return str(self.id)
  
class Items(db.Model):
  __tablename__ = "items"

  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100))
  description = db.Column(db.String(100))
  prix = db.Column(db.Float(20))
  image = db.Column(db.String(100))

class Comments(db.Model):
  __tablename__ = "comments"

  id = db.Column(db.Integer, primary_key=True)
  description = db.Column(db.String(100))
  product_id = db.Column(db.Integer)
  user_id = db.Column(db.Integer)

class Orders(db.Model):
  __tablename__ = "orders"

  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.String(100))
  status = db.Column(db.String(100))
  prix = db.Column(db.Integer)
  user_id = db.Column(db.Integer)
