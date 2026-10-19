from flask import Flask, render_template
from sqlalchemy import create_engine, text
from forecasting import create_sales_forecast

app = Flask(__name__)

# Replace YOUR_PASSWORD with your PostgreSQL password
engine = create_engine(
    "postgresql+psycopg2://postgres:NewPassword123!@localhost:5432/shopinsight_db"
)

@app.route("/")
def home():
    return """
    <h1>ShopInsight</h1>
    <h2>E-Commerce Sales Analytics</h2>
    <p><a href="/customers">Open Customer Analytics</a></p>
    """

from markupsafe import escape

@app.route("/customers")
def customers():
    with engine.connect() as conn:
        total_customers = conn.execute(text("""
            SELECT COUNT(DISTINCT customer_id)
            FROM orders
            WHERE customer_id IS NOT NULL
        """)).scalar() or 0

        total_sales = conn.execute(text("""
            SELECT COALESCE(SUM(sales), 0)
            FROM orders
        """)).scalar() or 0

        average_spending = conn.execute(text("""
            SELECT AVG(customer_sales)
            FROM (
                SELECT customer_id, SUM(sales) AS customer_sales
                FROM orders
                WHERE customer_id IS NOT NULL
                GROUP BY customer_id
            ) AS customer_totals
        """)).scalar() or 0

        average_orders = conn.execute(text("""
            SELECT AVG(order_count)
            FROM (
                SELECT customer_id,
                       COUNT(DISTINCT order_id) AS order_count
                FROM orders
                WHERE customer_id IS NOT NULL
                GROUP BY customer_id
            ) AS customer_orders
        """)).scalar() or 0

        top_customers = conn.execute(text("""
            SELECT customer_id,
                   MAX(customer_name) AS customer_name,
                   COUNT(DISTINCT order_id) AS total_orders,
                   SUM(sales) AS total_sales
            FROM orders
            WHERE customer_id IS NOT NULL
            GROUP BY customer_id
            ORDER BY total_sales DESC
            LIMIT 10
        """)).mappings().all()

    rows = ""
    for i, c in enumerate(top_customers, start=1):
        rows += f"""
        <tr>
            <td>{i}</td>
            <td>{escape(str(c['customer_name'] or 'Unknown'))}</td>
            <td>{c['total_orders']}</td>
            <td>₹{float(c['total_sales'] or 0):,.2f}</td>
        </tr>
        """

    if not rows:
        rows = '<tr><td colspan="4">No customer records found.</td></tr>'

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>ShopInsight - Customer Analytics</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f1f5f9;
                color: #1e293b;
            }}
            header {{
                background: #172554;
                color: white;
                padding: 22px 30px;
            }}
            header a {{
                color: white;
                margin-right: 18px;
            }}
            main {{
                max-width: 1100px;
                margin: 30px auto;
                padding: 0 20px;
            }}
            .cards {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 25px 0;
            }}
            .card, .table-card {{
                background: white;
                padding: 22px;
                border-radius: 12px;
                box-shadow: 0 3px 12px #0000000d;
            }}
            .card p {{ color: #64748b; }}
            .card h2 {{ color: #2563eb; overflow-wrap: anywhere; }}
            .table-card {{ overflow-x: auto; }}
            table {{ width: 100%; border-collapse: collapse; min-width: 500px; }}
            th, td {{ padding: 14px; border-bottom: 1px solid #e2e8f0; text-align: left; }}
            th {{ background: #eff6ff; }}
        </style>
    </head>
    <body>
        <header>
            <h1>ShopInsight</h1>
            <a href="/">Home</a>
            <a href="/customers">Customers</a>
        </header>
        <main>
            <h1>Customer Analytics</h1>
            <p>Understand customer spending and purchasing behaviour.</p>

            <section class="cards">
                <div class="card">
                    <p>Total Customers</p>
                    <h2>{total_customers}</h2>
                </div>
                <div class="card">
                    <p>Total Sales</p>
                    <h2>₹{float(total_sales):,.2f}</h2>
                </div>
                <div class="card">
                    <p>Average Customer Spending</p>
                    <h2>₹{float(average_spending):,.2f}</h2>
                </div>
                <div class="card">
                    <p>Average Orders per Customer</p>
                    <h2>{float(average_orders):,.2f}</h2>
                </div>
            </section>

            <section class="table-card">
                <h2>Top 10 Customers by Sales</h2>
                <table>
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>Customer</th>
                            <th>Orders</th>
                            <th>Total Sales</th>
                        </tr>
                    </thead>
                    <tbody>{rows}</tbody>
                </table>
            </section>
        </main>
    </body>
    </html>
    """
@app.route("/products")
def products():
    with engine.connect() as conn:
        product_summary = conn.execute(text("""
            SELECT
                product_id,
                MAX(product_name) AS product_name,
                MAX(category) AS category,
                SUM(quantity) AS quantity_sold,
                SUM(sales) AS total_sales,
                SUM(profit) AS total_profit
            FROM orders
            WHERE product_id IS NOT NULL
            GROUP BY product_id
            ORDER BY total_sales DESC
            LIMIT 10
        """)).mappings().all()

        category_summary = conn.execute(text("""
            SELECT
                category,
                SUM(sales) AS total_sales,
                SUM(profit) AS total_profit,
                SUM(quantity) AS quantity_sold
            FROM orders
            GROUP BY category
            ORDER BY total_sales DESC
        """)).mappings().all()

    return render_template(
        "products.html",
        product_summary=product_summary,
        category_summary=category_summary
    )
@app.route("/regions")
def regions():
    with engine.connect() as conn:
        region_summary = conn.execute(text("""
            SELECT
                region,
                SUM(sales) AS total_sales,
                SUM(profit) AS total_profit,
                COUNT(DISTINCT order_id) AS total_orders
            FROM orders
            WHERE region IS NOT NULL
            GROUP BY region
            ORDER BY total_sales DESC
        """)).mappings().all()

        city_summary = conn.execute(text("""
            SELECT
                city,
                MAX(region) AS region,
                SUM(sales) AS total_sales,
                COUNT(DISTINCT order_id) AS total_orders
            FROM orders
            WHERE city IS NOT NULL
            GROUP BY city
            ORDER BY total_sales DESC
            LIMIT 10
        """)).mappings().all()

    return render_template(
        "regions.html",
        region_summary=region_summary,
        city_summary=city_summary
    )
@app.route("/forecast")
def forecast():
    try:
        actual_df, forecast_df = create_sales_forecast(engine)

        actual_data = [
            {
                "month": row["month"].strftime("%b %Y"),
                "sales": float(row["actual_sales"])
            }
            for _, row in actual_df.iterrows()
        ]

        forecast_data = [
            {
                "month": row["month"].strftime("%b %Y"),
                "sales": float(row["forecast_sales"])
            }
            for _, row in forecast_df.iterrows()
        ]

        return render_template(
            "forecast.html",
            actual_data=actual_data,
            forecast_data=forecast_data
        )

    except Exception as e:
        return f"Forecast error: {e}", 500
if __name__ == "__main__":
    app.run(debug=False,use_reloader=False)
