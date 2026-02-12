from flask import Flask, request, render_template_string
import pickle
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64

app = Flask(__name__)

# ==============================
# LOAD MODELS
# ==============================
model_A = pickle.load(open("model_A.pkl", "rb"))
model_B = pickle.load(open("model_B.pkl", "rb"))
model_C = pickle.load(open("model_C.pkl", "rb"))

# ==============================
# HTML PAGE
# ==============================
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Demand Forecasting System</title>
    <style>
        body {
            font-family: Arial;
            background: linear-gradient(to right, #1e3c72, #2a5298);
            text-align: center;
            padding-top: 50px;
        }
        .card {
            background: white;
            width: 500px;
            margin: auto;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0px 0px 20px rgba(0,0,0,0.3);
        }
        input, select, button {
            padding: 10px;
            width: 80%;
            margin: 10px;
            border-radius: 8px;
            border: none;
        }
        button {
            background-color: #2a5298;
            color: white;
            font-weight: bold;
            cursor: pointer;
        }
        h3 {
            color: green;
        }
    </style>
</head>
<body>

<div class="card">
    <h2>📊 Demand Forecasting System</h2>

    <form method="POST">
        <input type="date" name="date" required>

        <select name="product" required>
            <option value="A">Product A</option>
            <option value="B">Product B</option>
            <option value="C">Product C</option>
        </select>

        <button type="submit">Predict Demand</button>
    </form>

    {% if prediction %}
        <h3>Predicted Demand: {{ prediction }}</h3>
    {% endif %}

    {% if graph_url %}
        <img src="data:image/png;base64,{{ graph_url }}" width="350"><br><br>
    {% endif %}

    {% if product_name %}
        <h4>Selected Product: {{ product_name }}</h4>
    {% endif %}

</div>

</body>
</html>
"""

# ==============================
# ROUTE
# ==============================
@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    graph_url = None
    product_name = None

    if request.method == "POST":
        date_input = request.form["date"]
        product_choice = request.form["product"]

        # Select correct model
        if product_choice == "A":
            model = model_A
            product_name = "Product A"
        elif product_choice == "B":
            model = model_B
            product_name = "Product B"
        else:
            model = model_C
            product_name = "Product C"

        # Convert date
        date_ordinal = datetime.strptime(date_input, "%Y-%m-%d").toordinal()

        df = pd.DataFrame([[date_ordinal]], columns=["Date"])
        result = model.predict(df)[0]
        prediction = round(abs(result), 2)

        # Create Graph
        base_date = datetime.strptime(date_input, "%Y-%m-%d")
        date_range = [base_date + timedelta(days=i) for i in range(-5, 5)]

        ordinal_dates = [d.toordinal() for d in date_range]
        preds = model.predict(pd.DataFrame(ordinal_dates, columns=["Date"]))

        plt.figure()
        plt.plot(date_range, preds)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%d-%m-%Y'))
        plt.xticks(rotation=45)
        plt.title("Demand Trend")
        plt.tight_layout()

        img = io.BytesIO()
        plt.savefig(img, format='png')
        img.seek(0)
        graph_url = base64.b64encode(img.getvalue()).decode()
        plt.close()

    return render_template_string(
        HTML_PAGE,
        prediction=prediction,
        graph_url=graph_url,
        product_name=product_name
    )

# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    app.run(debug=True)
