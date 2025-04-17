import pandas as pd
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# === НАСТРОЙКИ ===
YOUR_EMAIL = "kirill636zhilinsky@gmail.com"              # ← Впиши СВОЙ Gmail
YOUR_APP_PASSWORD = "skkw zbuq dkem qrcw"       # ← Впиши App Password
TO_EMAIL = "kirill636zhilinsky@gmail.com"                # ← Куда отправлять

# === ЗАГРУЗКА ПОРТФЕЛЯ ===
df = pd.read_excel("portfolio.xlsx")
df["Total Invested"] = df["Quantity"] * df["Purchase Price"] + df["Bank Fee"]

# === АКТУАЛЬНЫЕ ЦЕНЫ ===
def get_price(ticker):
    try:
        stock = yf.Ticker(ticker)
        data = stock.history(period="5d")  # Берём за 5 дней, чтобы был шанс получить цену
        if not data.empty:
            return data["Close"].dropna().iloc[-1]  # Последняя доступная цена
        else:
            print(f"{ticker}: Нет данных в history")
            return None
    except Exception as e:
        print(f"{ticker}: Ошибка при получении цены — {e}")
        return None

df["Current Price"] = df["Ticker"].apply(get_price)
df["Current Value"] = df["Quantity"] * df["Current Price"]
df["Profit"] = df["Current Value"] - df["Total Invested"]
df["Profit %"] = (df["Profit"] / df["Total Invested"]) * 100

# === ПИСЬМО ===
summary = df[["Company", "Ticker", "Quantity", "Purchase Price", "Current Price", "Profit", "Profit %"]]
summary_html = summary.to_html(index=False, float_format="%.2f")

total_value = df["Current Value"].sum()
total_profit = df["Profit"].sum()

email_subject = "Ежедневный отчёт по портфелю"
email_body = f"""
<h2>Привет! Вот твой отчёт по портфелю:</h2>
{summary_html}
<p><b>Общая стоимость портфеля:</b> ${total_value:,.2f}</p>
<p><b>Общая прибыль:</b> ${total_profit:,.2f}</p>
"""

msg = MIMEMultipart("alternative")
msg["Subject"] = email_subject
msg["From"] = YOUR_EMAIL
msg["To"] = TO_EMAIL

part = MIMEText(email_body, "html")
msg.attach(part)

with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
    server.login(YOUR_EMAIL, YOUR_APP_PASSWORD)
    server.sendmail(YOUR_EMAIL, TO_EMAIL, msg.as_string())

print("Письмо отправлено успешно!")
