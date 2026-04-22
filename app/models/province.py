from app.extensions import db


class Province(db.Model):
    __tablename__ = "provinces"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)

    labs = db.relationship("Lab", back_populates="province", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Province {self.name}>"
