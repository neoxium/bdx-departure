"""
BDX Departure Checker Test suite
"""
from src import cli
from datetime import datetime
import pytest
import pytz
import pandas


def test_arg_to_datetime():
    """
    Tests valid time from input argument
    """
    with pytest.raises(SystemExit):
        cli.arg_to_datetime('25:75')
    assert isinstance(cli.arg_to_datetime('12:00'), datetime)


def test_round_minutes():
    rounded = [x for x in map(cli.round_minutes, range(0, 100))]
    assert min(rounded) == 0 \
        and max(rounded) == 55


def test_dataframe_from_response():
    """
    Tests valid dataframe from expected api response.
    """
    response = """
    {
        "nhits": 193,
        "parameters": {
            "dataset": "ci_courb_a",
            "timezone": "UTC",
            "rows": 1,
            "format": "json"
        },
        "records": [
            {
                "datasetid": "ci_courb_a",
                "recordid": "4525c52b6a75de3595ff043941ebe8e423062207",
                "fields": {
                    "bm_prevision": 250,
                    "bm_refdense": 250,
                    "bm_reffluid": 200,
                    "bm_heure": "2020-01-29T06:00:00+00:00",
                    "bm_cdate": "2011-06-09",
                    "bm_actuel": 784,
                    "bm_ident": 72,
                    "bm_gid": 1,
                    "bm_mdate": "2020-01-29T23:00:49+00:00",
                    "bm_refexcep": 250
                },
                "record_timestamp": "2020-01-29T22:05:00.422000+00:00"
            }
        ]
    }
    """
    df = cli.dataframe_from_response(response)

    assert isinstance(df, pandas.DataFrame) \
        and df.iloc[0].bm_prevision == 250 \
        and df.iloc[0].bm_heure.to_pydatetime() == datetime(2020, 1, 29, 6, 0, 0, 0, pytz.UTC)