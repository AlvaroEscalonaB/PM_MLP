import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from plotly.graph_objects import Figure, Scatter, Bar
from custom_errors import AttributeValidation

def sns_set_style():
  sns.set_theme(style='darkgrid')

def plot_process_time(df: pd.DataFrame, origin_destination: str | None = None, period: str = '15T', type_plot='hist', reference_activity='Assign Carga'):
  #!: Validate that the needed columns are in the df dataframe
  available_periods = ['10T', '15T', '20T', '30T', 'H']
  if not period in available_periods:
    raise Exception('Periods must be one of these values: ', available_periods)
  unique_origin_destination = df['origin_destination'].unique().tolist()

  if origin_destination == None:
    df_copy = df.copy()
  else:
    if not origin_destination in unique_origin_destination:
      raise Exception(f'The "origin_destination" must be between these values: {unique_origin_destination}')
    df_copy = df.copy()[df['origin_destination'] == origin_destination]

  df_copy['timediff'] = df_copy[['case_id', 'timestamp']].groupby('case_id')['timestamp'].diff().dt.total_seconds() / 60
  short_df = df_copy[['case_id', 'activity', 'timestamp', 'timediff']]
  between_activities = ['Assign Carga', 'Empty Descarga']
  df_first_act = short_df[short_df['activity'] == reference_activity].drop(columns=['timediff'])
  df_timediff = short_df.groupby('case_id')['timediff'].sum().reset_index()
  df_merged = df_first_act.merge(df_timediff, on='case_id')
  df_merged['truncated_ts'] = df_merged.drop(columns=['activity'])['timestamp'].dt.floor(period)
  df_merged['format_hour'] = df_merged['truncated_ts'].dt.strftime('%H:%M')
  df_merged['hour_sorted'] = df_merged['truncated_ts'].dt.strftime('%H.%M').astype(float)
  df_merged['hour_sorted'] = df_merged['hour_sorted'].astype(int) + (df_merged['hour_sorted'] % 1) * 10 / 6
  # Obtain unique values for the hour
  unique_ticks = df_merged[['hour_sorted', 'format_hour']].drop_duplicates().sort_values(by='hour_sorted')
  # Start figures
  fig, (ax1, ax2) = plt.subplots(figsize=(15, 11), ncols=1, nrows=2)
  fig.tight_layout(h_pad=5)
  if type_plot == 'hist':
    sns.barplot(data=df_merged, x='hour_sorted', y='timediff', ax=ax1)
  else:
    sns.boxplot(data=df_merged, x='hour_sorted', y='timediff', ax=ax1, fliersize=0)
    ax1.set(ylim=(0, df_merged['timediff'].quantile(0.925) * 1.25))

  ax1.set_title(f'Bar plot with mean in {origin_destination}')
  ax1.set_xticklabels(unique_ticks['format_hour'], rotation=45, fontsize=8)
  ax1.set(xlabel="Hora de día", ylabel="Tiempo de ciclo")
  sns.countplot(data=df_merged, x='hour_sorted', ax=ax2)
  ax2.set_title(f'Frequency of dispatch movements in {origin_destination}')
  ax2.set_xticklabels(unique_ticks['format_hour'], rotation=45, fontsize=8)
  ax2.set(xlabel="Hora del día", ylabel="Frecuencia")


