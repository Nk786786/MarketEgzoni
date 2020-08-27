from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)


app.secret_key = "thisisthemostsecretkeyever"
app.permanent_session_lifetime = timedelta(weeks=42)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lists.sqlite3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///stocks.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.update(
    DEBUG=True,
    # EMAIL SETTINGS
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USE_SSL=True,
    MAIL_USERNAME='eol.nuha22@gmail.com',
    MAIL_PASSWORD='haxherja'
)
mail = Mail(app)
db = SQLAlchemy(app)


class lists(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(100))
    password = db.Column(db.String(100))

    def __init__(self, name, email, phone, password):
        self.name = name
        self.email = email
        self.phone = phone
        self.password = password


class stocks(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    category = db.Column(db.String(100))
    section = db.Column(db.String(100))
    company = db.Column(db.String(100))
    product = db.Column(db.String(100))
    quantity = db.Column(db.String(100))
    price = db.Column(db.String(100))

    def __init__(self, category, section, company, product, quantity, price):
        self.category = category
        self.section = section
        self.company = company
        self.product = product
        self.quantity = quantity
        self.price = price


class Order:
    def __init__(self, id, category, product, quantity, price, qmimi):
        self.id = id
        self.category = category
        self.product = product
        self.quantity = quantity
        self.price = price
        self.qmimi = qmimi


orders = []
prices = [0]
if len(orders) == 0:
    prices.clear()
length = len(orders)


def base():
    return render_template("base.html", orders=orders, length=length)


@app.route("/view-products")
def view():
    return render_template("view.html", values1=stocks.query.all())


@app.route("/view-users")
def viewUsers():
    return render_template("view-users.html", values=lists.query.all())


@app.route("/admin-write", methods=["POST", "GET"])
def write():
    if request.method == "POST":
        category = request.form["category"]
        section = request.form["section"]
        company = request.form["company"]
        product = request.form["product"]
        price = request.form["price"]
        quantity = request.form["quantity"]
        found = stocks.query.filter_by(product=product).first()
        if found:
            found.category = category
            found.section = section
            found.company = company
            found.price = price
            found.quantity = quantity
            db.session.commit()
        else:
            stc = stocks(category, section, company, product, quantity, price)
            db.session.add(stc)
            db.session.commit()
    return render_template("write.html")


@app.route("/admin-delete", methods=["POST", "GET"])
def delete():
    if request.method == "POST":
        product = request.form["product"]
        found = stocks.query.filter_by(product=product).first()
        if found:
            stocks.query.filter_by(_id=found._id).delete()
            db.session.commit()
    return render_template("delete.html")


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        session.permanent = True
        user = request.form["name"]
        found_user = lists.query.filter_by(name=user).first()
        if found_user:
            password = request.form["password"]
            if found_user.password == password:
                session["user"] = user
                orders.clear()
                prices.clear()
                return redirect(url_for("home"))
            else:
                flash(f"Fjalëkalimi është gabim!")
                return redirect(url_for("login"))

        else:
            flash(f"Emri është gabim!")
            return redirect(url_for("login"))
    else:
        if "user" in session:
            return redirect(url_for("home"))
        return render_template("login.html")


@app.route("/signup", methods=["POST", "GET"])
def signup():
    if request.method == "POST":
        user = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        password = request.form["password"]
        session.permanent = True
        found_user = lists.query.filter_by(name=user).first()
        found_user1 = lists.query.filter_by(email=email).first()
        if found_user:
            flash(f"Ky emër i përdoruesit nuk është i lirë!")
            return redirect(url_for("signup"))
        if found_user1:
            flash(f"Një llogari tjetër është regjistruar me këtë email!")
            return redirect(url_for("signup"))
        usr = lists(user, email, phone, password)
        db.session.add(usr)
        db.session.commit()
        session["user"] = user
        msg = Message("Market Egzoni!",
                      sender="eol.nuha22@gmail.com",
                      recipients=[email])
        msg.html = render_template('Welcome.html', user=user)
        mail.send(msg)
        return redirect(url_for("home"))
    else:
        if "user" in session:
            return redirect(url_for("home"))
        return render_template("signup.html")


@app.route("/forgotpassword", methods=["POST", "GET"])
def password():
    if "user" in session:
        return redirect(url_for('home'))
    if request.method == "POST":
        user = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        session.permanent = True
        found_user = lists.query.filter_by(name=user).first()
        if found_user:
            if found_user.email == email:
                if found_user.phone == phone:
                    msg = Message("Market Egzoni!",
                                  sender="eol.nuha22@gmail.com",
                                  recipients=[email])
                    msg.body = "Greetings " + user + "!"
                    msg.html = render_template('forgot_password.html', user=user, password=found_user.password)
                    mail.send(msg)
                    return render_template("found.html")
                else:
                    flash(f"Numri i telefonit është gabim!")
            else:
                flash(f"Email është gabim!")
        else:
            flash(f"Emri është gabim!")
    return render_template("password.html")


@app.route("/changepassword", methods=["POST", "GET"])
def change():
    if request.method == "POST":
        user = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]
        found_user = lists.query.filter_by(name=user).first()
        if found_user:
            if found_user.email == email:
                if found_user.password == password:
                    if not password == password1:
                        if password1 == password2:
                            found_user.password = password2
                            db.session.commit()
                            session["user"] = user
                            return redirect(url_for('home'))
                        else:
                            flash(f"Fjalëkalimat e ri nuk përputhen!")
                    else:
                        flash(f"Fjalëkalimi i ri nuk mund të jetë i njëjtë me të vjetrin!")
                else:
                    flash(f"Fjalëkalimi i vjetër nuk është i saktë!")
            else:
                flash(f"Email nuk përputhet!")
        else:
            flash(f"Ky emër i përdoruesit nuk egziston!")
    return render_template("change.html")


