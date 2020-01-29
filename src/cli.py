"""
Command Line Interface
"""
import argparse
from datetime import datetime
import json
import pytz
import requests
import pandas

API_URL = "https://opendata.bordeaux-metropole.fr/api/records/1.0/search/"
TIMEZONE = "Europe/Paris"


def run():
    """
    Run command from args dict
    :return:
    """
    arg = get_arg()
    param_datetime = arg_to_datetime(arg["time"])

    try:
        dataframe = dataframe_from_response(request_api())
        previsions = dataframe.bm_prevision
        print(output_str(
            hit=dataframe[dataframe.bm_heure == param_datetime],
            mini=dataframe[previsions == previsions.min()],
            maxi=dataframe[previsions == previsions.max()],
            avg=previsions.mean()))
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
    parser.add_argument("time", metavar="time", type=str, help="Time to check for (hh:mm)")
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


def round_minutes(minutes: int) -> int:
    """
    Round number to nearest 5, avoid next hour overflow
    :param minutes:
    :return int:
    """
    return 55 if minutes > 55 else 5 * round(minutes / 5)


def request_api() -> str:
    """
    Request API for daily records from 7am to 11pm, 193 records a day
    :return str:
    """
    response = requests.get(API_URL, params={"dataset": "ci_courb_a", "rows": 193})
    return response.text


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


def output_str(hit: pandas.DataFrame, mini: pandas.DataFrame, maxi: pandas.DataFrame, avg: float) -> str:
    display_average = int(round(avg))

    result = "It's a great time to leave :)" \
        if hit.bm_prevision.iloc[0] < avg \
        else "It's not a good time to leave :("

    message = ("\nBDX TRAFFIC CHECKER\n\n"
               "Prevision: {req_prev} @ {req_hour}\n"
               "Minimum: {min_prev} @ {min_hour}\n"
               "Maximum: {max_prev} @ {max_hour}\n"
               "Average: {avg_prev}\n\n"
               "" + result)

    return message.format(
        req_prev=hit.bm_prevision.iloc[0],
        req_hour=time_format(hit.bm_heure.iloc[0]),

        min_prev=mini.bm_prevision.iloc[0],
        min_hour=time_format(mini.bm_heure.iloc[0]),

        max_prev=maxi.bm_prevision.iloc[0],
        max_hour=time_format(maxi.bm_heure.iloc[0]),

        avg_prev=display_average)


def time_format(dt) -> str:
    """
    Convert Numpy Datetime64 to datetime type, timezone aware
    :param dt:
    :return str:
    """
    return pandas.to_datetime(dt).strftime("%H:%M")
