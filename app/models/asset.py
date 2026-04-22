from app.extensions import db


class Asset(db.Model):
    __tablename__ = "assets"

    id = db.Column(db.Integer, primary_key=True)
    asset_name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    serial_number = db.Column(db.String(120), unique=True, nullable=False)
    status = db.Column(db.String(50), nullable=False, default="Working Fine")
    lab_id = db.Column(db.Integer, db.ForeignKey("labs.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    lab = db.relationship("Lab", back_populates="assets")
    creator = db.relationship("User", back_populates="assets_created")

    def __repr__(self):
        return f"<Asset {self.asset_name} ({self.status})>"
