from db import db


# Mapping row in table to python class.
class ItemModel(db.Model):

    # Create/Use table items.
    __tablename__ = "items"

    # Define columns in table.
    id = db.Column(db.Integer, primary_key=True)  # auto-incrementing
    name = db.Column(db.String(80), unique=True, nullable=False)  # 80 character limit
    description = db.Column(db.String)
    price = db.Column(db.Float(precision=2), unique=False, nullable=False)

    # Map store_id to the id column in the stores table. <<< [!] stores table not stores model or file.
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), unique=False, nullable=False)

    # Define a relationship with the StoreModel class, since store_id defines
    # a relationship with stores table. Below, store now contains a StoreModel
    # object whose id matches the foreign key defined above.
    store = db.relationship("StoreModel", back_populates="items") # back_populate means the StoreModel class will have an items relationship.

    # This also must be done item_tags.py.
    tags = db.relationship("TagModel", back_populates="items", secondary="items_tags")