from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

class TonerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100))
    printer_model = db.Column(db.String(100))
    toner_type = db.Column(db.String(100))
    requested_by = db.Column(db.String(100))
    request_date = db.Column(db.DateTime, server_default=db.func.now())

class CartridgeStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    printer_model_no = db.Column(db.String(100))
    cartridge_no = db.Column(db.String(100))
    quantity = db.Column(db.Integer)
    issue_to = db.Column(db.String(100))
    damaged = db.Column(db.Integer)
    total_stock = db.Column(db.Integer)

class CartridgeIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100))
    printer_model_no = db.Column(db.String(100))
    cartridge_no = db.Column(db.String(100))
    quantity_issued = db.Column(db.Integer)
    issue_date = db.Column(db.DateTime, server_default=db.func.now())

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100))
    designation = db.Column(db.String(100))
    contact = db.Column(db.String(20))
