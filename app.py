from flask import Flask, request, render_template_string, redirect, url_for, session
import pickle
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64

app = Flask(__name__)
app.secret_key = "secret123"

# ==============================
# Load Models
# ==============================
model_A = pickle.load(open("model_A.pkl", "rb"))
model_B = pickle.load(open("model_B.pkl", "rb"))
model_C = pickle.load(open("model_C.pkl", "rb"))

# ==============================
# LOGIN PAGE
# ==============================
LOGIN_PAGE = """
<h2>Login</h2>
<form method="POST">
<input type="text" name="username" placeholder="Username" required><br><br>
<input type="password" name="password" placeholder="Password" required><br><br>
<button type="submit">Login</button>
</form>
"""

# ==============================
# MAIN HTML
# ==============================
HTML_PAGE = """
<h2>📊 Demand Forecasting System</h2>
<a href="/logout"><button>Logout</button></a>

<form method="POST">
<input type="date" name="date" required><br><br>

<select name="product" required>
<option value="A">Product A</option>
<option value="B">Product B</option>
<option value="C">Product C</option>
</select><br><br>

<button type="submit">Predict Demand</button>
</form>

{% if prediction %}
<h3 style="color:green;">Predicted Demand: {{ prediction }}</h3>
{% endif %}

{% if graph_url %}
<img src="data:image/png;base64,{{ graph_url }}" width="400">
{% endif %}
"""

# ==============================
# LOGIN ROUTE
# ==============================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        if username == "admin" and password == "1234":
            session["user"] = username
            return redirect(url_for("home"))
        else:
            return "Invalid Credentials"

    return render_template_string(LOGIN_PAGE)

# ==============================
# HOME ROUTE
# ==============================
@app.route("/", methods=["GET", "POST"])
def home():
    if "user" not in session:
        return redirect(url_for("login"))

    prediction = None
    graph_url = None

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
        plt.xticks(rotation=45)
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

    return render_template_string(HTML_PAGE, prediction=prediction, graph_url=graph_url)

# ==============================
# LOGOUT
# ==============================
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