@app.route("/logout")
def logout():
    if "user" in session:
        flash(f"Shkyçja është bërë me sukses!")
    session.pop("user", None)
    session.pop("password", None)

    return redirect(url_for("login"))


@app.route("/", methods=["POST", "GET"])
@app.route("/home", methods=["POST", "GET"])
def home():
    if request.method == "POST":
        if "user" in session:
            if 'ankes' in request.form:
                text = request.form["name"]
                emri = request.form["emri"]
                adresa = request.form["adresa"]
                titulli = request.form["titulli"]
                client = session["user"]
                found_user = lists.query.filter_by(name=client).first()
                email = found_user.email
                msg = Message(titulli,
                          sender=email,
                          recipients=["eol.nuha22@gmail.com"])
                msg.body = "Greetings"
                msg.html = render_template('requestfromclient.html', user=client, text=text, emri=emri, adresa=adresa, titulli=titulli
                                       )
                mail.send(msg)
            for item in orders:
                if "remove" + str(item.id) in request.form:
                    remove = orders.index(item)
                    orders.pop(remove)
                    prices.pop(remove)
                    length = len(orders)

            if 'submit1' in request.form:
                if not len(orders) == 0:
                    orders.clear()
                    prices.clear()

            elif 'order' in request.form:

                client = session["user"]
                found_user = lists.query.filter_by(name=client).first()
                email = found_user.email
                phone = found_user.phone
                if len(orders) == 0:
                    flash("Porosia është e zbrazët!")
                else:

                    for item in orders:
                        product = item.product
                        found_product = stocks.query.filter_by(product=product).first()
                        sasia = item.quantity
                        new = int(found_product.quantity) - int(sasia)
                        if new >= 0:
                            found_product.quantity = new
                            db.session.commit()
                        else:
                            found_product.quantity = 0
                            db.session.commit()

                    msg = Message("Market Egzoni!",
                                  sender=email,
                                  recipients=["eol.nuha22@gmail.com"])
                    msg.body = "Greetings"
                    msg.html = render_template('client.html', client=client, email=email, phone=phone, orders=orders,
                                               total=("%.2f" % round(sum(prices), 2)))
                    mail.send(msg)
                    orders.clear()
                    prices.clear()
                    length = len(orders)
                    flash(f"Porosia është dërguar me sukses!")

            
            
        else:
            flash(f"Ju lutem kyçuni!")
            return redirect(url_for('login'))
    length = len(orders)
    return render_template('index.html', values1=stocks.query.all(), prices=prices, total=("%.2f" % round(sum(prices), 2)),
                           length=length, orders=orders)


@app.route("/ushqime", methods=["POST", "GET"])
def space():
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            values = stocks.query.all()
            length = len(orders)
            for item in values:
                if 'submit' + item.product in request.form:
                    category = "Ushqime"
                    quantity = request.form["quantity"]
                    if int(item.quantity) >= int(quantity):
                        product = item.product
                        qmimi = item.price
                        price = int(quantity) * float(qmimi)
                        orders.append(
                            Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                                  price=("%.2f" % round(price, 2)), qmimi=qmimi))
                        prices.append(price)
                    else:
                        flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            for item in orders:
                if "remove" + str(item.id) in request.form:
                    remove = orders.index(item)
                    orders.pop(remove)
                    prices.pop(remove)
                    length = len(orders)

            if 'submit1' in request.form:
                if not len(orders) == 0:
                    orders.clear()
                    prices.clear()

            elif 'order' in request.form:

                client = session["user"]
                found_user = lists.query.filter_by(name=client).first()
                email = found_user.email
                phone = found_user.phone
                if len(orders) == 0:
                    flash("Porosia është e zbrazët!")
                else:

                    for item in orders:
                        product = item.product
                        found_product = stocks.query.filter_by(product=product).first()
                        sasia = item.quantity
                        new = int(found_product.quantity) - int(sasia)
                        if new >= 0:
                            found_product.quantity = new
                            db.session.commit()
                        else:
                            found_product.quantity = 0
                            db.session.commit()

                    msg = Message("Market Egzoni!",
                                  sender=email,
                                  recipients=["eol.nuha22@gmail.com"])
                    msg.body = "Greetings"
                    msg.html = render_template('client.html', client=client, email=email, phone=phone, orders=orders,
                                               total=("%.2f" % round(sum(prices), 2)))
                    mail.send(msg)
                    orders.clear()
                    prices.clear()
                    length = len(orders)
                    flash(f"Porosia është dërguar me sukses!")

    length = len(orders)

    return render_template('Spaceinvaders.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)),
                           length=length, values1=stocks.query.all())


