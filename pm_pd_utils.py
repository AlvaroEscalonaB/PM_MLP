import pm4py
import pandas as pd
from typing import List, Dict
from pm4py.visualization.dfg import visualizer as dfg_visualization
from pm4py.algo.discovery.dfg import algorithm as dfg_discovery
from collections import Counter
from typing import Tuple
from pm4py.objects.log.obj import EventLog, Trace

class PandasError(Exception):
  def __init__(self, message):
    print(f'Pandas Error |> {message}')
    super().__init__(message)

class ArgumentError(Exception):
  def __init__(self, message):
    print(f'Argument Error |> {message}')
    super().__init__(message)

class ValidationError(Exception):
  def __init__(self, message):
    print(f'Validation Error |> {message}')
    super().__init__(message)

def trimmed_mean(df: pd.DataFrame, col: str, trim_value: float = 0.05, only_upper: bool = True) -> pd.DataFrame:
  if col not in df.columns:
    raise PandasError(f'The column "{col}" is not in the dataframe columns')
  if trim_value >= 0.5:
    raise ArgumentError(f'The arg trim_value cannot be greater than 0.5')
  low_quantile = 0 if only_upper else trim_value
  return df[(df[col] > df[col].quantile(low_quantile)) & (df[col] < df[col].quantile(1 - trim_value))]

def analyze_column(df: pd.DataFrame, column_name: str) -> pd.Series | None:
  if column_name not in df.columns:
    print(f"'{column_name}' is not in the Dataframe")
    return None
  return df.groupby(column_name)[column_name].count().sort_values(ascending=False)

def filter_df_log_by_attribute(df_event_log: pd.DataFrame, col_attribute: str, col_value: str, negative: bool = False) -> pd.DataFrame:
  if col_attribute not in df_event_log.columns:
    raise ValidationError(f'"{col_attribute}" is not in the dataframe columns {df_event_log.columns}')

  unique_values = df_event_log[col_attribute].unique()
  if col_value not in unique_values:
    raise ValidationError(f'"{col_value}" is not in the values of the column of {col_attribute}, values can be: {", ".join(unique_values.tolist())}')

  if negative:
    return df_event_log[df_event_log[col_attribute] != col_value]

  return df_event_log[df_event_log[col_attribute] == col_value]

def filter_activities(df: pd.DataFrame, activities: List[str], remove: bool = False) -> pd.DataFrame:
  all_activities = df['activity'].unique().tolist()
  if len(set(activities) - set(all_activities)) > 0:
    raise ValidationError(f'There are activities to filter that does not appears in the dataframe {", ".join(list(set(activities) - set(all_activities)))}')

  if remove:
    return df[~df['activity'].isin(activities)]

  return df[df['activity'].isin(activities)]

def process_event_log(event_log: EventLog) -> Tuple[Counter, Counter]:
  performance_dfg, start_activities, end_activities = pm4py.discover_performance_dfg(event_log)
  pm4py.view_performance_dfg(performance_dfg, start_activities, end_activities)

  # See the time taken between activities
  dfg_frequency = dfg_discovery.apply(event_log)
  gviz = dfg_visualization.apply(dfg_frequency, log=event_log, variant=dfg_visualization.Variants.FREQUENCY)
  dfg_visualization.view(gviz)
  return (performance_dfg, dfg_frequency)

def initial_dataframe_analysis(df: pd.DataFrame, with_dfg: bool = False) -> Tuple[EventLog, Counter | None, Counter | None]:
  df_formed = pm4py.format_dataframe(df, case_id='case_id', activity_key='activity', timestamp_key='timestamp')
  event_log = pm4py.convert_to_event_log(df_formed)
  # See the traces repetitions
  performance_dfg, dfg_frequency = None, None
  if with_dfg:
    performance_dfg, dfg_frequency = process_event_log(event_log)

  return (event_log, performance_dfg, dfg_frequency)

def check_variant_frequency(variants: Dict[Tuple[str], List[Trace]]) -> pd.DataFrame:
  variants_items = variants.items()
  variants_items_frequency = [[', '.join(variant_str), len(trace)] for variant_str, trace in variants_items]
  df_traces = pd.DataFrame(variants_items_frequency, columns=['variant', 'frequency']).sort_values(by='frequency', ascending=False)
  df_traces['total_percent'] = (df_traces['frequency'] / df_traces['frequency'].sum() * 100).round(4)
  return df_traces