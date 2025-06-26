from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Users table
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)

# Toner Requests table
class TonerRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    department = db.Column(db.String(100), nullable=False)
    printer_model = db.Column(db.String(100), nullable=False)
    toner_type = db.Column(db.String(100), nullable=False)
    requested_by = db.Column(db.String(100), nullable=False)
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

# Cartridge Stock table
class CartridgeStock(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    printer_model_no = db.Column(db.String(100), nullable=False)
    cartridge_no = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    issue_to = db.Column(db.String(100), nullable=True)
    damaged = db.Column(db.Integer, nullable=False, default=0)
    total_stock = db.Column(db.Integer, nullable=False)

# Cartridge Issue table
class CartridgeIssue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), nullable=False)
    printer_model_no = db.Column(db.String(100), nullable=False)
    cartridge_no = db.Column(db.String(100), nullable=False)
    quantity_issued = db.Column(db.Integer, nullable=False)
    issue_date = db.Column(db.DateTime, default=datetime.utcnow)

# Employees table
class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    employee_name = db.Column(db.String(100), unique=True, nullable=False)
