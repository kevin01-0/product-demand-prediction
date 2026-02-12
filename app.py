from flask import Flask, render_template, request, redirect, url_for, session
import pickle
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load models
model_A = pickle.load(open("model_A.pkl", "rb"))
model_B = pickle.load(open("model_B.pkl", "rb"))
model_C = pickle.load(open("model_C.pkl", "rb"))

# ================= LOGIN =================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Simple authentication
        if email == "admin@gmail.com" and password == "1234":
            session["user"] = email
            return redirect(url_for("home"))
        else:
            return "Invalid Login"

    return render_template("login.html")


# ================= HOME =================
@app.route("/home", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    prediction = None
    graph_url = None
    product_name = None

    if request.method == "POST":
        date_input = request.form["date"]
        product_choice = request.form["product"]

        model = model_A if product_choice == "A" else model_B if product_choice == "B" else model_C

        date_ordinal = datetime.strptime(date_input, "%Y-%m-%d").toordinal()
        df = pd.DataFrame([[date_ordinal]], columns=["Date"])
        result = model.predict(df)[0]
        prediction = round(abs(result), 2)

        base_date = datetime.strptime(date_input, "%Y-%m-%d")
        date_range = [base_date + timedelta(days=i) for i in range(-5, 5)]
        ordinal_dates = [d.toordinal() for d in date_range]
        preds = model.predict(pd.DataFrame(ordinal_dates, columns=["Date"]))

        plt.figure()
        plt.plot(date_range, preds)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        plt.xticks(rotation=45)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

        product_name = product_choice

    return render_template("home.html",
                           prediction=prediction,
                           graph_url=graph_url,
                           product_name=product_name)


# ================= LOGOUT =================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(debug=True)

