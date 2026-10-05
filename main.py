# Copyright 2026 Darcy Sprigg

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import yfinance as yf
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.pagesizes import A4
import os
from datetime import date
import matplotlib.pyplot as plt

# Selected stock
input_ticker = "GOOG"

# Main file
def main():

    five_year_stock_data = download_stock_data(input_ticker)
    graph_output_path = generate_price_graph(five_year_stock_data)
    stock_data = yf.Ticker(input_ticker)
    metrics_dict = get_metrics(stock_data)

    generate_pdf(graph_output_path, metrics_dict, stock_data)

    return

# Generate price graph
def generate_price_graph(five_year_stock_data):

    five_year_stock_data["Close"].plot()
    plt.title(f"Five Year {input_ticker} Stock Price")

    graph_output_path = os.path.join("./Stock Price Graphs", f"{input_ticker}_stock_price_graph.png")

    plt.savefig(graph_output_path)

    return graph_output_path
 
# Download stock data
def download_stock_data(input_ticker):

    today = date.today()

    string_date = str(today)
    five_years_ago = str(f"{int(string_date[:4]) - 5}{string_date[4:]}")

    if string_date[5:] == "02-29":
        five_years_ago = five_years_ago[:-1] + "8"

    stock_data = yf.download(input_ticker, start = five_years_ago, end = today)

    return stock_data

# Obtain metrics from stock data
def get_metrics(stock_data):

    stock_info = stock_data.info
    metrics_dict = {}

    trailing_PE_ratio = stock_info.get("trailingPE")
    PB_ratio = stock_info.get("priceToBook", "N/A")
    dividend_yield = stock_info.get("dividendYield")
    return_on_equity = stock_info.get("returnOnEquity")
    debt_to_equity = stock_info.get("debtToEquity")
    earnings_growth = stock_info.get("earningsGrowth")

    metrics_dict["Industry"] = stock_info["industry"]
    metrics_dict["Sector"] = stock_info["sector"]
    metrics_dict["numEmployees"] = stock_info["fullTimeEmployees"]
    metrics_dict["City"] = stock_info["city"]
    metrics_dict["State/Province"] = stock_info["state"]
    metrics_dict["Country"] = stock_info["country"]

    cur_price = stock_data.info["currentPrice"]

    free_cash_flow = stock_info.get("freeCashflow")
    market_cap = stock_info.get("marketCap")
    free_cash_flow_yield = (free_cash_flow / market_cap)

    recKey = stock_info["recommendationKey"]
    if recKey == "strong_buy":
        recKey = "Strong Buy"
    elif recKey == "strong_sell":
        recKey = "Strong Sell"
    elif recKey == "buy":
        recKey = "Buy"
    elif recKey == "sell":
        recKey = "Sell"
    elif recKey == "hold":
        recKey = "Hold"

    metrics_dict["trailing_PE_ratio"] = trailing_PE_ratio
    metrics_dict["PB_ratio"] = PB_ratio
    metrics_dict["dividend_yield"] = dividend_yield
    metrics_dict["return_on_equity"] = return_on_equity
    metrics_dict["debt_to_equity"] = debt_to_equity
    metrics_dict["earnings_growth"] = earnings_growth
    metrics_dict["free_cash_flow_yield"] = free_cash_flow_yield
    metrics_dict["cur_price"] = cur_price
    metrics_dict["recommendationKey"] = recKey
    metrics_dict["recommentationVal"] = stock_info["recommendationMean"]

    return metrics_dict

