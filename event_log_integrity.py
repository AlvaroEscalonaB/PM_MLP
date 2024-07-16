import pandas as pd
from custom_errors import validate_necessary_pandas_columns

def overlap_metric(df_log: pd.DataFrame) -> pd.DataFrame:
  """
    Calculate the metric that an event start before the previous is finished
  """
  df_copy = df_log.copy().\
                   reset_index().\
                   rename(columns={'index': 'id'})
  min_columns = ['id', 'activity', 'timestamp', 'timestamp_end']
  validate_necessary_pandas_columns(df_copy, min_columns)
  df_case_lagged = df_copy[min_columns].shift(-1).dropna()
  df_case_lagged['id'] = df_copy['id'].astype(int)
  renamed_columns = {'activity': 'future_activity', 'timestamp': 'future_timestamp', 'timestamp_end': 'future_timestamp_end'}
  df_case_lagged = df_case_lagged.rename(columns=renamed_columns)
  df_join = pd.merge(df_copy, df_case_lagged, on='id').dropna(subset=['future_timestamp', 'future_timestamp_end'])
  case_total_events = df_copy.shape[0]
  df_overlapping_events = df_join[(df_join['timestamp_end'] > df_join['future_timestamp']) & (df_join['timestamp_end'] < df_join['future_timestamp_end'])][['activity', 'future_activity']]
  overlap_metric_value = df_overlapping_events.shape[0] / case_total_events
  print(f'Overlap Metric: {overlap_metric_value:.2%}')

  return df_overlapping_events

def events_contained_metric(df_log: pd.DataFrame) -> pd.DataFrame:
  """
    Calculate the metric that an event start and finish inside the window time of previous activity
  """
  df_copy = df_log.copy().\
                   reset_index().\
                   rename(columns={'index': 'id'})
  min_cols = ['id', 'activity', 'timestamp', 'timestamp_end']
  validate_necessary_pandas_columns(df_copy, min_cols)
  df_case_lagged = df_copy[min_cols].shift(-1).dropna()
  df_case_lagged['id'] = df_copy['id'].astype(int)
  renamed_columns = {'activity': 'future_activity', 'timestamp': 'future_timestamp', 'timestamp_end': 'future_timestamp_end'}
  df_case_lagged = df_case_lagged.rename(columns=renamed_columns)
  df_join = pd.merge(df_copy, df_case_lagged, on='id').dropna(subset=['timestamp', 'timestamp_end', 'future_timestamp'])
  df_contained_events = df_join[(df_join['timestamp'] < df_join['future_timestamp']) &\
                                (df_join['timestamp_end'] > df_join['future_timestamp_end'])
                               ]
  contained_events = df_contained_events.shape[0]
  events_contained_metric_value = contained_events / df_join.shape[0]
  print(f'Entirely contained events: {events_contained_metric_value:.2%}')

  return df_contained_events
