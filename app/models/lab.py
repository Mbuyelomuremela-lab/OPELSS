from app.extensions import db


class Lab(db.Model):
    __tablename__ = "labs"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    province_id = db.Column(db.Integer, db.ForeignKey("provinces.id"), nullable=False)
    latitude = db.Column(db.Float, nullable=False, default=0.0)
    longitude = db.Column(db.Float, nullable=False, default=0.0)
    radius_meters = db.Column(db.Float, nullable=False, default=1000.0)

    province = db.relationship("Province", back_populates="labs")
    users = db.relationship("User", back_populates="assigned_lab")
    attendance_logs = db.relationship("AttendanceLog", back_populates="lab", cascade="all, delete-orphan")
    assets = db.relationship("Asset", back_populates="lab", cascade="all, delete-orphan")
    visitors = db.relationship("Visitor", back_populates="lab", cascade="all, delete-orphan")
    enquiries = db.relationship("Enquiry", back_populates="lab", cascade="all, delete-orphan")
    programmes = db.relationship("Programme", back_populates="lab", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Lab {self.name} in {self.province.name if self.province else 'Unknown'}>"
