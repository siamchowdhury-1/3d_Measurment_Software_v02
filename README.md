# 3D Measurement Software v02

Software for calculating the measurements of 3D objects, written in pure Python (NumPy + Matplotlib). Build objects from primitive shapes, extrusions and revolved profiles, move and rotate them, and measure length, width, height, radius, diameter, wall thickness, position and volume in the unit you choose.

Developed at **Arkansas State University**, AR.

| Role | Name |
|---|---|
| Lead | Siam Chowdhury |
| Co-author | Bishal Banik |
| Mentor | Dr. Asif Hoda |

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

Any change you push to the `.py` file (new shapes, fixed formulas) shows up in the web version automatically. No build step needed.

> The two files must stay in the **same folder**. If you rename the Python file, also update `PY_FILE` near the top of the `<script>` in `index.html`.

## Publish on GitHub Pages

1. Create a new repository on GitHub and upload all files in this folder (keep them at the top level).
2. In the repo, go to **Settings → Pages**.
3. Under **Build and deployment**, set **Source** to *Deploy from a branch*, choose **main** and **/ (root)**, then **Save**.
4. Wait a minute or two. Your link appears at the top of the Pages settings:
   `https://siamchowdhury-1.github.io/3d_Measurment_Software_v02/`
5. Paste that link into the "Try it online" section of this README.

Or with git:

```bash
git init
git add .
git commit -m "3D Measurement Software v02: desktop + web version"
git branch -M main
git remote add origin https://github.com/siamchowdhury-1/3d_Measurment_Software_v02.git
git push -u origin main
```

## Run on the desktop

```bash
pip install -r requirements.txt
python 3d_Measurment_Software_v02.py
```

On Linux you may also need Tkinter: `sudo apt install python3-tk`

## Test the web version locally

Opening `index.html` by double-clicking won't work, because browsers block pages opened from disk from loading other files. Start a tiny local server instead:

```bash
python -m http.server 8000
```

Then open **http://localhost:8000**.

## Known limitations

- **OBJ/STL export** currently writes a small placeholder point/triangle at each object's position, not the full mesh.
- **Boolean shapes** are saved to JSON but skipped when the file is opened again.
- **Boolean volumes** are approximations: union adds both volumes, cut subtracts, intersect takes the smaller one.
- In the browser, every view change is redrawn by Matplotlib, so orbiting is a little less smooth than on the desktop.

## Project structure

```
├── 3d_Measurment_Software_v02.py   # the app (desktop GUI + all 3D and measurement logic)
├── index.html                      # web front-end that runs the .py in the browser
├── requirements.txt                # desktop dependencies
├── .nojekyll                       # tells GitHub Pages to serve files as-is
└── README.md
```
