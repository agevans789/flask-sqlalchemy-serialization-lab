from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow # Add this
from sqlalchemy import MetaData
from sqlalchemy.ext.associationproxy import association_proxy

metadata = MetaData(naming_convention={
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
})

db = SQLAlchemy(metadata=metadata)
ma = Marshmallow() # Initialize ma here without the app

# --- Models ---
class Customer(db.Model):
    __tablename__ = 'customers'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    reviews = db.relationship('Review', back_populates='customer')
    items = association_proxy('reviews', 'item')

class Item(db.Model):
    __tablename__ = 'items'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    price = db.Column(db.Float)
    reviews = db.relationship('Review', back_populates='item')

class Review(db.Model):
    __tablename__ = 'reviews'
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String)
    customer_id = db.Column(db.Integer, db.ForeignKey('customers.id'))
    item_id = db.Column(db.Integer, db.ForeignKey('items.id'))
    customer = db.relationship('Customer', back_populates='reviews')
    item = db.relationship('Item', back_populates='reviews')

# --- Schemas (Fixes the NameError in tests) ---
# --- Schemas ---

class ReviewSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Review
        load_instance = True
        include_fk = True  # Includes foreign keys like customer_id

    # The test expects 'customer' and 'item' keys in the review dictionary
    customer = ma.Nested("CustomerSchema", exclude=("reviews",))
    item = ma.Nested("ItemSchema", exclude=("reviews",))

class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True

    # The test expects a 'reviews' key in the customer dictionary
    reviews = ma.Nested(ReviewSchema, many=True, exclude=("customer",))

class ItemSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Item
        load_instance = True

    # The test expects a 'reviews' key in the item dictionary
    reviews = ma.Nested(ReviewSchema, many=True, exclude=("item",))


