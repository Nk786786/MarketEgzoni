from flask import Flask, render_template, request, session, redirect, url_for, flash
from datetime import timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message

app = Flask(__name__)

app.secret_key = "eol"
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
    MAIL_PASSWORD='h*******a'
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
    product = db.Column(db.String(100))
    quantity = db.Column(db.String(100))

    def __init__(self, product, quantity):
        self.product = product
        self.quantity = quantity


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
        product = request.form["product"]
        quantity = request.form["quantity"]
        found = stocks.query.filter_by(product=product).first()
        if found:
            found.quantity = quantity
            db.session.commit()
        else:
            stc = stocks(product, quantity)
            db.session.add(stc)
            db.session.commit()
    return render_template("write.html")


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
    length = len(orders)
    return render_template('index.html', length=length)


@app.route("/ushqime", methods=["POST", "GET"])
def space():
    found_product = stocks.query.filter_by(product="Doritos Cool Ranch").first()
    sasia = found_product.quantity
    found_product1 = stocks.query.filter_by(product="Doritos Cheese Supreme").first()
    sasia1 = found_product1.quantity
    found_product2 = stocks.query.filter_by(product="Doritos Nacho Cheese").first()
    sasia2 = found_product2.quantity
    found_product3 = stocks.query.filter_by(product="Doritos Spicy Sweet Chili").first()
    sasia3 = found_product3.quantity
    found_product4 = stocks.query.filter_by(product="Doritos Chilli").first()
    sasia4 = found_product4.quantity
    found_product5 = stocks.query.filter_by(product="Patos Bahrati").first()
    sasia5 = found_product5.quantity
    found_product6 = stocks.query.filter_by(product="Patos Rolls").first()
    sasia6 = found_product6.quantity
    found_product7 = stocks.query.filter_by(product="Patos Classic").first()
    sasia7 = found_product7.quantity
    found_product8 = stocks.query.filter_by(product="Patos Critos").first()
    sasia8 = found_product8.quantity
    found_product9 = stocks.query.filter_by(product="Plazma 150g").first()
    sasia9 = found_product9.quantity
    found_product10 = stocks.query.filter_by(product="Plazma 300g").first()
    sasia10 = found_product10.quantity
    found_product11 = stocks.query.filter_by(product="Plazma 600g").first()
    sasia11 = found_product11.quantity
    found_product12 = stocks.query.filter_by(product="Plazma të bluar 300g").first()
    sasia12 = found_product12.quantity
    found_product13 = stocks.query.filter_by(product="Plazma të bluar 800g").first()
    sasia13 = found_product13.quantity
    found_product14 = stocks.query.filter_by(product="Snickers").first()
    sasia14 = found_product14.quantity
    found_product15 = stocks.query.filter_by(product="Mars").first()
    sasia15 = found_product15.quantity
    found_product16 = stocks.query.filter_by(product="Milky Way").first()
    sasia16 = found_product16.quantity
    found_product17 = stocks.query.filter_by(product="Twix").first()
    sasia17 = found_product17.quantity
    found_product18 = stocks.query.filter_by(product="Raffaello").first()
    sasia18 = found_product18.quantity
    found_product19 = stocks.query.filter_by(product="Bisfino").first()
    sasia19 = found_product19.quantity
    found_product20 = stocks.query.filter_by(product="Bisfino e vogël").first()
    sasia20 = found_product20.quantity
    found_product21 = stocks.query.filter_by(product="Romantic").first()
    sasia21 = found_product21.quantity
    found_product22 = stocks.query.filter_by(product="Samba").first()
    sasia22 = found_product22.quantity
    found_product23 = stocks.query.filter_by(product="Merci").first()
    sasia23 = found_product23.quantity
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            category = "Ushqime"
            quantity = request.form["quantity"]
            if 'submit' in request.form:
                if int(sasia) >= int(quantity):
                    product = "Doritos Cool Ranch"
                    qmimi = 0.9
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit1' in request.form:
                if int(sasia1) >= int(quantity):
                    product = "Doritos Cheese Supreme"
                    qmimi = 0.9
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit2' in request.form:
                if int(sasia2) >= int(quantity):
                    product = "Doritos Nacho Cheese"
                    qmimi = 0.9
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit3' in request.form:
                if int(sasia3) >= int(quantity):
                    product = "Doritos Spicy Sweet Chili"
                    qmimi = 0.9
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit4' in request.form:
                if int(sasia4) >= int(quantity):
                    product = "Doritos Chilli"
                    qmimi = 0.9
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit5' in request.form:
                if int(sasia5) >= int(quantity):
                    product = "Patos Bahrati"
                    qmimi = 1.1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit6' in request.form:
                if int(sasia6) >= int(quantity):
                    product = "Patos Rolls"
                    qmimi = 1.1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit7' in request.form:
                if int(sasia7) >= int(quantity):
                    product = "Patos Classic"
                    qmimi = 1.1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit8' in request.form:
                if int(sasia8) >= int(quantity):
                    product = "Patos Critos"
                    qmimi = 1.1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit9' in request.form:
                if int(sasia9) >= int(quantity):
                    product = "Plazma 150g"
                    qmimi = 1.7
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit10' in request.form:
                if int(sasia10) >= int(quantity):
                    product = "Plazma 300g"
                    qmimi = 3.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit11' in request.form:
                if int(sasia11) >= int(quantity):
                    product = "Plazma 600g"
                    qmimi = 6
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit12' in request.form:
                if int(sasia12) >= int(quantity):
                    product = "Plazma të bluar 300g"
                    qmimi = 3.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit13' in request.form:
                if int(sasia13) >= int(quantity):
                    product = "Plazma të bluar 800g"
                    qmimi = 7.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit14' in request.form:
                if int(sasia14) >= int(quantity):
                    product = "Snickers"
                    qmimi = 0.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit15' in request.form:
                if int(sasia15) >= int(quantity):
                    product = "Mars"
                    qmimi = 0.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit16' in request.form:
                if int(sasia16) >= int(quantity):
                    product = "Milky Way"
                    qmimi = 0.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit17' in request.form:
                if int(sasia17) >= int(quantity):
                    product = "Twix"
                    qmimi = 1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit18' in request.form:
                if int(sasia18) >= int(quantity):
                    product = "Raffaello"
                    qmimi = 1.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit19' in request.form:
                if int(sasia19) >= int(quantity):
                    product = "Bisfino"
                    qmimi = 1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit20' in request.form:
                if int(sasia20) >= int(quantity):
                    product = "Bisfino e vogël"
                    qmimi = 0.8
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit21' in request.form:
                if int(sasia21) >= int(quantity):
                    product = "Romantic"
                    qmimi = 1.1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit22' in request.form:
                if int(sasia22) >= int(quantity):
                    product = "Samba"
                    qmimi = 1.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit23' in request.form:
                if int(sasia23) >= int(quantity):
                    product = "Merci"
                    qmimi = 2.1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
    length = len(orders)

    return render_template('Spaceinvaders.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)),
                           length=length, sasia=sasia, sasia1=sasia1, sasia2=sasia2, sasia3=sasia3, sasia4=sasia4,
                           sasia5=sasia5, sasia6=sasia6, sasia7=sasia7, sasia8=sasia8, sasia9=sasia9, sasia10=sasia10,
                           sasia11=sasia11, sasia12=sasia12, sasia13=sasia13, sasia14=sasia14, sasia15=sasia15,
                           sasia16=sasia16, sasia17=sasia17, sasia18=sasia18, sasia19=sasia19, sasia20=sasia20,
                           sasia21=sasia21, sasia22=sasia22, sasia23=sasia23)


