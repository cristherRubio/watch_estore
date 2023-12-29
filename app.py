from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'watches.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '[m,GMyKn)(Z71Kk{s|e`'

db = SQLAlchemy(app)

# Models
class Status(db.Model):
    __tablename__ = 'status'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)


class Watch(db.Model):
    __tablename__ = 'watch'
    id = db.Column(db.Integer, primary_key=True)
    SKU = db.Column(db.String(255), nullable=False)
    price_buy = db.Column(db.Float, nullable=False)
    date_in = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('status.id'), nullable=False, default=1)
    date_out = db.Column(db.TIMESTAMP, nullable=True)
    price_sell = db.Column(db.Float, nullable=True)
    profit = db.Column(db.Float, nullable=True)
    status = db.relationship('Status', backref=db.backref('watches', lazy=True))

    def __repr__(self):
        return f"<Watch {self.name}>"


# Routes
@app.route('/')
def index():
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Basic authentication (replace with a more secure mechanism in a real application)
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            flash('Login successful!', 'success')
            return redirect(url_for('stock'))
        else:
            flash('Invalid username or password', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('Logout successful!', 'success')
    return redirect(url_for('login'))


@app.route('/stock', methods=['GET', 'POST'])
def stock():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle form submission to add a new item
        sku = request.form.get('SKU')
        price_buy = float(request.form.get('price_buy'))

        # Assuming you have a default status with id 1 (e.g., 'AVAILABLE')
        default_status = Status.query.get(1)

        new_watch = Watch(SKU=sku, price_buy=price_buy, status=default_status)
        db.session.add(new_watch)
        db.session.commit()

        flash('Item added successfully!', 'success')

    # Fetch all watches from the database
    available_watches = Watch.query.filter_by(status_id=1).all()

    return render_template('stock.html', watches=available_watches)


@app.route('/update_status/<int:watch_id>/<int:status_id>')
def update_status(watch_id, status_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    
    if status_id == 2:  # Assuming status_id 2 is for "SOLD"
        return render_template('modal.html', watch_id=watch_id)

    watch = Watch.query.get(watch_id)
    new_status = Status.query.get(status_id)

    if watch and new_status:
        watch.status = new_status
        db.session.commit()
        flash('Status updated successfully!', 'success')
    else:
        flash('Unable to update status', 'error')

    return redirect(url_for('stock'))


@app.route('/handle_sold/<int:watch_id>', methods=['POST'])
def handle_sold(watch_id):
    # Handle the form submission for the "SOLD" status
    store = request.form.get('store')
    sell_price = float(request.form.get('sell_price'))

    # Perform actions with store and sell_price as needed
    # ...

    # Update status to "SOLD" and commit changes
    watch = Watch.query.get(watch_id)
    sold_status = Status.query.filter_by(name='SOLD').first()
    watch.status = sold_status
    db.session.commit()

    flash('Status updated successfully!', 'success')

    return redirect(url_for('stock'))



@app.route('/history', methods=['GET', 'POST'])
def history():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle form submission to modify an entry
        watch_id = request.form.get('watch_id')
        new_status_id = request.form.get('new_status_id')

        # Find the watch by ID
        watch_to_modify = Watch.query.get(watch_id)

        if watch_to_modify:
            # Update the status of the watch
            watch_to_modify.status_id = new_status_id
            db.session.commit()

    # Fetch all watches from the database
    all_watches = Watch.query.all()

    return render_template('history.html', watches=all_watches)


if __name__ == '__main__':
    app.run(debug=True)