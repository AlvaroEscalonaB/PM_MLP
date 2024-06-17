import builtins
import pandas as pd
import numpy as np

def format_dfg_to_dataframe(dfg: dict[tuple[str, str], dict[str, int]]) -> pd.DataFrame:
  """
    From mpdfg package dfg generate 
    The specific interface of this dfg is:
    {'activities': Counter[str, itn], 'connections': Counter[tuple[str, str], dict[frequency, time]] }
  """
  connection_data = [{'origin': transition[0], 'destination': transition[1], **data} for transition, data in dfg['connections'].items()]
  return pd.DataFrame(connection_data)


def handle_negatives_times(df_connections: pd.DataFrame) -> pd.DataFrame:
  """
    Swaps the connections that have a negative time difference
  """
  validate_necessary_pandas_columns(df_connections, ['origin', 'destination', 'frequency', 'time'])

  df_filter_connections_positive = df_connections[df_connections['time'] >= 0]
  df_filter_connections_negative = df_connections[df_connections['time'] < 0]
  df_filter_connections_negative.columns = ['destination', 'origin', 'frequency', 'time']
  df_filter_connections_negative.loc[:,'time'] = df_filter_connections_negative['time'].abs()
  df_sorted = pd.concat([df_filter_connections_negative, df_filter_connections_positive])
  df_sorted['total_time'] = df_sorted['frequency'] * df_sorted['time']
  total_rows_before = df_sorted.shape[0]
  df_resumed = df_sorted.groupby(['origin', 'destination']).agg({'frequency': 'sum', 'total_time': 'sum'})
  df_resumed['time'] = df_resumed['total_time'] / df_resumed['frequency']
  df_resumed = df_resumed.drop(columns=['total_time'])
  print(f'Total rows {df_resumed.shape[0]}. Filtered a total of {total_rows_before - df_resumed.shape[0]} rows')
  return df_sorted


def filter_by_percentile_frequency(df_log: pd.DataFrame, percentile: float = 0.9) -> pd.DataFrame:
  """
    Filter the dataframe with cols ['origin', 'destination', 'frequency', 'time'] according 
    to a percentile
  """
  return df_log[df_log['frequency'] > df_log['frequency'].quantile(percentile)]


def filter_by_minimum_count_frequency(df_log: pd.DataFrame, min_count_activities: int = 10) -> pd.DataFrame:
  """
    Filter the dataframe with cols ['origin', 'destination', 'frequency', 'time'] according 
    to a min threshold frequency
  """
  return df_log[df_log['frequency'] > min_count_activities]


def generate_filtered_dfg_dict(df: pd.DataFrame) -> dict:
  """
    Transform pandas DataFrame into a dict with the following interface
    dict[Tuple[str, str], dict[str, int]]
  """
  records = df.to_dict('records')
  return { (record['origin'], record['destination']): {'frequency': record['frequency'], 'time': record['time']} for record in records }


def squeeze_consecutive_activities(df_log: pd.DataFrame) -> pd.DataFrame:
  """
    Gather the consecutive activities into one keeping the information of the first record
  """
  validate_necessary_pandas_columns(df_log, ['case_id', 'activity', 'timestamp', 'timestamp_end'])
  df_log['dummy_group'] = (df_log['activity'] != df_log['activity'].shift()).cumsum()

  df_squeezed = df_log.groupby('dummy_group').agg({
      'case_id':       'first',
      'activity':      'first',
      'timestamp':     'min',
      'timestamp_end': 'max'
  }).reset_index(drop=True)

  # TODO: Also keep the record of the other columns
  return df_squeezed.drop(columns=['dummy_group'])


def remove_not_connected_activities(dfg: dict) -> pd.DataFrame:
  dfg_copy = dfg.copy()
  connections = np.ndarray([*dfg['connections'].keys()]).flat()
  dfg_copy['activities'] = { key: value for key, value in dfg['activities'].items() if key in connections }
  return dfg


def filter_start_and_end_activities(dfg, start_activities, end_activities) -> tuple[dict, dict]:
  """
    Filter the start and end activities dict variables according to dfg connections
  """
  unique_activities = pd.Series(sum([list(i) for i in dfg['connections'].keys()], [])).unique()
  return ({ key: value for key, value in start_activities.items() if key in unique_activities },
          { key: value for key, value in end_activities.items() if key in unique_activities })

# Validations

def validate_necessary_pandas_columns(df: pd.DataFrame, columns: list[str] | str):
  """
    Raise an AttributeValidation error if the column(s) are not in the pandas DataFrame
  """
  match type(columns):
    case builtins.str:
      if not columns in df.columns:
        AttributeValidation(f'"{columns}" is not in {df.columns.tolist()}')
    case builtins.list:
      columns_difference = set(columns).difference(set(df.columns))
      if not len(columns_difference) == 0:
        AttributeValidation(f'"{columns_difference}" are not in {df.columns.tolist()}')

class AttributeValidation(Exception):
  def __init__(self, message, errors):            
    super().__init__(message)
    self.errors = errors
