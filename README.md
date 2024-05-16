# Considerations

- To run the plots of graphviz you should add computer/system packages

`sudo apt install python3-pydot graphviz`

Otherwise you would't run the functions `initial_dataframe_analysis` and `process_event_log` and the plot functions of

### Handling virtual env

- Create the virtualenv or venv

`python -m venv <NAME OF YOUR VIRTUAL ENV>`

- Activate the virtual env (if you are with this activated, then the shell should have a prefix with the name of the venv name)

`source <NAME OF YOUR VIRTUAL ENV>/bin/activate`

- Deactivate the venv

`deactivate`

### Working in colab

- To import python files from `ipynb` in colab first you have to import the path:

```python
import sys
sys.path.append('/content/drive/MyDrive') # must be the path where the .py file is
```

### Other utilities

`pm4py` has some old dependencies and raise some warnings, to supress all:

```python
import warnings
warnings.filterwarnings("ignore")
```

If you add another dependency after that please run

`pip freeze -l > requirements.txt`

this is for track the new package added
