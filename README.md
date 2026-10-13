# 3D Measurement Software v02

Software for calculating the measurements of 3D objects, written in pure Python (NumPy + Matplotlib). Build objects from primitive shapes, extrusions and revolved profiles, move and rotate them, and measure length, width, height, radius, diameter, wall thickness, position and volume in the unit you choose.
**Developers**
| Role | Name |
|---|---|
| Lead | Siam Chowdhury |
| Co-author | Bishal Banik |
| Mentor | Dr. Asif Hoda |
| Institution | Arkansas State University, AR, USA |

It runs two ways from the same Python file:

| | How | What you need |
|---|---|---|
| 🌐 **In the browser** | Open the GitHub Pages link | Nothing — just a modern browser |
| 🖥️ **On the desktop** | `python 3d_Measurment_Software_v02.py` | Python 3.8+, NumPy, Matplotlib, Tkinter |

## ▶ Try it online

**[https://siamchowdhury-1.github.io/3d_Measurment_Software_v02/](https://siamchowdhury-1.github.io/3d_Measurment_Software_v02/)**

The first visit downloads about 15 MB (the Python runtime plus NumPy and Matplotlib). After that the browser caches it and startup is much faster.

## Features

- **Shapes:** Box, Sphere, Cylinder, Cone, Torus, Tube, Wedge, Extrusion (custom 2D profile), Revolution (profile revolved around Z)
- **Booleans:** Union, Cut A−B, Intersect (visual approximation; no CAD kernel)
- **Properties:** edit dimensions, profiles, position, Z rotation, color and label
- **Move / Rotate:** type an exact position and angle, or nudge by ±0.1 and rotate by ±15°
- **Measure:** Length, Width, Depth, Height, Radius, Diameter, Inner/Outer Radius and Diameter, Wall Thickness, Position X/Y/Z and Volume
- **Units:** mm, cm, m, in, ft, yd, µm (model sizes are treated as metres and converted)
- **All dimensions:** a full size report for the selected object
- **Scene volumes:** per-object volume and total scene volume
- **Views:** Isometric, Front, Top, Right; drag to orbit, scroll to zoom
- **Files:** save/open scenes as JSON, export OBJ/STL, save a PNG screenshot

## How the web version works

`index.html` uses [Pyodide](https://pyodide.org), which is Python compiled to WebAssembly, to run **the same `3d_Measurment_Software_v02.py` file** inside the browser:

1. It loads Python, NumPy and Matplotlib in the page.
2. It fetches `3d_Measurment_Software_v02.py` from the same folder.
3. Browsers can't open Tkinter windows, so it replaces Tkinter with harmless stand-ins and loads your file unchanged.
4. It uses the file's own `Scene`, shape classes, `volume()` math, measurement and move/rotate methods, `render()`, JSON save/load and OBJ/STL export. Matplotlib draws the 3D view to an image, and the page shows it with an HTML interface.

## Known limitations

- **OBJ/STL export** currently writes a small placeholder point/triangle at each object's position, not the full mesh.
- **Boolean shapes** are saved to JSON but skipped when the file is opened again