@app.route("/pije", methods=["POST", "GET"])
def dino():
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            values = stocks.query.all()
            for item in values:
                if 'submit' + item.product in request.form:
                    category = "Pije"
                    quantity = request.form["quantity"]
                    if int(item.quantity) >= int(quantity):
                        product = item.product
                        qmimi = item.price
                        price = int(quantity) * float(qmimi)
                        orders.append(
                            Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                                  price=("%.2f" % round(price, 2)), qmimi=qmimi))
                        prices.append(price)
                    else:
                        flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            for item in orders:
                if "remove" + str(item.id) in request.form:
                    remove = orders.index(item)
                    orders.pop(remove)
                    prices.pop(remove)
                    length = len(orders)

            if 'submit1' in request.form:
                if not len(orders) == 0:
                    orders.clear()
                    prices.clear()

            elif 'order' in request.form:

                client = session["user"]
                found_user = lists.query.filter_by(name=client).first()
                email = found_user.email
                phone = found_user.phone
                if len(orders) == 0:
                    flash("Porosia është e zbrazët!")
                else:

                    for item in orders:
                        product = item.product
                        found_product = stocks.query.filter_by(product=product).first()
                        sasia = item.quantity
                        new = int(found_product.quantity) - int(sasia)
                        if new >= 0:
                            found_product.quantity = new
                            db.session.commit()
                        else:
                            found_product.quantity = 0
                            db.session.commit()

                    msg = Message("Market Egzoni!",
                                  sender=email,
                                  recipients=["eol.nuha22@gmail.com"])
                    msg.body = "Greetings"
                    msg.html = render_template('client.html', client=client, email=email, phone=phone, orders=orders,
                                               total=("%.2f" % round(sum(prices), 2)))
                    mail.send(msg)
                    orders.clear()
                    prices.clear()
                    length = len(orders)
                    flash(f"Porosia është dërguar me sukses!")
    length = len(orders)
    return render_template('dino.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)),
                           length=length, values1=stocks.query.all())


@app.route("/higjienë", methods=["POST", "GET"])
def tower():
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            values = stocks.query.all()
            for item in values:
                if 'submit' + item.product in request.form:
                    category = "Higjienë"
                    quantity = request.form["quantity"]
                    if int(item.quantity) >= int(quantity):
                        product = item.product
                        qmimi = item.price
                        price = int(quantity) * float(qmimi)
                        orders.append(
                            Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                                  price=("%.2f" % round(price, 2)), qmimi=qmimi))
                        prices.append(price)
                    else:
                        flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            for item in orders:
                if "remove" + str(item.id) in request.form:
                    remove = orders.index(item)
                    orders.pop(remove)
                    prices.pop(remove)
                    length = len(orders)

            if 'submit1' in request.form:
                if not len(orders) == 0:
                    orders.clear()
                    prices.clear()

            elif 'order' in request.form:

                client = session["user"]
                found_user = lists.query.filter_by(name=client).first()
                email = found_user.email
                phone = found_user.phone
                if len(orders) == 0:
                    flash("Porosia është e zbrazët!")
                else:

                    for item in orders:
                        product = item.product
                        found_product = stocks.query.filter_by(product=product).first()
                        sasia = item.quantity
                        new = int(found_product.quantity) - int(sasia)
                        if new >= 0:
                            found_product.quantity = new
                            db.session.commit()
                        else:
                            found_product.quantity = 0
                            db.session.commit()

                    msg = Message("Market Egzoni!",
                                  sender=email,
                                  recipients=["eol.nuha22@gmail.com"])
                    msg.body = "Greetings"
                    msg.html = render_template('client.html', client=client, email=email, phone=phone, orders=orders,
                                               total=("%.2f" % round(sum(prices), 2)))
                    mail.send(msg)
                    orders.clear()
                    prices.clear()
                    length = len(orders)
                    flash(f"Porosia është dërguar me sukses!")
    length = len(orders)
    return render_template('tower.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)),
                           length=length, values1=stocks.query.all())



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