@app.route("/pije", methods=["POST", "GET"])
def dino():
    found_product = stocks.query.filter_by(product="Coca Cola kanace").first()
    sasia = found_product.quantity
    found_product1 = stocks.query.filter_by(product="Coca Cola 2l").first()
    sasia1 = found_product1.quantity
    found_product2 = stocks.query.filter_by(product="Coca Cola 1.5l").first()
    sasia2 = found_product2.quantity
    found_product3 = stocks.query.filter_by(product="Fanta Orangje 2l").first()
    sasia3 = found_product3.quantity
    found_product4 = stocks.query.filter_by(product="Fanta Exotic Ks 2l").first()
    sasia4 = found_product4.quantity
    found_product5 = stocks.query.filter_by(product="Fanta Exotic Al 2l").first()
    sasia5 = found_product5.quantity
    found_product6 = stocks.query.filter_by(product="Fanta Shokata 2l").first()
    sasia6 = found_product6.quantity
    found_product7 = stocks.query.filter_by(product="Fanta Orangje kanace").first()
    sasia7 = found_product7.quantity
    found_product8 = stocks.query.filter_by(product="Fanta Exotic Al kanace").first()
    sasia8 = found_product8.quantity
    found_product9 = stocks.query.filter_by(product="Frutti Mollë 1l").first()
    sasia9 = found_product9.quantity
    found_product10 = stocks.query.filter_by(product="Frutti Dredhëz 1l").first()
    sasia10 = found_product10.quantity
    found_product11 = stocks.query.filter_by(product="Frutti Portokall 1l").first()
    sasia11 = found_product11.quantity
    found_product12 = stocks.query.filter_by(product="Frutti Dardhë 1l").first()
    sasia12 = found_product12.quantity
    found_product13 = stocks.query.filter_by(product="Frutti Pjeshkë 1l").first()
    sasia13 = found_product13.quantity
    found_product14 = stocks.query.filter_by(product="Smirnoff").first()
    sasia14 = found_product14.quantity
    found_product15 = stocks.query.filter_by(product="Birra Peja kanace").first()
    sasia15 = found_product15.quantity
    found_product16 = stocks.query.filter_by(product="Birra Peja shishe xhami").first()
    sasia16 = found_product16.quantity
    found_product17 = stocks.query.filter_by(product="Birra Shkupi kanace").first()
    sasia17 = found_product17.quantity
    found_product18 = stocks.query.filter_by(product="Birra Shkupi shishe xhami").first()
    sasia18 = found_product18.quantity
    found_product24 = stocks.query.filter_by(product="Jack Daniels Birrë").first()
    sasia24 = found_product24.quantity
    found_product25 = stocks.query.filter_by(product="Jack Daniels Alkool").first()
    sasia25 = found_product25.quantity
    found_product26 = stocks.query.filter_by(product="Birra Lasko shishe xhami").first()
    sasia26 = found_product26.quantity
    found_product27 = stocks.query.filter_by(product="Birra Lasko kanace").first()
    sasia27 = found_product27.quantity
    found_product28 = stocks.query.filter_by(product="Pepsi kanace").first()
    sasia28 = found_product28.quantity
    found_product29 = stocks.query.filter_by(product="Pepsi Zero Sugar kanace").first()
    sasia29 = found_product29.quantity
    found_product30 = stocks.query.filter_by(product="Pepsi 2l").first()
    sasia30 = found_product30.quantity
    found_product31 = stocks.query.filter_by(product="Pepsi 600 ml").first()
    sasia31 = found_product31.quantity
    found_product32 = stocks.query.filter_by(product="Pepsi Diet kanace").first()
    sasia32 = found_product32.quantity
    found_product33 = stocks.query.filter_by(product="Pepsi Diet 2l").first()
    sasia33 = found_product33.quantity
    found_product34 = stocks.query.filter_by(product="Sprite kanace").first()
    sasia34 = found_product34.quantity
    found_product35 = stocks.query.filter_by(product="Sprite 2l").first()
    sasia35 = found_product35.quantity
    found_product36 = stocks.query.filter_by(product="Sprite Lemon Lime 2l").first()
    sasia36 = found_product36.quantity
    found_product37 = stocks.query.filter_by(product="Sprite 0.5l").first()
    sasia37 = found_product37.quantity
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            category = "Pije"
            quantity = request.form["quantity"]
            if 'submit' in request.form:
                if int(sasia) >= int(quantity):
                    product = "Coca Cola kanace"
                    qmimi = 0.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit1' in request.form:
                if int(sasia1) >= int(quantity):
                    product = "Coca Cola 2l"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")

            elif 'submit2' in request.form:
                if int(sasia2) >= int(quantity):
                    product = "Coca Cola 1.5l"
                    qmimi = 0.95
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit3' in request.form:
                if int(sasia3) >= int(quantity):
                    product = "Fanta Orangje 2l"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)


            elif 'submit4' in request.form:
                if int(sasia4) >= int(quantity):
                    product = "Fanta Exotic Ks 2l"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit5' in request.form:
                if int(sasia5) >= int(quantity):
                    product = "Fanta Exotic Al 2l"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit6' in request.form:
                if int(sasia6) >= int(quantity):
                    product = "Fanta Shokata 2l"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit7' in request.form:
                if int(sasia7) >= int(quantity):
                    product = "Fanta Orangje kanace"
                    qmimi = 0.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit8' in request.form:
                if int(sasia8) >= int(quantity):
                    product = "Fanta Exotic Al kanace"
                    qmimi = 0.7
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit9' in request.form:
                if int(sasia9) >= int(quantity):
                    product = "Frutti Mollë 1l"
                    qmimi = 0.75
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit10' in request.form:
                if int(sasia10) >= int(quantity):
                    product = "Frutti Dredhëz 1l"
                    qmimi = 0.75
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit11' in request.form:
                if int(sasia11) >= int(quantity):
                    product = "Frutti Portokall 1l"
                    qmimi = 0.9
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit12' in request.form:
                if int(sasia12) >= int(quantity):
                    product = "Frutti Dardhë 1l"
                    qmimi = 0.75
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit13' in request.form:
                if int(sasia13) >= int(quantity):
                    product = "Frutti Pjeshkë 1l"
                    qmimi = 0.75
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit14' in request.form:
                if int(sasia14) >= int(quantity):
                    product = "Smirnoff"
                    qmimi = 1.4
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit15' in request.form:
                if int(sasia15) >= int(quantity):
                    product = "Birra Peja kanace"
                    qmimi = 0.7
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit16' in request.form:
                if int(sasia16) >= int(quantity):
                    product = "Birra Peja shishe xhami"
                    qmimi = 1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit17' in request.form:
                if int(sasia17) >= int(quantity):
                    product = "Birra Shkupi kanace"
                    qmimi = 0.7
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit18' in request.form:
                if int(sasia18) >= int(quantity):
                    product = "Birra Shkupi shishe xhami"
                    qmimi = 1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit24' in request.form:
                if int(sasia24) >= int(quantity):
                    product = "Jack Daniels Birrë"
                    qmimi = 0.8
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit25' in request.form:
                if int(sasia25) >= int(quantity):
                    product = "Jack Daniels Alkool"
                    qmimi = 4.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit26' in request.form:
                if int(sasia26) >= int(quantity):
                    product = "Birra Lasko shishe xhami"
                    qmimi = 1
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit27' in request.form:
                if int(sasia27) >= int(quantity):
                    product = "Birra Lasko kanace"
                    qmimi = 0.7
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit28' in request.form:
                if int(sasia28) >= int(quantity):
                    product = "Pepsi kanace"
                    qmimi = 0.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit29' in request.form:
                if int(sasia29) >= int(quantity):
                    product = "Pepsi Zero Sugar kanace"
                    qmimi = 0.8
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit30' in request.form:
                if int(sasia30) >= int(quantity):
                    product = "Pepsi 2l"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit31' in request.form:
                if int(sasia31) >= int(quantity):
                    product = "Pepsi 600 ml"
                    qmimi = 0.6
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit32' in request.form:
                if int(sasia32) >= int(quantity):
                    product = "Pepsi Diet kanace"
                    qmimi = 0.7
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit33' in request.form:
                if int(sasia33) >= int(quantity):
                    product = "Pepsi Diet 2l"
                    qmimi = 1.4
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit34' in request.form:
                if int(sasia34) >= int(quantity):
                    product = "Sprite kanace"
                    qmimi = 0.5
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit35' in request.form:
                if int(sasia35) >= int(quantity):
                    product = "Sprite 2l"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit36' in request.form:
                if int(sasia36) >= int(quantity):
                    product = "Sprite Lemon Lime 2l"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit37' in request.form:
                if int(sasia37) >= int(quantity):
                    product = "Sprite 0.5l"
                    qmimi = 0.6
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
    length = len(orders)

    return render_template('dino.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)),
                           length=length, sasia=sasia, sasia1=sasia1, sasia2=sasia2, sasia3=sasia3, sasia4=sasia4,
                           sasia5=sasia5, sasia6=sasia6, sasia7=sasia7, sasia8=sasia8, sasia9=sasia9, sasia10=sasia10,
                           sasia11=sasia11, sasia12=sasia12, sasia13=sasia13, sasia14=sasia14, sasia15=sasia15,
                           sasia16=sasia16, sasia17=sasia17, sasia18=sasia18, sasia24=sasia24, sasia25=sasia25,
                           sasia26=sasia26, sasia27=sasia27, sasia28=sasia28, sasia29=sasia29, sasia30=sasia30,
                           sasia31=sasia31, sasia32=sasia32, sasia33=sasia33, sasia34=sasia34, sasia35=sasia35,
                           sasia36=sasia36, sasia37=sasia37)


