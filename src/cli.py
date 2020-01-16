"""
Command Line Interface
"""
import argparse
import requests
from datetime import datetime
import pytz
import pandas
import json

API_URL = "https://opendata.bordeaux-metropole.fr/api/records/1.0/search/"
TIMEZONE = "Europe/Paris"


def run():
    """
    Run command from args dict
    :return:
    """
    arg = get_arg()
    param_datetime = str_to_datetime(arg["time"])
    dataframe = dataframe_from_response(request_api())

    previsions = dataframe.bm_prevision

    try:
        requested_prevision = dataframe[dataframe.bm_heure == param_datetime]

        min_prevision = dataframe[previsions == previsions.min()]
        max_prevision = dataframe[previsions == previsions.max()]

        average_prevision = previsions.mean()
        median_prevision = previsions.median()

        result = "It's a great time to leave :)" \
            if requested_prevision.bm_prevision.values[0] < median_prevision \
            else "It's not a very good time to leave :("

        message = ("Prevision: {req_prev} @ {req_hour}\n"
                   "Minimum: {min_prev} @ {min_hour}\n"
                   "Maximum: {max_prev} @ {max_hour}\n"
                   "Average: {avg_prev}\n"
                   "" + result)

        print(message.format(
            req_prev=requested_prevision.bm_prevision.values[0],
            req_hour=param_datetime.strftime("%H:%M"),
            min_prev=min_prevision.bm_prevision.values[0],
            min_hour=time_format(min_prevision.bm_heure.values[0]),
            max_prev=max_prevision.bm_prevision.values[0],
            max_hour=time_format(max_prevision.bm_heure.values[0]),
            avg_prev=average_prevision))

        exit(0)
    except IndexError:
        print("Your departure time may not have been found, try few minutes before or after")
        exit(2)


def get_arg() -> dict:
    """
    Get args from issued command
    :return dict:
    """
    parser = argparse.ArgumentParser(description="BDX TRAFFIC CHECKER")
    parser.add_argument("time", metavar="time", type=str, help="Time to check for (hh:ii)")
    args = parser.parse_args()
    return vars(args)


def str_to_datetime(time_str: str) -> datetime:
    """
    Convert time string hh:mm to datetime
    :param time_str:
    :return:
    """
    try:
        args_parsed = [int(n) for n in time_str.split(":")]
        today = datetime.now(pytz.timezone(TIMEZONE))
        return today.replace(
            hour=args_parsed[0],
            minute=round_minutes(args_parsed[1]),
            second=0,
            microsecond=0)
    except TypeError:
        print("Argument format is invalid.")
        exit(2)
    except ValueError:
        print("Argument value is invalid")
        exit(2)


def dataframe_from_response(response: str) -> pandas.DataFrame:
    """
    Create dataframe from API response
    :param response:
    :return:
    """
    response_dict = json.loads(response)
    data = [record["fields"] for record in response_dict["records"]]
    dataframe = pandas.DataFrame(data)
    dataframe.bm_heure = pandas.to_datetime(dataframe.bm_heure).dt.tz_convert(TIMEZONE)
    return dataframe


def round_minutes(minutes: int) -> int:
    """
    Round number to nearest 5
    :param minutes:
    :return int:
    """
    return 5 * round(minutes / 5)


def request_api() -> str:
    """
    Request API
    :return dict:
    """
    response = requests.get(API_URL, params={"dataset": "ci_courb_a"})
    return response.text


def time_format(dt) -> datetime:
    """
    Convert Numpy Datetime64 to datetime type, timezone aware
    :param dt:
    :return:
    """
    return pandas.to_datetime(dt).strftime("%H:%M")
