from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)

app.secret_key = "eol"
app.permanent_session_lifetime = timedelta(days=7)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///lists.sqlite3'
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

@app.route("/order", methods=["POST", "GET"])
def order():

    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))

    else:
        length = len(orders)
        if request.method == "POST":
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
                    return redirect(url_for("order"))

            elif 'order' in request.form:
                client = session["user"]
                found_user = lists.query.filter_by(name=client).first()
                email = found_user.email
                phone = found_user.phone
                if len(orders) == 0:
                    flash("Porosia është e zbrazët!")
                else:
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
        return render_template("order.html", orders=orders, length=length, prices=prices, total=("%.2f" % round(sum(prices), 2)))


@app.route("/view")
def view():
    return render_template("view.html", values=lists.query.all())


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
                    msg = Message("Pygames with Eol!",
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
                text = request.form["name"]
                client = session["user"]
                found_user = lists.query.filter_by(name=client).first()
                email = found_user.email
                msg = Message("Pygames with Eol!",
                              sender=email,
                              recipients=["eol.nuha22@gmail.com"])
                msg.body = "Greetings"
                msg.html = render_template('requestfromclient.html', user=client, text=text
                                           )
                mail.send(msg)
            else:
                flash(f"Ju lutem kyçuni!")
                return redirect(url_for('login'))
    return render_template('index.html')


@app.route("/ushqime", methods=["POST", "GET"])
def space():
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            if 'submit' in request.form:
                category = "Ushqime"
                product = "Doritos Cool Ranch"
                quantity = request.form["quantity"]
                qmimi = 0.9
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit1' in request.form:
                category = "Ushqime"
                product = "Doritos Cheese Supreme"
                quantity = request.form["quantity"]
                qmimi = 0.9
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit2' in request.form:
                category = "Ushqime"
                product = "Doritos Nacho Cheese"
                quantity = request.form["quantity"]
                qmimi = 0.9
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit3' in request.form:
                category = "Ushqime"
                product = "Doritos Spicy Sweet Chili"
                quantity = request.form["quantity"]
                qmimi = 0.9
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit4' in request.form:
                category = "Ushqime"
                product = "Doritos Chilli"
                quantity = request.form["quantity"]
                qmimi = 0.9
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit5' in request.form:
                category = "Ushqime"
                product = "Patos Bahrati"
                quantity = request.form["quantity"]
                qmimi = 1.1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit6' in request.form:
                category = "Ushqime"
                product = "Patos Rolls"
                quantity = request.form["quantity"]
                qmimi = 1.1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit7' in request.form:
                category = "Ushqime"
                product = "Patos Classic"
                quantity = request.form["quantity"]
                qmimi = 1.1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit8' in request.form:
                category = "Ushqime"
                product = "Patos Critos"
                quantity = request.form["quantity"]
                qmimi = 1.1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit9' in request.form:
                category = "Ushqime"
                product = "Plazma 150g"
                quantity = request.form["quantity"]
                qmimi = 1.7
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit10' in request.form:
                category = "Ushqime"
                product = "Plazma 300g"
                quantity = request.form["quantity"]
                qmimi = 3.2
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit11' in request.form:
                category = "Ushqime"
                product = "Plazma 600g"
                quantity = request.form["quantity"]
                qmimi = 6
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit12' in request.form:
                category = "Ushqime"
                product = "Plazma të bluar 300g"
                quantity = request.form["quantity"]
                qmimi = 3.5
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit13' in request.form:
                category = "Ushqime"
                product = "Plazma të bluar 800g"
                quantity = request.form["quantity"]
                qmimi = 7.5
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit14' in request.form:
                category = "Ushqime"
                product = "Snickers"
                quantity = request.form["quantity"]
                qmimi = 0.5
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit15' in request.form:
                category = "Ushqime"
                product = "Mars"
                quantity = request.form["quantity"]
                qmimi = 0.5
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit16' in request.form:
                category = "Ushqime"
                product = "Milky Way"
                quantity = request.form["quantity"]
                qmimi = 0.5
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit17' in request.form:
                category = "Ushqime"
                product = "Twix"
                quantity = request.form["quantity"]
                qmimi = 1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit18' in request.form:
                category = "Ushqime"
                product = "Raffaello"
                quantity = request.form["quantity"]
                qmimi = 1.5
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit19' in request.form:
                category = "Ushqime"
                product = "Bisfino"
                quantity = request.form["quantity"]
                qmimi = 1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit20' in request.form:
                category = "Ushqime"
                product = "Bisfino e vogël"
                quantity = request.form["quantity"]
                qmimi = 0.8
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit21' in request.form:
                category = "Ushqime"
                product = "Romantic"
                quantity = request.form["quantity"]
                qmimi = 1.1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit22' in request.form:
                category = "Ushqime"
                product = "Samba"
                quantity = request.form["quantity"]
                qmimi = 1.2
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit23' in request.form:
                category = "Ushqime"
                product = "Merci"
                quantity = request.form["quantity"]
                qmimi = 2.1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)

    return render_template('Spaceinvaders.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)))


@app.route("/pije", methods=["POST", "GET"])
def dino():
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            if 'submit' in request.form:
                category = "Pije"
                product = "Coca Cola kanace"
                quantity = request.form["quantity"]
                qmimi = 0.5
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit1' in request.form:
                category = "Pije"
                product = "Coca Cola 2l"
                quantity = request.form["quantity"]
                qmimi = 1.3
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit2' in request.form:
                category = "Pije"
                product = "Coca Cola 1.5l"
                quantity = request.form["quantity"]
                qmimi = 0.95
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit3' in request.form:
                category = "Pije"
                product = "Fanta Orangje 2l"
                quantity = request.form["quantity"]
                qmimi = 1.3
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit4' in request.form:
                category = "Pije"
                product = "Fanta Exotic Ks 2l"
                quantity = request.form["quantity"]
                qmimi = 1.3
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit5' in request.form:
                category = "Pije"
                product = "Fanta Exotic Al 2l"
                quantity = request.form["quantity"]
                qmimi = 1.3
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit6' in request.form:
                category = "Pije"
                product = "Fanta Shokata 2l"
                quantity = request.form["quantity"]
                qmimi = 1.3
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit7' in request.form:
                category = "Pije"
                product = "Fanta Orangje kanace"
                quantity = request.form["quantity"]
                qmimi = 0.5
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit8' in request.form:
                category = "Pije"
                product = "Fanta Exotic Al kanace"
                quantity = request.form["quantity"]
                qmimi = 0.7
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit9' in request.form:
                category = "Pije"
                product = "Frutti Mollë 1l"
                quantity = request.form["quantity"]
                qmimi = 0.75
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit10' in request.form:
                category = "Pije"
                product = "Frutti Dredhëz 1l"
                quantity = request.form["quantity"]
                qmimi = 0.75
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit11' in request.form:
                category = "Pije"
                product = "Frutti Portokall 1l"
                quantity = request.form["quantity"]
                qmimi = 0.9
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit12' in request.form:
                category = "Pije"
                product = "Frutti Dardhë 1l"
                quantity = request.form["quantity"]
                qmimi = 0.75
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit13' in request.form:
                category = "Pije"
                product = "Frutti Pjeshkë 1l"
                quantity = request.form["quantity"]
                qmimi = 0.75
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit14' in request.form:
                category = "Pije"
                product = "Smirnoff"
                quantity = request.form["quantity"]
                qmimi = 1.4
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit15' in request.form:
                category = "Pije"
                product = "Birra Peja kanace"
                quantity = request.form["quantity"]
                qmimi = 0.7
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit16' in request.form:
                category = "Pije"
                product = "Birra Peja shishe xhami"
                quantity = request.form["quantity"]
                qmimi = 1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit17' in request.form:
                category = "Pije"
                product = "Birra Shkupi kanace"
                quantity = request.form["quantity"]
                qmimi = 0.7
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit18' in request.form:
                category = "Pije"
                product = "Birra Shkupi shishe xhami"
                quantity = request.form["quantity"]
                qmimi = 1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit19' in request.form:
                category = "Ushqime"
                product = "Bisfino"
                quantity = request.form["quantity"]
                qmimi = 1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit20' in request.form:
                category = "Ushqime"
                product = "Bisfino e vogël"
                quantity = request.form["quantity"]
                qmimi = 0.8
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit21' in request.form:
                category = "Ushqime"
                product = "Romantic"
                quantity = request.form["quantity"]
                qmimi = 1.1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit22' in request.form:
                category = "Ushqime"
                product = "Samba"
                quantity = request.form["quantity"]
                qmimi = 1.2
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit23' in request.form:
                category = "Ushqime"
                product = "Merci"
                quantity = request.form["quantity"]
                qmimi = 2.1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit24' in request.form:
                category = "Pije"
                product = "Jack Daniels Birrë"
                quantity = request.form["quantity"]
                qmimi = 0.8
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit25' in request.form:
                category = "Pije"
                product = "Jack Daniels Alkool"
                quantity = request.form["quantity"]
                qmimi = 4.2
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit26' in request.form:
                category = "Pije"
                product = "Birra Lasko shishe xhami"
                quantity = request.form["quantity"]
                qmimi = 1
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit27' in request.form:
                category = "Pije"
                product = "Birra Lasko kanace"
                quantity = request.form["quantity"]
                qmimi = 0.7
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)

    return render_template('dino.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)))


@app.route("/higjienë", methods=["POST", "GET"])
def tower():
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            if 'submit' in request.form:
                category = "Higjienë"
                product = "Abc i lëngjshëm i zi"
                quantity = request.form["quantity"]
                qmimi = 2.2
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit1' in request.form:
                category = "Higjienë"
                product = "Abc i lëngjshëm i bardhë"
                quantity = request.form["quantity"]
                qmimi = 2.2
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit2' in request.form:
                category = "Higjienë"
                product = "Abc powder detergjent"
                quantity = request.form["quantity"]
                qmimi = 1.8
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit3' in request.form:
                category = "Higjienë"
                product = "Abc detergjent për rroba matik"
                quantity = request.form["quantity"]
                qmimi = 2
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit4' in request.form:
                category = "Higjienë"
                product = "Brush e dhëmbëve për fëmijë Colgate"
                quantity = request.form["quantity"]
                qmimi = 0.8
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit5' in request.form:
                category = "Higjienë"
                product = "Brush e dhëmbëve Colgate Double"
                quantity = request.form["quantity"]
                qmimi = 2.4
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit9' in request.form:
                category = "Higjienë"
                product = "Brush e dhëmbëve Colgate"
                quantity = request.form["quantity"]
                qmimi = 1.4
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit10' in request.form:
                category = "Higjienë"
                product = "Colgate MaxWhite"
                quantity = request.form["quantity"]
                qmimi = 2.8
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit11' in request.form:
                category = "Higjienë"
                product = "Colgate MaxFresh Blue"
                quantity = request.form["quantity"]
                qmimi = 1.7
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit12' in request.form:
                category = "Higjienë"
                product = "Colgate MaxFresh Green"
                quantity = request.form["quantity"]
                qmimi = 0.75
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit13' in request.form:
                category = "Higjienë"
                product = "Colgate Herbal"
                quantity = request.form["quantity"]
                qmimi = 1.3
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit14' in request.form:
                category = "Higjienë"
                product = "Domestos i gjelbër"
                quantity = request.form["quantity"]
                qmimi = 1.6
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit15' in request.form:
                category = "Higjienë"
                product = "Domestos i kaltër"
                quantity = request.form["quantity"]
                qmimi = 1.6
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit16' in request.form:
                category = "Higjienë"
                product = "Domestos i bardhë"
                quantity = request.form["quantity"]
                qmimi = 1.6
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)
            elif 'submit17' in request.form:
                category = "Higjienë"
                product = "Domestos i verdhë"
                quantity = request.form["quantity"]
                qmimi = 1.6
                price = int(quantity) * qmimi
                orders.append(
                    Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                          price=("%.2f" % round(price, 2)), qmimi=qmimi))
                prices.append(price)

    return render_template('tower.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)))



if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
