# Import Libraries
import scrapy
import re


# Helper Function
def remove_white_spaces(input_string):
    return re.sub(r"\s+", " ", input_string).strip()


# Define Class For Scraping from TransferMarktDe
class TransferMarktDe(scrapy.Spider):
    name = "transfermarkt_de"

    def __init__(self, urls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.start_urls = urls

    def parse(self, response, **kwargs):
        # Game Date
        Game_Date = response.xpath(
            '//p[@class="sb-datum hide-for-small"]/a/text()'
        ).getall()
        Game_Date = remove_white_spaces(Game_Date[1].split(",")[-1])

        # Teams Name
        Teams_Names = response.xpath('//a[@class="sb-vereinslink"]/text()').getall()

        Team_1_Name = Teams_Names[0]
        Team_2_Name = Teams_Names[1]

        # Teams IDs
        Teams_Urls = response.xpath('//a[@class="sb-vereinslink"]/@href').getall()
        Team_1_Url = Teams_Urls[0]
        Team_2_Url = Teams_Urls[1]

        Team_1_ID = Team_1_Url.split("/")[-3]
        Team_2_ID = Team_2_Url.split("/")[-3]

        # Players URLs
        Players_Urls = response.xpath(
            '//span[@class="aufstellung-rueckennummer-name"]//a/@href'
        ).getall()

        # Players Names
        Players_Names = [url.split("/")[1].replace("-", " ") for url in Players_Urls]

        # Players IDs
        Players_IDs = [url.split("/")[-1] for url in Players_Urls]

        #  Check Which UI Appear
        if len(Players_Names) == 22:
            # Team 1
            Players_Team_1 = Players_Names[:11]

            Players_Team_1_IDs = Players_IDs[:11]

            # Team 2
            Players_Team_2 = Players_Names[11:]

            Players_Team_2_IDs = Players_IDs[11:]
        else:
            # Team 1
            Players_Team_1 = response.xpath(
                '//table[@class="aufstellung-spielerliste-table"]//tr/td/a/text()'
            ).getall()
            Players_Team_1 = Players_Team_1[:-1]

            Players_Team_1_Urls = response.xpath(
                '//table[@class="aufstellung-spielerliste-table"]//tr/td/a/@href'
            ).getall()

            Players_Team_1_IDs = [url.split("/")[-1] for url in Players_Team_1_Urls]
            Players_Team_1_IDs = Players_Team_1_IDs[:-1]

            # Team 2
            Players_Team_2_Urls = response.xpath(
                '//span[@class="aufstellung-rueckennummer-name"]//a/@href'
            ).getall()

            Players_Team_2 = [
                url.split("/")[1].replace("-", " ") for url in Players_Team_2_Urls
            ]

            Players_Team_2_IDs = [url.split("/")[-1] for url in Players_Team_2_Urls]

        Players_Team_1 = [name.title() for name in Players_Team_1]
        Players_Team_2 = [name.title() for name in Players_Team_2]

        print(
            "********************************** Scraping **********************************"
        )
        yield {
            # Game Date
            "Game_Date": Game_Date,
            # Teams Name
            "Team_1_Name": Team_1_Name,
            "Team_2_Name": Team_2_Name,
            # Team 1
            "Team_1_ID": Team_1_ID,
            "Players_Team_1": Players_Team_1,
            "Players_Team_1_IDs": Players_Team_1_IDs,
            # Team 2
            "Team_2_ID": Team_2_ID,
            "Players_Team_2": Players_Team_2,
            "Players_Team_2_IDs": Players_Team_2_IDs,
        }

    def start_requests(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        }
        for url in self.start_urls:
            yield scrapy.Request(url, headers=headers, callback=self.parse)