def plot_pareto(df_original: pd.DataFrame, col_discrete: str, col_value: str, title: str = 'Pareto',
                ylabel: str = 'Conteo', ylabel_2: str = 'Porcentaje') -> Figure:
  
  """
    Dataframe that receives should have the categorical column already grouped with the value to analyze, is not necessary
    to pass the cumulated values or the sorted dataframe
  """
  df_cols = df_original.columns

  color_palette = {
    'dark_teal': '#007B92',
    'light_dark_teal': '#2CA1B7',
    'light_teal': '#62CFC9',
    'main_red': '#DC1F33',
    'dark_yellow': '#EFAC1E',
    'grid_color': '#DFDFDF',
  }

  if not col_discrete in df_cols:
    raise AttributeError(f'"{col_discrete}" is not in the dataframe columns: {[*df_cols]}')

  if not col_value in df_cols:
    raise AttributeError(f'"{col_value}" is not in the dataframe columns: {[*df_cols]}')

  df = df_original.copy()
  df = df.sort_values(by=col_value, ascending=False)
  df['cumulated'] = df[col_value].cumsum() / df[col_value].sum() * 100
  df = df.reset_index(drop=True)
  above_eighth = (df['cumulated'] < 80).sum() + 1
  total_sum = df[col_value].sum()

  plot_data = [
    Bar(
      name=ylabel,
      x= df[col_discrete],
      y= df[col_value],
      marker= {'color': list(np.repeat(color_palette['dark_teal'], above_eighth)) +\
                        list(np.repeat(color_palette['light_dark_teal'], max(len(df[col_discrete]) - above_eighth, 0)))
              }
    ),
    Scatter(
      line= {
        'color': color_palette['main_red'], 
        'width': 3
      },
      name=ylabel_2, 
      x=df[col_discrete],
      y=df['cumulated'], 
      yaxis='y2',
      mode='lines+markers'
    ),
  ]
  
  plot_layout = {
    'height': 500,
    # Title Graph
    'title': {
      'text': title,
      'font': dict(size=24)
    },
    'font': {
      'size': 14,
      'color': 'rgb(44, 44, 44)',
    },
          
    'margin': {
      'b': 20,
      'l': 50,
      'r': 50,
      't': 10,
    },
    
    'plot_bgcolor': 'rgb(255, 255, 255)', 

    # Settings Legend
    'legend': {
      'x': 0.79,
      'y': 1.2,
      'font': {
        'size': 12, 
        'color': 'rgb(70, 70, 70)', 
      },
      'orientation': 'h',
    },
    
    # Yaxis 1 position left
    'yaxis': {
      'title': ylabel,
      'range': [0, total_sum * 1.05],
      'titlefont': {
      'size': 16, 
      'color': 'rgb(70, 70, 70)',
      },
    }, 
    
    # Yaxis 2 position right
    'yaxis2': {
      'side': 'right',
      'range': [0, 105], 
      'title': ylabel_2,
      'titlefont': {
        'size': 16, 
        'color': 'rgb(70, 70, 70)', 
      },
      'overlaying': 'y',
      'ticksuffix': ' %',
      'showgrid': True,
      'gridcolor': color_palette['grid_color'],
      'gridwidth': 0.5
    }
  }

  fig = Figure(data=plot_data, layout=plot_layout)
  fig.add_shape(
    type='line',
    x0=0.02,
    x1=0.98,
    y0=80,
    y1=80,
    line=dict(
      color=color_palette['dark_yellow'],
      width=3,
      dash='dash'
    ),
    xref='paper',
    yref='y2'
  )

  return fig


def fill_timeday(df: pd.DataFrame, period: str = '30T') -> pd.DataFrame:
  if 'timestamp' not in df.columns:
    raise AttributeError(f'timestamp is not in dataframe columns #{df.columns.tolist()}')

  possible_periods = ['10T', '15T', '20T', '30T', 'H']
  if period not in possible_periods:
    raise AttributeError(f'#{period} is not in the available possible periods: #{possible_periods}')

  df_copy = df.copy()
  df_copy['truncated_ts'] = df_copy['timestamp'].dt.floor(period)
  df_copy['hour_sorted'] = df_copy['truncated_ts'].dt.strftime('%H.%M').astype(float)
  df_copy['hour_sorted'] = df_copy['hour_sorted'].astype(int) + (df_copy['hour_sorted'] % 1) * 10 / 6
  df_copy = df_copy.groupby(by='hour_sorted')['hour_sorted'].count().rename('count').reset_index()
  df_filled = pd.DataFrame(data={
                                  'num_hour': np.arange(0, 24, 0.5),
                                  'num_format': pd.date_range(start='00:00', end='23:59', freq='30T').strftime('%H:%M')
                                })
  df_filled = df_filled.merge(df_copy, left_on='num_hour', right_on='hour_sorted', how='left').\
                        drop(columns=['hour_sorted']).\
                        fillna(0)
  df_filled['count'] = df_filled['count'].astype(int)
  return df_filled


def plot_timeday(df: pd.DataFrame, title: str = None) -> plt.Figure:
  df_filled = fill_timeday(df)
  fig, ax = plt.subplots(figsize=(12, 5), ncols=1, nrows=1)
  fig.tight_layout(h_pad=5)
  sns.barplot(data=df_filled, x='hour_sorted', y='count', ax=ax)

  if title != None:
    ax.set_title(f'Frecuencia de movimientos de evento "{title}"')
  else:
    ax.set_title(f'Frecuencia de movimientos de eventos')

  ax.set_xticklabels(ax.get_xticklabels(), rotation=45, fontsize=8)
  ax.set(xlabel="Hora del día", ylabel='Frecuencia');

  return fig