# Main pdf generation funciton
def generate_pdf(graph_output_path, metrics_dict, stock_data):

    output_path = os.path.join("./Generated_pdfs", f"{input_ticker}_evaluation.pdf")

    output_pdf = Canvas(output_path, pagesize=A4)
    output_pdf.setFont("Times-Bold", 35)
    output_pdf.drawString(120, 765,f"{input_ticker} Stock Overview")

    output_pdf.setFont("Times-Roman", 18)
    output_pdf.drawString(220, 720, f"Dated: {str(date.today())}")

    output_pdf.setFont("Times-Bold", 22)
    output_pdf.drawString(70, 670,f"Company Background:")

    output_pdf.setFont("Times-Roman", 18)
    output_pdf.drawString(70, 630, f"Sector: {metrics_dict["Sector"]}")
    output_pdf.drawString(70, 600, f"Industry: {metrics_dict["Industry"]}")
    output_pdf.drawString(70, 570, f"Number of Employees: {metrics_dict["numEmployees"]}")
    output_pdf.drawString(70, 540, f"Headquarters: {metrics_dict["City"]}, {metrics_dict["State/Province"]}, {metrics_dict["Country"]}")


    output_pdf.setFont("Times-Bold", 22)
    output_pdf.drawString(70, 490,f"Current Analytical Consensus:")

    output_pdf.setFont("Times-Roman", 18)

    output_pdf.drawString(70, 450, f"Recommended Action: {metrics_dict["recommendationKey"]}")
    output_pdf.drawString(70, 420, f"1-5 Buy/Sell Score: {round(metrics_dict["recommentationVal"], 2)}")

    output_pdf.setFont("Times-Bold", 22)
    output_pdf.drawString(70, 370,f"Stock Price Trend:")

    output_pdf.drawImage(graph_output_path, 45, 5, 500, 360)

    # End page 1
    output_pdf.showPage()

    output_pdf.setFont("Times-Roman", 18)
    if metrics_dict["cur_price"] == "N/A":
        output_pdf.drawString(70, 765, "Current Price: N/A")
    else:
        output_pdf.drawString(70, 765, f"Current Price: ${round(metrics_dict["cur_price"], 2)}")

    output_pdf.setFont("Times-Bold", 22)
    output_pdf.drawString(70, 715, "Value Metrics Chart:")

    output_pdf.setFont("Times-Roman", 18)

    for num in [640, 600, 560, 520, 480, 440, 400]:
        output_pdf.rect(75, num, 225, 40)
        output_pdf.rect(300, num, 225, 40)

    output_pdf.drawString(105, 655, "Price-to-Earnings Ratio")
    if metrics_dict["trailing_PE_ratio"] == "N/A" or metrics_dict["trailing_PE_ratio"] is None:
        output_pdf.drawString(400, 655, "N/A")
    else:
        output_pdf.drawString(400, 655, str(round(metrics_dict["trailing_PE_ratio"],2)))

    output_pdf.drawString(125, 615, "Price-to-Book Ratio")
    if metrics_dict["PB_ratio"] == "N/A" or metrics_dict["PB_ratio"] is None:
        output_pdf.drawString(400, 615, "N/A")
    else:
        output_pdf.drawString(400, 615, str(round(metrics_dict["PB_ratio"],2)))

    output_pdf.drawString(140, 575, "Dividend Yield")
    if metrics_dict["dividend_yield"] == "N/A" or metrics_dict["dividend_yield"] is None:
        output_pdf.drawString(400, 575, "N/A")
    else:
        output_pdf.drawString(400, 575, str(round(metrics_dict["dividend_yield"],2)))

    output_pdf.drawString(115, 535, "Free Cash Flow Yield")
    if metrics_dict["free_cash_flow_yield"] == "N/A" or metrics_dict["free_cash_flow_yield"] is None:
        output_pdf.drawString(400, 535, "N/A")
    else:
        output_pdf.drawString(400, 535, str(round(metrics_dict["free_cash_flow_yield"],2)))

    output_pdf.drawString(135, 495, "Return on Equity")
    if metrics_dict["return_on_equity"] == "N/A" or metrics_dict["return_on_equity"] is None:
        output_pdf.drawString(400, 495, "N/A")
    else:
        output_pdf.drawString(400, 495, str(round(metrics_dict["return_on_equity"],2)))

    output_pdf.drawString(115, 455, "Debt-to-Equity Ratio")
    if metrics_dict["debt_to_equity"] == "N/A" or metrics_dict["debt_to_equity"] is None:
        output_pdf.drawString(400, 455, "N/A")
    else:
        output_pdf.drawString(400, 455, str(round(metrics_dict["debt_to_equity"],2)))

    output_pdf.drawString(130, 415, "Earnings Growth")
    if metrics_dict["earnings_growth"] == "N/A" or metrics_dict["earnings_growth"] is None:
        output_pdf.drawString(400, 415, "N/A")
    else:
        output_pdf.drawString(400, 415, str(round(metrics_dict["earnings_growth"],2)))


    output_pdf.setFont("Times-Bold", 22)
    output_pdf.drawString(70, 350, f"{str(stock_data.financials.columns[0])[:4]} Finances Chart:")

    output_pdf.setFont("Times-Roman", 18)

    for num in [275, 235, 195, 155, 115]:
        output_pdf.rect(75, num, 225, 40)
        output_pdf.rect(300, num, 225, 40)

    output_pdf.drawString(138, 290, "Total Revenue")
    output_pdf.drawString(135, 250, "Total Expenses") 
    output_pdf.drawString(142, 210, "Gross Profit")
    output_pdf.drawString(124, 170, "Operating Income")
    output_pdf.drawString(143, 130, "Net Income")

    output_pdf.drawString(355, 290, f"${str(stock_data.financials.loc["Total Revenue"].iloc[0])}")
    output_pdf.drawString(355, 250, f"${str(stock_data.financials.loc["Total Expenses"].iloc[0])}")
    output_pdf.drawString(355, 210, f"${str(stock_data.financials.loc["Gross Profit"].iloc[0])}")
    output_pdf.drawString(355, 170, f"${str(stock_data.financials.loc["Operating Income"].iloc[0])}")
    output_pdf.drawString(355, 130, f"${str(stock_data.financials.loc["Net Income"].iloc[0])}")

    output_pdf.setFont("Times-Roman", 12)
    output_pdf.drawString(240, 50, "Created by Darcy Sprigg")
    output_pdf.drawString(237, 30, "darcysprigg@outlook.com")

    # End page 2
    output_pdf.showPage()

    output_pdf.save()


    return

if __name__ == "__main__":
    main()