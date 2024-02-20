import json
import os

import pandas as pd

from . import date_utils as date_utils


def get_dataset_name(file: str) -> str:
    return file.split(os.sep)[-1:][0].replace(".csv", "")


def _frame_to_json(frame):
    json_str = frame.to_json(orient='records')
    return json.loads(json_str)


def load_dataframe(file_csv):
    return pd.read_csv(file_csv)


def count_lines(file_csv: str) -> int:
    df = load_dataframe(file_csv)
    return len(df)


def file_csv_to_json(file_csv):
    df = load_dataframe(file_csv)
    frame = df.iloc[:]
    return _frame_to_json(frame)


def json_to_file_csv(file_csv, data_json):
    df = pd.DataFrame.from_dict(data_json)
    df.to_csv(file_csv, index=False)


def split_data_frame_by_value(file_csv, column, value):
    df = load_dataframe(file_csv)
    low_values = df[df[column] < value]
    high_values = df[df[column] >= value]
    return low_values, high_values


def normalize_column_value(file_csv, column, value):
    df = load_dataframe(file_csv)
    df[column][df[column] >= value] = value
    df.to_csv(file_csv, index=False)


def normalize_column_date(df: pd.DataFrame, date_column_index) -> pd.DataFrame:
    df[date_column_index] = pd.to_datetime(df[date_column_index], errors='coerce')
    return df


def sum_group_dataframe_by_date(df: pd.DataFrame, date_column_index, freq='60Min') -> pd.DataFrame:
    return df.groupby(pd.Grouper(key=date_column_index, freq=freq)).sum().reset_index()


def mean_group_dataframe_by_date(df: pd.DataFrame, date_column_index, freq='60Min') -> pd.DataFrame:
    return df.groupby(pd.Grouper(key=date_column_index, freq=freq)).mean(numeric_only=True).reset_index()


def dataframe_to_json(df: pd.DataFrame) -> list[dict]:
    try:
        return json.loads(df.to_json(orient="records"))
    except Exception as e:
        print(str(e))
        return []


def format_time_zone(frame: pd.Series) -> pd.Series:
    _frame = frame.map(lambda x: x.tz_convert(date_utils.LOCAL_TIME_ZONE)).dt.strftime(date_utils.DATE_FORMAT_UTC)
    _frame = _frame.map(lambda x: str(x).replace('"', ""))
    return _frame