@app.route("/higjienë", methods=["POST", "GET"])
def tower():
    found_product = stocks.query.filter_by(product="Abc i lëngjshëm i zi").first()
    sasia = found_product.quantity
    found_product1 = stocks.query.filter_by(product="Abc i lëngjshëm i bardhë").first()
    sasia1 = found_product1.quantity
    found_product2 = stocks.query.filter_by(product="Abc powder detergjent").first()
    sasia2 = found_product2.quantity
    found_product3 = stocks.query.filter_by(product="Abc detergjent për rroba matik").first()
    sasia3 = found_product3.quantity
    found_product4 = stocks.query.filter_by(product="Brush e dhëmbëve për fëmijë Colgate").first()
    sasia4 = found_product4.quantity
    found_product5 = stocks.query.filter_by(product="Brush e dhëmbëve Colgate Double").first()
    sasia5 = found_product5.quantity
    found_product9 = stocks.query.filter_by(product="Brush e dhëmbëve Colgate").first()
    sasia9 = found_product9.quantity
    found_product10 = stocks.query.filter_by(product="Colgate MaxWhite").first()
    sasia10 = found_product10.quantity
    found_product11 = stocks.query.filter_by(product="Colgate MaxFresh Blue").first()
    sasia11 = found_product11.quantity
    found_product12 = stocks.query.filter_by(product="Colgate MaxFresh Green").first()
    sasia12 = found_product12.quantity
    found_product13 = stocks.query.filter_by(product="Colgate Herbal").first()
    sasia13 = found_product13.quantity
    found_product14 = stocks.query.filter_by(product="Domestos i gjelbër").first()
    sasia14 = found_product14.quantity
    found_product15 = stocks.query.filter_by(product="Domestos i kaltër").first()
    sasia15 = found_product15.quantity
    found_product16 = stocks.query.filter_by(product="Domestos i bardhë").first()
    sasia16 = found_product16.quantity
    found_product17 = stocks.query.filter_by(product="Domestos i verdhë").first()
    sasia17 = found_product17.quantity
    found_product18 = stocks.query.filter_by(product="Schauma Repair and Pflege").first()
    sasia18 = found_product18.quantity
    found_product19 = stocks.query.filter_by(product="Schauma Frucht and Vitamin").first()
    sasia19 = found_product19.quantity
    found_product20 = stocks.query.filter_by(product="Schauma Herbs").first()
    sasia20 = found_product20.quantity
    found_product21 = stocks.query.filter_by(product="Schauma Blossom Oil").first()
    sasia21 = found_product21.quantity
    found_product22 = stocks.query.filter_by(product="Schauma Almond Milk").first()
    sasia22 = found_product22.quantity
    found_product23 = stocks.query.filter_by(product="Schauma Sea Buckthorn").first()
    sasia23 = found_product23.quantity
    found_product24 = stocks.query.filter_by(product="Schauma Color Glanz").first()
    sasia24 = found_product24.quantity
    found_product25 = stocks.query.filter_by(product="Schauma for men shampoo").first()
    sasia25 = found_product25.quantity
    found_product26 = stocks.query.filter_by(product="Schauma Sports Power").first()
    sasia26 = found_product26.quantity
    found_product27 = stocks.query.filter_by(product="Schauma Anti Schuppen").first()
    sasia27 = found_product27.quantity
    found_product28 = stocks.query.filter_by(product="Schauma Hair Activator").first()
    sasia28 = found_product28.quantity
    found_product29 = stocks.query.filter_by(product="Schauma Carbon Force").first()
    sasia29 = found_product29.quantity
    if not "user" in session:
        flash(f"Ju lutem kyçuni!")
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            category = "Higjienë"
            quantity = request.form["quantity"]
            if 'submit' in request.form:
                if int(sasia) >= int(quantity):
                    product = "Abc i lëngjshëm i zi"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit1' in request.form:
                if int(sasia1) >= int(quantity):
                    product = "Abc i lëngjshëm i bardhë"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit2' in request.form:
                if int(sasia2) >= int(quantity):
                    product = "Abc powder detergjent"
                    qmimi = 1.8
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit3' in request.form:
                if int(sasia3) >= int(quantity):
                    product = "Abc detergjent për rroba matik"
                    qmimi = 2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit4' in request.form:
                if int(sasia4) >= int(quantity):
                    product = "Brush e dhëmbëve për fëmijë Colgate"
                    qmimi = 0.8
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit5' in request.form:
                if int(sasia5) >= int(quantity):
                    product = "Brush e dhëmbëve Colgate Double"
                    qmimi = 2.4
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit9' in request.form:
                if int(sasia9) >= int(quantity):
                    product = "Brush e dhëmbëve Colgate"
                    qmimi = 1.4
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit10' in request.form:
                if int(sasia10) >= int(quantity):
                    product = "Colgate MaxWhite"
                    qmimi = 2.8
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit11' in request.form:
                if int(sasia11) >= int(quantity):
                    product = "Colgate MaxFresh Blue"
                    qmimi = 1.7
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit12' in request.form:
                if int(sasia12) >= int(quantity):
                    product = "Colgate MaxFresh Green"
                    qmimi = 0.75
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit13' in request.form:
                if int(sasia13) >= int(quantity):
                    product = "Colgate Herbal"
                    qmimi = 1.3
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit14' in request.form:
                if int(sasia14) >= int(quantity):
                    product = "Domestos i gjelbër"
                    qmimi = 1.6
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit15' in request.form:
                if int(sasia15) >= int(quantity):
                    product = "Domestos i kaltër"
                    qmimi = 1.6
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit16' in request.form:
                if int(sasia16) >= int(quantity):
                    product = "Domestos i bardhë"
                    qmimi = 1.6
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit17' in request.form:
                if int(sasia17) >= int(quantity):
                    product = "Domestos i verdhë"
                    qmimi = 1.6
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit18' in request.form:
                if int(sasia18) >= int(quantity):
                    product = "Schauma Repair and Pflege"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit19' in request.form:
                if int(sasia19) >= int(quantity):
                    product = "Schauma Frucht and Vitamin"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit20' in request.form:
                if int(sasia20) >= int(quantity):
                    product = "Schauma Herbs"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit21' in request.form:
                if int(sasia21) >= int(quantity):
                    product = "Schauma Blossom Oil"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit22' in request.form:
                if int(sasia22) >= int(quantity):
                    product = "Schauma Almond Milk"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit23' in request.form:
                if int(sasia23) >= int(quantity):
                    product = "Schauma Sea Buckthorn"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit24' in request.form:
                if int(sasia24) >= int(quantity):
                    product = "Schauma Color Glanz"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit25' in request.form:
                if int(sasia25) >= int(quantity):
                    product = "Schauma for men shampoo"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit26' in request.form:
                if int(sasia26) >= int(quantity):
                    product = "Schauma Sports Power"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit27' in request.form:
                if int(sasia27) >= int(quantity):
                    product = "Schauma Anti Schuppen"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit28' in request.form:
                if int(sasia28) >= int(quantity):
                    product = "Schauma Hair Activator"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)
                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
            elif 'submit29' in request.form:
                if int(sasia29) >= int(quantity):
                    product = "Schauma Carbon Force"
                    qmimi = 2.2
                    price = int(quantity) * qmimi
                    orders.append(
                        Order(id=len(orders) + 1, category=category, product=product, quantity=int(quantity),
                              price=("%.2f" % round(price, 2)), qmimi=qmimi))
                    prices.append(price)

                else:
                    flash(f"Nuk ka sasi të mjaftueshme ne depo!")
    length = len(orders)

    return render_template('tower.html', orders=orders, prices=prices, total=("%.2f" % round(sum(prices), 2)),
                           length=length, sasia=sasia, sasia1=sasia1, sasia2=sasia2, sasia3=sasia3, sasia4=sasia4,
                           sasia5=sasia5, sasia9=sasia9, sasia10=sasia10,
                           sasia11=sasia11, sasia12=sasia12, sasia13=sasia13, sasia14=sasia14, sasia15=sasia15,
                           sasia16=sasia16, sasia17=sasia17, sasia18=sasia18, sasia19=sasia19, sasia20=sasia20,
                           sasia21=sasia21, sasia22=sasia22, sasia23=sasia23, sasia24=sasia24, sasia25=sasia25,
                           sasia26=sasia26, sasia27=sasia27, sasia28=sasia28, sasia29=sasia29)


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
        return render_template("order.html", orders=orders, length=length, prices=prices,
                               total=("%.2f" % round(sum(prices), 2)))


if __name__ == "__main__":
    db.create_all()
    app.run(debug=True)
