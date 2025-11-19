from prophet import Prophet
import pandas as pd


def train_and_forecast(df: pd.DataFrame, periods: int = 7) -> pd.DataFrame:
    dfp = df.rename(columns={"date": "ds", "units_sold": "y"})[["ds", "y"]]
    model = Prophet(yearly_seasonality=True, weekly_seasonality=True)
    model.fit(dfp)
    future = model.make_future_dataframe(periods=periods)
    forecast = model.predict(future)[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(periods)
    forecast.columns = ["date", "predicted_units", "lower_ci", "upper_ci"]
    return forecast
