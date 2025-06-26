from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Employee, TonerRequest, CartridgeStock, CartridgeIssue

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# SQLite Config
import os
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://toner_0xlo_user:0gKYMP7RUh6ZMGgspdw3OvMx6WE1Qb3S@dpg-d1ehq0euk2gs73ao6ufg-a.singapore-postgres.render.com/toner_0xlo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------- CREATE TABLES ON STARTUP ----------
with app.app_context():
    db.create_all()

# ---------- AUTH ROUTES ----------

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))
    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('home'))
        else:
            return "Invalid credentials"
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ---------- MAIN ROUTES ----------

@app.route('/')
def home():
    if 'username' not in session:
        return redirect(url_for('login'))
    return render_template('home.html')

# ---------- TONER REQUEST ROUTES ----------

@app.route('/request-toner', methods=['GET', 'POST'])
def request_toner():
    if request.method == 'POST':
        new_request = TonerRequest(
            department=request.form['department'],
            printer_model=request.form['printerModel'],
            toner_type=request.form['tonerType'],
            requested_by=request.form['requestedBy']
        )
        db.session.add(new_request)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('request_toner.html')


@app.route('/view-requests')
def view_requests():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403
    requests = TonerRequest.query.order_by(TonerRequest.date_requested.desc()).all()
    return render_template('view_requests.html', requests=requests)


# ---------- STOCK ROUTES ----------

@app.route('/view-stock')
def view_stock():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403
    stock = CartridgeStock.query.order_by(CartridgeStock.id.asc()).all()
    models = db.session.query(CartridgeStock.printer_model_no).distinct().all()
    models = [model[0] for model in models]
    return render_template('view_stock.html', stock=stock, models=models)



@app.route('/add-stock', methods=['GET', 'POST'])
def add_stock():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403

    if request.method == 'POST':
        printer_model = request.form['printerModel']
        cartridge_no = request.form['cartridgeNo']
        quantity = int(request.form['quantity'])
        issue_to = request.form.get('issueTo', 'None')
        damaged = int(request.form['damaged'])

        # Check if the same stock already exists
        existing_stock = CartridgeStock.query.filter_by(
            printer_model_no=printer_model,
            cartridge_no=cartridge_no
        ).first()

        if existing_stock:
            # Update existing stock quantities
            existing_stock.quantity += quantity
            existing_stock.total_stock += quantity
            existing_stock.damaged += damaged
        else:
            # Create new stock entry
            new_stock = CartridgeStock(
                printer_model_no=printer_model,
                cartridge_no=cartridge_no,
                quantity=quantity,
                issue_to=issue_to,
                damaged=damaged,
                total_stock=quantity
            )
            db.session.add(new_stock)

        db.session.commit()
        return redirect(url_for('view_stock'))

    printer_models = [p[0] for p in db.session.query(CartridgeStock.printer_model_no).distinct().all()]
    cartridge_nos = [c[0] for c in db.session.query(CartridgeStock.cartridge_no).distinct().all()]

    return render_template('add_stock.html',
                           printer_models=printer_models,
                           cartridge_nos=cartridge_nos)


# ---------- ISSUE CARTRIDGE ----------

@app.route('/issue-cartridge', methods=['GET', 'POST'])
def issue_cartridge():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403

    if request.method == 'POST':
        issue = CartridgeIssue(
            employee_name=request.form['employeeName'],
            printer_model_no=request.form['printerModel'],
            cartridge_no=request.form['cartridgeNo'],
            quantity_issued=int(request.form['quantity'])
        )
        db.session.add(issue)

        stock = CartridgeStock.query.filter_by(
            printer_model_no=request.form['printerModel'],
            cartridge_no=request.form['cartridgeNo']
        ).first()

        if stock and stock.total_stock >= int(request.form['quantity']):
            stock.total_stock -= int(request.form['quantity'])
        else:
            return "Insufficient stock"

        db.session.commit()
        return redirect(url_for('view_stock'))

    printer_models = [p[0] for p in db.session.query(CartridgeStock.printer_model_no).distinct().all()]
    cartridge_nos = [c[0] for c in db.session.query(CartridgeStock.cartridge_no).distinct().all()]
    employees = [e.employee_name for e in Employee.query.all()]  # ✅ Fetch employee names

    return render_template('issue_cartridge.html',
                           printer_models=printer_models,
                           cartridge_nos=cartridge_nos,
                           employees=employees)

# ---------- VIEW ISSUED CARTRIDGES ----------

@app.route('/issued-cartridges')
def issued_cartridges():
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized Access", 403
    issued_list = CartridgeIssue.query.order_by(CartridgeIssue.issue_date.desc()).all()
    return render_template('issued_cartridges.html', issued_list=issued_list)

# ---------- HEALTH CHECK ROUTE ----------

@app.route('/healthz')
def health_check():
    return "OK", 200


# ---------- RUN APP ----------
if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=port)

