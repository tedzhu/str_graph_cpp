# Str Graph Cpp: Graph Based String Operation Library

## Setup

To prepare the environment and build the extension module for running the library:
```
python -m venv myenv
source myenv/bin/activate
pip install -r requirements.txt
python setup.py build_ext --inplace
```

Documentation is generated by gathering the docstrings using pdoc: `pdoc str_graph_cpp.py -d google -o docs`

## Running Example and Tests

To run the example code: `python example.py`

To run tests: `python test.py`

## API Usage

Please see `example.py` for simple usage.

Please see the documentation page [docs/str_graph_cpp.html](https://htmlpreview.github.io/?https://github.com/tedzhu/str_graph_cpp/blob/master/docs/str_graph_cpp.html) for comprehensive API reference.

## Project Notes

For the purpose of this exercise we made the following decisions to align with the nature of this project:
- Favor modern language features over backwards compatibility (requiring Python 3.9 or later for graphlib).
- Perform strong type checks during setup function calls.
- Provide a set of minimalist, method based API for users (as shown in the documentation page).
- We assume the amount of calculation within the operations ("the heavy lifting") is significantly higher than 
  the amount of calling the operations. Based on this we implement a lot of dynamic features on the Python side 
  to make the usage as convenient as possible, similar to PyTorch or Airflow. If this ever becomes the
  bottleneck the dispatching can be done on the C++ side as well.