import pandas as pd
import builtins

class AttributeValidation(Exception):
  def __init__(self, message):
    super().__init__(message)


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
