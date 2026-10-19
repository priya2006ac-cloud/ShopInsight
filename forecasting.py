import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def create_sales_forecast(engine):
    query = """
        SELECT
            DATE_TRUNC('month', order_date)::date AS month,
            SUM(sales) AS actual_sales
        FROM orders
        WHERE order_date IS NOT NULL
        GROUP BY DATE_TRUNC('month', order_date)
        ORDER BY month
    """

    with engine.connect() as conn:
        df = pd.read_sql(query, conn)

    if len(df) < 2:
        return df, pd.DataFrame(
            columns=["month", "forecast_sales"]
        )

    df["month"] = pd.to_datetime(df["month"])
    df["actual_sales"] = pd.to_numeric(
        df["actual_sales"], errors="coerce"
    )
    df = df.dropna(subset=["actual_sales"]).reset_index(drop=True)

    if len(df) < 2:
        return df, pd.DataFrame(
            columns=["month", "forecast_sales"]
        )

    # Use sequential month numbers as the input feature.
    df["month_number"] = np.arange(len(df))

    X = df[["month_number"]]
    y = df["actual_sales"]

    model = LinearRegression()
    model.fit(X, y)

    future_numbers = np.arange(len(df), len(df) + 3)
    future_sales = model.predict(
        pd.DataFrame({"month_number": future_numbers})
    )

    future_sales = np.maximum(future_sales, 0)

    future_dates = pd.date_range(
        start=df["month"].max() + pd.offsets.MonthBegin(1),
        periods=3,
        freq="MS"
    )

    forecast_df = pd.DataFrame({
        "month": future_dates,
        "forecast_sales": np.round(future_sales, 2)
    })

    return df, forecast_df
