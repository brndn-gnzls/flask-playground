from db import db

class TagModel(db.Model):
    __tablename__ = "tags"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey("stores.id"), nullable=False)

    store = db.relationship("StoreModel", back_populates="tags")

    # Tell SQLAlchemy to go through the secondary table in order to find what items this tag is related to.
    # Go into the secondary table, look at the tag_id ForeignKeys that are linked to this tag's id
    # it will give the items that are related to the tag-id in the secondary table.
    # This also must be done item.py.
    items = db.relationship("ItemModel", back_populates="tags", secondary="items_tags")
