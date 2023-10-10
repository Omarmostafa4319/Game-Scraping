from flask import Flask, render_template, request, send_file
from io import BytesIO
import multiprocessing
import json

from scrapy.crawler import CrawlerProcess
from Scraper.transfermarkt_de import TransferMarktDe
import pandas as pd

app = Flask(__name__)


def calling_spider(spider_name, url, json_name):
    process = CrawlerProcess(
        settings={
            "FEEDS": {
                f"/api/{json_name}.json": {
                    "format": "json",
                    "overwrite": True,
                }
            },
        }
    )
    process.crawl(spider_name, url)
    process.start()
    process.join()  # Wait for the process to finish


def read_data(json_name):
    with open(f"/api/{json_name}.json") as data:
        return json.loads(data.read())[0]


def run_spider_in_process(url):
    calling_spider(spider_name=TransferMarktDe, url=[url], json_name="game")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/download_excel", methods=["POST"])
def download_excel():
    url = request.form["url"]

    # Check if the URL is not empty
    if not url.strip():
        return "Please enter a valid URL."

    # Run the spider in a separate process
    process = multiprocessing.Process(target=run_spider_in_process, args=(url,))
    process.start()
    process.join()  # Wait for the subprocess to finish

    # Call your existing functions to generate Excel file
    Game_Data = read_data(json_name="game")

    # ... (rest of your existing code)
    # Game Date
    Game_Date = Game_Data["Game_Date"]

    # Team 1
    Team_1_Name = Game_Data["Team_1_Name"]
    Team_1_ID = Game_Data["Team_1_ID"]
    Players_Team_1 = Game_Data["Players_Team_1"]
    Players_Team_1_IDs = Game_Data["Players_Team_1_IDs"]

    # Team 2
    Team_2_Name = Game_Data["Team_2_Name"]
    Team_2_ID = Game_Data["Team_2_ID"]
    Players_Team_2 = Game_Data["Players_Team_2"]
    Players_Team_2_IDs = Game_Data["Players_Team_2_IDs"]

    # Create a Pandas DataFrame with the data
    data_1 = {
        "Player's name": Players_Team_1,
        "Squad Number": [5, 26, 6, 39, 7, 31, 10, 16, 27, 7, 14],
        "Player ID": Players_Team_1_IDs,
        "Club name": [Team_1_Name] * 11,
        "Club ID": [Team_1_ID] * 11,
        "Opposition name": [Team_2_Name] * 11,
        "Opposition Club ID": [Team_2_ID] * 11,
        "Home or Away": ["Home"] * 11,
        "Game date": [Game_Date] * 11,
        "Season": ["23/24"] * 11,
    }
    data_2 = {
        "Player's name": Players_Team_2,
        "Squad Number": [6, 4, 26, 27, 10, 21, 12, 8, 9, 18, 20],
        "Player ID": Players_Team_2_IDs,
        "Club name": [Team_2_Name] * 11,
        "Club ID": [Team_2_ID] * 11,
        "Opposition name": [Team_1_Name] * 11,
        "Opposition Club ID": [Team_1_ID] * 11,
        "Home or Away": ["Away"] * 11,
        "Game date": [Game_Date] * 11,
        "Season": ["23/24"] * 11,
    }

    df_1 = pd.DataFrame(data_1)
    df_2 = pd.DataFrame(data_2)

    # Save the tables to Excel sheets
    output = BytesIO()
    with pd.ExcelWriter(output) as writer:
        df_1.to_excel(
            writer, sheet_name="Bokshy into the wild", index=False, startrow=0
        )
        df_2.to_excel(
            writer,
            sheet_name="Bokshy into the wild",
            index=False,
            startrow=len(df_1) + 2,
            header=False,
        )

    output.seek(0)
    return send_file(
        output, as_attachment=True, download_name="Scouting_Full_Notes_VIP.xlsx"
    )


if __name__ == "__main__":
    app.run(debug=True)
    print("+-" * 20 + "Excel sheet created successfully!" + "+-" * 20)
