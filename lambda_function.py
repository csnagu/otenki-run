import datetime
import json
import os
import sys

import requests

trello_querystring_template = {
    "key": os.getenv("TRELLO_KEY"),
    "token": os.getenv("TRELLO_TOKEN")
}


def create_trello_checkitems(checklist_id, possible_date):
    url = f"https://api.trello.com/1/checklists/{checklist_id}/checkItems"
    w_list = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    date_format = "%Y-%m-%d"

    for date, pop in possible_date.items():
        # 降水確率が30%以下のときに、checklistへitemを追加する
        if pop <= 0.3:
            querystring = {
                "name": w_list[datetime.datetime.strptime(date.split()[0], date_format).weekday()]
            }
            querystring.update(trello_querystring_template)
            requests.request("POST", url, params=querystring)


def create_trello_checklist(card_id):
    url = f"https://api.trello.com/1/cards/{card_id}/checklists"
    querystring = {
        "name": "チェックリスト"
    }
    querystring.update(trello_querystring_template)

    response = requests.request("POST", url, params=querystring)
    json_response = json.loads(response.text)
    return json_response["id"]


def create_trello_card():
    url = "https://api.trello.com/1/cards"
    # "Sprint" リストの上部に "ランニング" というカードを追加する
    querystring = {
        "idList": "5f53ab966e167d7ac13331ad",
        "idLabels": "5f53ab66cdabcf46c0dc3cae",
        "pos": "top",
        "name": "ランニングする"
    }
    querystring.update(trello_querystring_template)

    response = requests.request("POST", url, params=querystring)
    json_response = json.loads(response.text)
    return json_response["id"]


def get_5days_weather_forecast():
    url = "https://api.openweathermap.org/data/2.5/forecast"
    querystring = {
        "q": "saitama,jp",
        "appid": os.getenv("OPENWEATHERMAP_KEY")
    }

    response = requests.request("GET", url, params=querystring)
    if response.status_code != 200:
        print(response.text)
        sys.exit(-1)

    return response.text


def lambda_handler(event, context):
    response = get_5days_weather_forecast()

    if response == None:
        print("weather forecast request returns None.")
        sys.exit()
    json_response = json.loads(response)

    possible_date = dict()
    for data in json_response["list"]:
        if "06:00:00" in data["dt_txt"]:
            possible_date[data["dt_txt"]] = data["pop"]

    card_id = create_trello_card()
    checklist_id = create_trello_checklist(card_id)
    create_trello_checkitems(checklist_id, possible_date)
