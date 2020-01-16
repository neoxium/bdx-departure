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
    param_datetime = arg_to_datetime(arg["time"])
    dataframe = dataframe_from_response(request_api())

    previsions = dataframe.bm_prevision

    try:
        requested_prevision = dataframe[dataframe.bm_heure == param_datetime]

        min_prevision = dataframe[previsions == previsions.min()]
        max_prevision = dataframe[previsions == previsions.max()]

        average_prevision = previsions.mean()

        result = "It's a great time to leave :)" \
            if requested_prevision.bm_prevision.iloc[0] < average_prevision \
            else "It's not a good time to leave :("

        message = ("\nBDX TRAFFIC CHECKER\n\n"
                   "Prevision: {req_prev} @ {req_hour}\n"
                   "Minimum: {min_prev} @ {min_hour}\n"
                   "Maximum: {max_prev} @ {max_hour}\n"
                   "Average: {avg_prev}\n\n"
                   "" + result)

        print(message.format(
            req_prev=requested_prevision.bm_prevision.iloc[0],
            req_hour=time_format(requested_prevision.bm_heure.iloc[0]),

            min_prev=min_prevision.bm_prevision.iloc[0],
            min_hour=time_format(min_prevision.bm_heure.iloc[0]),

            max_prev=max_prevision.bm_prevision.iloc[0],
            max_hour=time_format(max_prevision.bm_heure.iloc[0]),

            avg_prev=int(round(average_prevision))))

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
    return vars(parser.parse_args())


def arg_to_datetime(time_arg: str) -> datetime:
    """
    Convert time string hh:mm to datetime
    :param time_arg:
    :return datetime:
    """
    try:
        args_parsed = [int(n) for n in time_arg.split(":")]
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
    :return pandas.DataFrame:
    """
    response_dict = json.loads(response)
    dataframe = pandas.DataFrame([record["fields"] for record in response_dict["records"]])
    dataframe.bm_heure = pandas.to_datetime(dataframe.bm_heure).dt.tz_convert(TIMEZONE)
    return dataframe


def round_minutes(minutes: int) -> int:
    """
    Round number to nearest 5, avoid next hour overflow
    :param minutes:
    :return int:
    """
    return 55 if minutes > 55 else 5 * round(minutes / 5)


def request_api() -> str:
    """
    Request API
    :return str:
    """
    response = requests.get(API_URL, params={"dataset": "ci_courb_a", "rows": 193})
    return response.text


def time_format(dt) -> str:
    """
    Convert Numpy Datetime64 to datetime type, timezone aware
    :param dt:
    :return str:
    """
    return pandas.to_datetime(dt).strftime("%H:%M")
