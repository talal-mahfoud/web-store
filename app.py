from flask import Flask, render_template, request, redirect, url_for, flash,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json



app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///test06.db'
app.config['SECRET_KEY'] = 'your_secret_key'

db = SQLAlchemy(app)

class USER(db.Model):
    __tablename__='users'
    nameus=db.Column(db.String(50),primary_key=True,nullable=False)
    passus=db.Column(db.Integer,nullable=False)

    # نموذج المنتج
class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    image = db.Column(db.String(200))

# نموذج الطلب
class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_phone = db.Column(db.String(20), nullable=False)
    items = db.Column(db.Text, nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@app.route("/sign")
def sign():
    return render_template('sign.html')

@app.route("/singup0",methods=['post'])
def home():
    nameus=request.form['usname']
    passus=request.form['pass']

    test=USER.query.filter_by(nameus=nameus).first()  
    if test:
        return('الاسم موجود مسبقا')
    else: 
      new_us=USER(
       nameus=nameus,
       passus=passus
    )
      db.session.add(new_us)
      db.session.commit()
      flash('تم التسجيل بنجاح')
      return redirect(url_for('index'))
@app.route("/login")
def login():
   if session.get('logged_in'):
       return redirect(url_for('logout'))
   return render_template('login.html')

@app.route("/login0",methods=['post'])
def log():
    nameus=request.form['usname']
    passus=request.form['pass']
    test=USER.query.filter_by(nameus=nameus,passus=passus).first() 
    if test:
        session['logged_in'] = True
        session['username'] = nameus
        return redirect(url_for('index'))

    else:
       # return"اعد تسجيل الدخول"
        return render_template('user.html',masseg="اعد تسجيل الدخول")
    
@app.route("/logout")
def logout():
    session.pop('logged_in', None)
    session.pop('usname', None)
    session.clear()
    return redirect(url_for('index'))


# الصفحة الرئيسية
@app.route('/')
def index():
    products = Product.query.all()
    
    if session.get('logged_in'):
        username0=f'{session["username"]}تم تسجيل الدخول بإسم'
        return render_template('index.html', products=products,username=username0)
    else:
        return render_template('index.html', products=products)


                               


# صفحة إدارة الطلبات والمنتجات
@app.route('/admin')
def admin():
    products = Product.query.all()
    orders = Order.query.order_by(Order.created_at.desc()).all()
    return render_template('admin.html', products=products, orders=orders,json=json)

# إضافة منتج جديد
@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.form['name']
    description = request.form['description']
    price = float(request.form['price'])
    image = request.form['image']

    new_product = Product(
        name=name,
        description=description,
        price=price,
        image=image
    )
    db.session.add(new_product)
    db.session.commit()
    flash('تمت إضافة المنتج بنجاح!', 'success')
    return redirect(url_for('admin'))

# حذف منتج
@app.route('/delete_product/<int:product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get(product_id)
    if product:
        db.session.delete(product)
        db.session.commit()
        flash('تم حذف المنتج بنجاح!', 'success')
    return redirect(url_for('admin'))

# معالجة طلب الزبون
@app.route('/place_order', methods=['POST'])
def place_order():
    customer_name = request.form['name']
    customer_phone = request.form['phone']
    items = {}
    total = 0.0

    for key, value in request.form.items():
        if key.startswith('item_'):
            product_id = int(key.split('_')[1])
            quantity = int(value)
            if quantity > 0:
                product = Product.query.get(product_id)
                items[product.name] = {
                    'quantity': quantity,
                    'price': product.price
                }
                total += quantity * product.price

    if items:
        new_order = Order(
            customer_name=customer_name,
            customer_phone=customer_phone,
            items=json.dumps(items),
            total=total
        )
        db.session.add(new_order)
        db.session.commit()
        flash('تم استلام طلبك بنجاح!', 'success')
    return redirect(url_for('index'))

# تحديث حالة الطلب
@app.route('/update_status/<int:order_id>', methods=['POST'])
def update_status(order_id):
    order = Order.query.get(order_id)
    if order:
        order.status = request.form['status']
        db.session.commit()
        flash('تم تحديث حالة الطلب بنجاح!', 'success')
    return redirect(url_for('admin'))

if __name__ =="__main__":
    with app.app_context():
         db.create_all()
    app.run(host='0.0.0.0',port=18012)
