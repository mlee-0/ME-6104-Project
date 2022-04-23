# Curve and Surface Visualizer
A GUI program for viewing and modifying curves and surfaces in 3D, written in Python.

<img src="Images/screenshot_1.png">

## Features
- Visualize Bézier, Hermite, and B-spline curves and surfaces
- Modify a control point by clicking and dragging it, or by typing values
- Specify the number of control points, number of nodes, and the order
- Select multiple geometries of the same type to view their continuity

## Dependencies
- NumPy (calculations of geometry)
- PyQt5 (graphical user interface)
- VTK 9 (visualization of 3D geometry)

## Running
This program can be run either by downloading the executable file or by downloading and running the source code.

### Executable file
Download the appropriate executable file [here]().

To create the executable file, download all source code, and download PyInstaller using: `pip install pyinstaller`. Then create the executable file using the `.spec` file for the desired operating system: `pyinstaller <filename>.spec`.

### Running from source
Download the source code and install all dependencies using: `pip install -r requirements.txt`. Run `main.py` to start the program.