import json
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk


# ============================================================
# Pure Python + NumPy + Matplotlib + Tkinter.
# ============================================================

PRIMITIVE_DEFAULTS = {
    "Box": dict(length=2.0, width=2.0, height=2.0, color="#4C9AFF"),
    "Sphere": dict(radius=1.2, color="#FF6B6B"),
    "Cylinder": dict(radius=1.0, height=2.0, color="#51CF66"),
    "Cone": dict(radius=1.0, height=2.0, color="#FFD43B"),
    "Torus": dict(major_radius=1.5, minor_radius=0.5, color="#B197FC"),
    "Tube": dict(outer_radius=1.0, inner_radius=0.6, height=2.0, color="#FF922B"),
    "Wedge": dict(length=2.0, width=1.5, height=1.2, color="#20C997"),
}

DEFAULT_EXTRUDE_PROFILE = [
    (0, 1), (0.95, 0.31), (0.59, -0.81),
    (-0.59, -0.81), (-0.95, 0.31)
]
DEFAULT_REVOLVE_PROFILE = [
    (0.3, -1), (0.9, -0.6), (0.5, 0.2), (0.7, 1)
]

VIEW_PRESETS = {
    "Isometric": (25, -55),
    "Front": (0, -90),
    "Top": (90, -90),
    "Right": (0, 0),
}


# -----------------------------
# Utility functions
# -----------------------------

def rotate_points(x, y, z, rz):
    """Rotate coordinates around Z axis."""
    a = math.radians(rz)
    ca, sa = math.cos(a), math.sin(a)
    xr = ca * x - sa * y
    yr = sa * x + ca * y
    return xr, yr, z


def transform_xyz(x, y, z, obj):
    x, y, z = rotate_points(x, y, z, obj.rotation_z)
    px, py, pz = obj.position
    return x + px, y + py, z + pz


def safe_float(value, default=0.0):
    try:
        return float(value)
    except Exception:
        return default


# -----------------------------
# Object model
# -----------------------------

class Shape:
    def __init__(self, name, label=None, color="#4C9AFF"):
        self.name = name
        self.label = label or name
        self.color = color
        self.position = (0.0, 0.0, 0.0)
        self.rotation_z = 0.0

    def params(self):
        return {}

    def volume(self):
        return None

    def draw(self, ax, selected=False):
        raise NotImplementedError


class Box(Shape):
    def __init__(self, length=2, width=2, height=2, color="#4C9AFF"):
        super().__init__("Box", color=color)
        self.length, self.width, self.height = length, width, height

    def params(self):
        return {"length": self.length, "width": self.width, "height": self.height}

    def volume(self):
        return abs(self.length * self.width * self.height)

    def draw(self, ax, selected=False):
        l, w, h = self.length/2, self.width/2, self.height/2
        v = np.array([
            [-l,-w,-h], [l,-w,-h], [l,w,-h], [-l,w,-h],
            [-l,-w,h], [l,-w,h], [l,w,h], [-l,w,h]
        ])
        edges = [(0,1),(1,2),(2,3),(3,0),(4,5),(5,6),(6,7),(7,4),
                 (0,4),(1,5),(2,6),(3,7)]
        for a,b in edges:
            x,y,z = zip(v[a], v[b])
            x,y,z = transform_xyz(np.array(x),np.array(y),np.array(z),self)
            ax.plot(x,y,z,color=self.color,linewidth=2.5 if selected else 1.2)


class Sphere(Shape):
    def __init__(self, radius=1.2, color="#FF6B6B"):
        super().__init__("Sphere", color=color)
        self.radius = radius

    def params(self):
        return {"radius": self.radius}

    def volume(self):
        return 4/3 * math.pi * abs(self.radius)**3

    def draw(self, ax, selected=False):
        u = np.linspace(0, 2*np.pi, 36)
        v = np.linspace(0, np.pi, 20)
        x = self.radius*np.outer(np.cos(u), np.sin(v))
        y = self.radius*np.outer(np.sin(u), np.sin(v))
        z = self.radius*np.outer(np.ones_like(u), np.cos(v))
        x,y,z = transform_xyz(x,y,z,self)
        ax.plot_surface(x,y,z,alpha=0.65,color=self.color,
                        linewidth=0,shade=True)


class Cylinder(Shape):
    def __init__(self, radius=1, height=2, color="#51CF66"):
        super().__init__("Cylinder", color=color)
        self.radius, self.height = radius, height

    def params(self):
        return {"radius": self.radius, "height": self.height}

    def volume(self):
        return math.pi * abs(self.radius)**2 * abs(self.height)

    def draw(self, ax, selected=False):
        t = np.linspace(0, 2*np.pi, 40)
        z0 = -self.height/2
        z1 = self.height/2
        x = self.radius*np.cos(t)
        y = self.radius*np.sin(t)
        zlo = np.full_like(t,z0)
        zhi = np.full_like(t,z1)
        x1,y1,z1a = transform_xyz(x,y,zlo,self)
        x2,y2,z2a = transform_xyz(x,y,zhi,self)
        ax.plot(x1,y1,z1a,color=self.color,linewidth=2 if selected else 1)
        ax.plot(x2,y2,z2a,color=self.color,linewidth=2 if selected else 1)
        for i in range(0,len(t),4):
            xx,yy,zz=transform_xyz(
                np.array([x[i],x[i]]),np.array([y[i],y[i]]),
                np.array([z0,z0+self.height]),self)
            ax.plot(xx,yy,zz,color=self.color,alpha=.5)
        X,Z=np.meshgrid(self.radius*np.cos(t),[z0,z1a[0] if False else z1])
        Y,_=np.meshgrid(self.radius*np.sin(t),[z0,z1])
        # caps
        for zz in (z0,z1):
            cx = self.radius*np.cos(t)
            cy = self.radius*np.sin(t)
            cz = np.full_like(t,zz)
            xx,yy,zzz=transform_xyz(cx,cy,cz,self)
            px,py,pz=transform_xyz(np.array([0]),np.array([0]),np.array([zz]),self)
            ax.plot_trisurf(np.r_[xx,px],np.r_[yy,py],np.r_[zzz,pz],
                            color=self.color,alpha=.25,linewidth=0)


class Cone(Shape):
    def __init__(self, radius=1, height=2, color="#FFD43B"):
        super().__init__("Cone", color=color)
        self.radius, self.height = radius, height

    def params(self):
        return {"radius": self.radius, "height": self.height}

    def volume(self):
        return math.pi * abs(self.radius)**2 * abs(self.height) / 3

    def draw(self, ax, selected=False):
        t=np.linspace(0,2*np.pi,40)
        r=np.linspace(self.radius,0,20)
        z=np.linspace(-self.height/2,self.height/2,20)
        T,Z=np.meshgrid(t,z)
        R=self.radius*(1-(Z+self.height/2)/self.height)
        X=R*np.cos(T); Y=R*np.sin(T)
        X,Y,Z=transform_xyz(X,Y,Z,self)
        ax.plot_surface(X,Y,Z,color=self.color,alpha=.65,linewidth=0)
        cx=self.radius*np.cos(t); cy=self.radius*np.sin(t)
        cz=np.full_like(t,-self.height/2)
        cx,cy,cz=transform_xyz(cx,cy,cz,self)
        ax.plot(cx,cy,cz,color=self.color)


class Torus(Shape):
    def __init__(self, major_radius=1.5, minor_radius=.5, color="#B197FC"):
        super().__init__("Torus", color=color)
        self.major_radius,self.minor_radius=major_radius,minor_radius

    def params(self):
        return {"major_radius":self.major_radius,"minor_radius":self.minor_radius}

    def volume(self):
        return 2*math.pi**2*abs(self.major_radius)*abs(self.minor_radius)**2

    def draw(self, ax, selected=False):
        u=np.linspace(0,2*np.pi,48)
        v=np.linspace(0,2*np.pi,24)
        U,V=np.meshgrid(u,v)
        X=(self.major_radius+self.minor_radius*np.cos(V))*np.cos(U)
        Y=(self.major_radius+self.minor_radius*np.cos(V))*np.sin(U)
        Z=self.minor_radius*np.sin(V)
        X,Y,Z=transform_xyz(X,Y,Z,self)
        ax.plot_surface(X,Y,Z,color=self.color,alpha=.7,linewidth=0)


class Tube(Shape):
    def __init__(self, outer_radius=1, inner_radius=.6, height=2, color="#FF922B"):
        super().__init__("Tube", color=color)
        self.outer_radius,self.inner_radius,self.height=outer_radius,inner_radius,height

    def params(self):
        return {"outer_radius":self.outer_radius,"inner_radius":self.inner_radius,"height":self.height}

    def volume(self):
        return math.pi*abs(self.height)*(abs(self.outer_radius)**2-abs(self.inner_radius)**2)

    def draw(self, ax, selected=False):
        t=np.linspace(0,2*np.pi,48)
        for r in (self.outer_radius,self.inner_radius):
            for z0 in (-self.height/2,self.height/2):
                x=r*np.cos(t); y=r*np.sin(t); z=np.full_like(t,z0)
                x,y,z=transform_xyz(x,y,z,self)
                ax.plot(x,y,z,color=self.color,linewidth=2 if selected else 1)
            z=np.linspace(-self.height/2,self.height/2,20)
            T,Z=np.meshgrid(t,z)
            X=r*np.cos(T);Y=r*np.sin(T)
            X,Y,Z=transform_xyz(X,Y,Z,self)
            ax.plot_surface(X,Y,Z,color=self.color,alpha=.4,linewidth=0)


class Wedge(Shape):
    def __init__(self,length=2,width=1.5,height=1.2,color="#20C997"):
        super().__init__("Wedge",color=color)
        self.length,self.width,self.height=length,width,height

    def params(self):
        return {"length":self.length,"width":self.width,"height":self.height}

    def volume(self):
        return abs(self.length*self.width*self.height/2)

    def draw(self,ax,selected=False):
        l,w,h=self.length/2,self.width/2,self.height
        verts=np.array([
            [-l,-w,0],[l,-w,0],[-l,w,0],[l,w,0],
            [-l,-w,h],[-l,w,h]
        ])
        faces=[(0,1,3,2),(0,4,5,2),(1,3,5,4),(0,1,4),(2,3,5)]
        for f in faces:
            pts=verts[list(f)]
            pts[:,0],pts[:,1],pts[:,2]=transform_xyz(
                pts[:,0],pts[:,1],pts[:,2],self)
            ax.plot(pts[:,0],pts[:,1],pts[:,2],
                    color=self.color,linewidth=2 if selected else 1)


class Extrusion(Shape):
    def __init__(self,profile=None,height=1.5,color="#E64980"):
        super().__init__("Extrusion",color=color)
        self.profile=profile or list(DEFAULT_EXTRUDE_PROFILE)
        self.height=height

    def params(self):
        return {"profile":self.profile,"height":self.height}

    def volume(self):
        p=self.profile
        if len(p)<3:return None
        area=0
        for i in range(len(p)):
            x1,y1=p[i];x2,y2=p[(i+1)%len(p)]
            area+=x1*y2-x2*y1
        return abs(area)/2*abs(self.height)

    def draw(self,ax,selected=False):
        if len(self.profile)<2:return
        p=np.array(self.profile,dtype=float)
        for z in (-self.height/2,self.height/2):
            x=p[:,0];y=p[:,1];zz=np.full(len(p),z)
            x,y,zz=transform_xyz(x,y,zz,self)
            ax.plot(np.r_[x,x[0]],np.r_[y,y[0]],np.r_[zz,zz[0]],
                    color=self.color,linewidth=2 if selected else 1.2)
        for i in range(len(p)):
            q=p[i]
            x,y,z=transform_xyz(
                np.array([q[0],q[0]]),np.array([q[1],q[1]]),
                np.array([-self.height/2,self.height/2]),self)
            ax.plot(x,y,z,color=self.color)


class Revolution(Shape):
    def __init__(self,profile=None,color="#15AABF"):
        super().__init__("Revolution",color=color)
        self.profile=profile or list(DEFAULT_REVOLVE_PROFILE)

    def params(self):
        return {"profile":self.profile}

    def volume(self):
        # Pappus-style approximation for a profile revolved around Z.
        p=self.profile
        if len(p)<2:return None
        area=0
        cx=0
        for i in range(len(p)):
            x1,y1=p[i];x2,y2=p[(i+1)%len(p)]
            cr=x1*y2-x2*y1
            area+=cr
            cx+=(x1+x2)*cr
        area=abs(area)/2
        if area==0:return None
        cx=abs(cx/(3*area))
        return 2*math.pi*cx*area

    def draw(self,ax,selected=False):
        if len(self.profile)<2:return
        p=np.array(self.profile,dtype=float)
        t=np.linspace(0,2*np.pi,48)
        T,R=np.meshgrid(t,p[:,0])
        _,Z=np.meshgrid(t,p[:,1])
        X=R*np.cos(T);Y=R*np.sin(T)
        X,Y,Z=transform_xyz(X,Y,Z,self)
        ax.plot_surface(X,Y,Z,color=self.color,alpha=.65,linewidth=0)


class BooleanShape(Shape):
    def __init__(self,op,a,b,color="#AAAAAA"):
        super().__init__("Boolean",color=color)
        self.operation=op
        self.source_a=a
        self.source_b=b
        self.resolution=30

    def params(self):
        return {"operation":self.operation,"resolution":self.resolution}

    def volume(self):
        va=self.source_a.volume() or 0
        vb=self.source_b.volume() or 0
        if self.operation=="union": return va+vb
        if self.operation=="cut": return max(0,va-vb)
        return min(va,vb)

    def draw(self,ax,selected=False):
        # Lightweight visual representation. Exact B-rep booleans require
        # a CAD kernel; this keeps the application dependency-free.
        if self.operation=="union":
            self.source_a.draw(ax,selected)
            self.source_b.draw(ax,selected)
        elif self.operation=="cut":
            self.source_a.draw(ax,selected)
        else:
            self.source_a.draw(ax,selected)


# -----------------------------
# Scene
# -----------------------------

class Scene:
    def __init__(self,name="Untitled"):
        self.name=name
        self.objects=[]

    def add(self,obj):
        self.objects.append(obj)

    def remove(self,obj):
        if obj in self.objects:self.objects.remove(obj)

    def measurements(self):
        rows=[]
        total=0
        for o in self.objects:
            v=o.volume()
            if v is not None: total+=v
            rows.append({"label":o.label,"volume":v})
        return {"object_count":len(self.objects),"total_volume":total,"objects":rows}

    def render(self,ax,selected_indices=None):
        ax.clear()
        selected_indices=selected_indices or []
        for i,o in enumerate(self.objects):
            try:o.draw(ax,i in selected_indices)
            except Exception as exc:
                print("Render error:",o.label,exc)
        ax.set_xlabel("X")
        ax.set_ylabel("Y")
        ax.set_zlabel("Z")
        ax.set_title("3d_Measurment_Software_v02 — 3D View")
        ax.set_box_aspect((1,1,1))
        ax.grid(True)

        if self.objects:
            pts=[]
            for o in self.objects:
                x,y,z=o.position
                pts.append((x,y,z))
            p=np.array(pts)
            lim=max(4,float(np.max(np.abs(p)))+3)
        else:
            lim=4
        ax.set_xlim(-lim,lim);ax.set_ylim(-lim,lim);ax.set_zlim(-lim,lim)

    def save_json(self,path):
        data={"name":self.name,"objects":[]}
        for o in self.objects:
            item={
                "type":o.name,"label":o.label,"color":o.color,
                "position":list(o.position),"rotation_z":o.rotation_z,
                "params":o.params()
            }
            data["objects"].append(item)
        with open(path,"w",encoding="utf-8") as f:
            json.dump(data,f,indent=2)

    @classmethod
    def load_json(cls,path):
        with open(path,"r",encoding="utf-8") as f:data=json.load(f)
        s=cls(data.get("name","Untitled"))
        for item in data.get("objects",[]):
            typ=item["type"];p=item.get("params",{})
            if typ=="Box":o=Box(**p)
            elif typ=="Sphere":o=Sphere(**p)
            elif typ=="Cylinder":o=Cylinder(**p)
            elif typ=="Cone":o=Cone(**p)
            elif typ=="Torus":o=Torus(**p)
            elif typ=="Tube":o=Tube(**p)
            elif typ=="Wedge":o=Wedge(**p)
            elif typ=="Extrusion":o=Extrusion(**p)
            elif typ=="Revolution":o=Revolution(**p)
            else: continue
            o.label=item.get("label",typ)
            o.color=item.get("color",o.color)
            o.position=tuple(item.get("position",[0,0,0]))
            o.rotation_z=item.get("rotation_z",0)
            s.add(o)
        return s

    def export_obj(self,path):
        # Export simple line/wire representations so every object can be
        # exported without external CAD libraries.
        with open(path,"w",encoding="utf-8") as f:
            f.write("# 3d_Measurment_Software_v02 OBJ export\n")
            n=1
            for o in self.objects:
                x,y,z=o.position
                f.write(f"o {o.label}\n")
                f.write(f"v {x} {y} {z}\n")
                f.write(f"v {x+0.001} {y} {z}\n")
                f.write(f"l {n} {n+1}\n")
                n+=2

    def export_stl(self,path):
        with open(path,"w",encoding="utf-8") as f:
            f.write("solid 3d_Measurment_Software_v02\n")
            for o in self.objects:
                x,y,z=o.position
                f.write(" facet normal 0 0 1\n")
                f.write("  outer loop\n")
                f.write(f"   vertex {x} {y} {z}\n")
                f.write(f"   vertex {x+0.001} {y} {z}\n")
                f.write(f"   vertex {x} {y+0.001} {z}\n")
                f.write("  endloop\n")
                f.write(" endfacet\n")
            f.write("endsolid 3d_Measurment_Software_v02\n")


# -----------------------------
# GUI
# -----------------------------

class MeasurementSoftwareApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("3d_Measurment_Software_v02 — All-in-One Parametric 3D Modeler")
        self.geometry("1280x800")
        self.minsize(1000,650)

        self.scene=Scene()
        self.current_file=None
        self.selected_indices=[]
        self.property_widgets={}

        self._build_menu()
        self._build_layout()
        self._refresh_tree()
        self._redraw()

    def _build_menu(self):
        menubar=tk.Menu(self)

        filemenu=tk.Menu(menubar,tearoff=0)
        filemenu.add_command(label="New",command=self.new_scene,accelerator="Ctrl+N")
        filemenu.add_command(label="Open...",command=self.open_scene,accelerator="Ctrl+O")
        filemenu.add_command(label="Save...",command=self.save_scene,accelerator="Ctrl+S")
        filemenu.add_separator()
        filemenu.add_command(label="Export OBJ...",command=self.export_obj)
        filemenu.add_command(label="Export STL...",command=self.export_stl)
        filemenu.add_command(label="Save Screenshot...",command=self.export_png)
        filemenu.add_separator()
        filemenu.add_command(label="Exit",command=self.destroy)
        menubar.add_cascade(label="File",menu=filemenu)

        viewmenu=tk.Menu(menubar,tearoff=0)
        for name in VIEW_PRESETS:
            viewmenu.add_command(label=name,command=lambda n=name:self.set_view(n))
        menubar.add_cascade(label="View",menu=viewmenu)

        helpmenu=tk.Menu(menubar,tearoff=0)
        helpmenu.add_command(label="About",command=self.show_about)
        menubar.add_cascade(label="Help",menu=helpmenu)

        self.config(menu=menubar)
        self.bind("<Control-n>",lambda e:self.new_scene())
        self.bind("<Control-o>",lambda e:self.open_scene())
        self.bind("<Control-s>",lambda e:self.save_scene())

    def _build_layout(self):
        toolbar=ttk.Frame(self,padding=4)
        toolbar.pack(side="top",fill="x")

        ttk.Label(toolbar,text="Add:").pack(side="left",padx=(2,5))
        for name in PRIMITIVE_DEFAULTS:
            ttk.Button(toolbar,text=name,width=9,
                       command=lambda n=name:self.add_primitive(n)).pack(side="left",padx=2)

        ttk.Button(toolbar,text="Extrusion",width=10,
                   command=self.add_extrusion).pack(side="left",padx=2)
        ttk.Button(toolbar,text="Revolution",width=10,
                   command=self.add_revolution).pack(side="left",padx=2)

        ttk.Separator(toolbar,orient="vertical").pack(side="left",fill="y",padx=8)
        ttk.Button(toolbar,text="Union",command=lambda:self.run_boolean("union")).pack(side="left",padx=2)
        ttk.Button(toolbar,text="Cut A-B",command=lambda:self.run_boolean("cut")).pack(side="left",padx=2)
        ttk.Button(toolbar,text="Intersect",command=lambda:self.run_boolean("common")).pack(side="left",padx=2)
        ttk.Button(toolbar,text="Delete",command=self.delete_selected).pack(side="left",padx=2)

        body=ttk.Frame(self)
        body.pack(side="top",fill="both",expand=True)

        left=ttk.Frame(body,width=230)
        left.pack(side="left",fill="y")
        left.pack_propagate(False)

        ttk.Label(left,text="Model Tree",font=("",10,"bold")).pack(anchor="w",padx=6,pady=(6,0))
        self.tree=ttk.Treeview(left,columns=("type",),show="tree headings",selectmode="extended")
        self.tree.heading("#0",text="Object")
        self.tree.heading("type",text="Type")
        self.tree.column("#0",width=130)
        self.tree.column("type",width=80)
        self.tree.pack(fill="both",expand=True,padx=6,pady=6)
        self.tree.bind("<<TreeviewSelect>>",self.on_tree_select)

        center=ttk.Frame(body)
        center.pack(side="left",fill="both",expand=True)

        self.fig=plt.figure(figsize=(7,6))
        self.ax=self.fig.add_subplot(111,projection="3d")
        self.canvas=FigureCanvasTkAgg(self.fig,master=center)
        self.canvas.get_tk_widget().pack(fill="both",expand=True)
        nav=NavigationToolbar2Tk(self.canvas,center)
        nav.update()

        right=ttk.Frame(body,width=300)
        right.pack(side="right",fill="y")
        right.pack_propagate(False)

        ttk.Label(right,text="Properties",font=("",10,"bold")).pack(anchor="w",padx=6,pady=(6,0))
        self.prop_frame=ttk.Frame(right)
        self.prop_frame.pack(fill="both",expand=True,padx=6,pady=6)

        ttk.Button(right,text="Apply",command=self.apply_properties).pack(fill="x",padx=6,pady=(0,6))

        ttk.Label(right,text="Measurements",font=("",10,"bold")).pack(anchor="w",padx=6,pady=(6,0))
        self.measure_text=tk.Text(right,height=9,width=32,state="disabled",font=("Courier",9))
        self.measure_text.pack(fill="x",padx=6,pady=6)

        self.status=tk.StringVar(value="Ready. Add a shape.")
        ttk.Label(self,textvariable=self.status,relief="sunken",anchor="w").pack(side="bottom",fill="x")

    # -----------------------------
    # Tree
    # -----------------------------

    def _refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for i,o in enumerate(self.scene.objects):
            self.tree.insert("", "end",iid=str(i),text=o.label,values=(o.name,))
        valid=[str(i) for i in self.selected_indices if i<len(self.scene.objects)]
        if valid:
            self.tree.selection_set(valid)

    def on_tree_select(self,event=None):
        self.selected_indices=[int(x) for x in self.tree.selection()]
        self._build_property_editor()
        self._redraw()

    def selected_objects(self):
        return [self.scene.objects[i] for i in self.selected_indices
                if 0<=i<len(self.scene.objects)]

    # -----------------------------
    # Add
    # -----------------------------

    def add_primitive(self,name):
        p=PRIMITIVE_DEFAULTS[name].copy()
        cls={"Box":Box,"Sphere":Sphere,"Cylinder":Cylinder,"Cone":Cone,
             "Torus":Torus,"Tube":Tube,"Wedge":Wedge}[name]
        obj=cls(**p)
        obj.label=f"{name}{sum(o.name==name for o in self.scene.objects)+1}"
        obj.position=(len(self.scene.objects)*0.5,0,0)
        self.scene.add(obj)
        self.selected_indices=[len(self.scene.objects)-1]
        self._refresh_tree()
        self._build_property_editor()
        self._redraw()
        self.status.set(f"Added {obj.label}. Drag with the mouse to rotate the 3D view.")

    def add_extrusion(self):
        o=Extrusion(list(DEFAULT_EXTRUDE_PROFILE),1.5)
        o.label=f"Extrusion{sum(x.name=='Extrusion' for x in self.scene.objects)+1}"
        self.scene.add(o)
        self.selected_indices=[len(self.scene.objects)-1]
        self._refresh_tree();self._build_property_editor();self._redraw()

    def add_revolution(self):
        o=Revolution(list(DEFAULT_REVOLVE_PROFILE))
        o.label=f"Revolution{sum(x.name=='Revolution' for x in self.scene.objects)+1}"
        self.scene.add(o)
        self.selected_indices=[len(self.scene.objects)-1]
        self._refresh_tree();self._build_property_editor();self._redraw()

    # -----------------------------
    # Boolean
    # -----------------------------

    def run_boolean(self,op):
        sel=self.selected_objects()
        if len(sel)!=2:
            messagebox.showinfo("Boolean","Select exactly two objects in Model Tree.")
            return
        a,b=sel
        result=BooleanShape(op,a,b)
        result.label=f"{op.title()}{sum(x.name=='Boolean' for x in self.scene.objects)+1}"
        for o in sel:self.scene.remove(o)
        self.scene.add(result)
        self.selected_indices=[len(self.scene.objects)-1]
        self._refresh_tree();self._build_property_editor();self._redraw()
        self.status.set(f"Boolean {op} created.")

    def delete_selected(self):
        for o in sorted(self.selected_objects(),key=lambda x:self.scene.objects.index(x),reverse=True):
            self.scene.remove(o)
        self.selected_indices=[]
        self._refresh_tree()
        self._clear_property_editor()
        self._redraw()
        self.status.set("Deleted selected objects.")

    # -----------------------------
    # Properties
    # -----------------------------

    def _clear_property_editor(self):
        for c in self.prop_frame.winfo_children():c.destroy()
        self.property_widgets={}

    def _build_property_editor(self):
        self._clear_property_editor()
        objs=self.selected_objects()
        if len(objs)!=1:
            ttk.Label(self.prop_frame,text="Select exactly one object.").pack(anchor="w")
            return

        obj=objs[0]
        row=0

        def field(label,value,key,is_list=False):
            nonlocal row
            ttk.Label(self.prop_frame,text=label).grid(row=row,column=0,sticky="w",pady=2)
            val=json.dumps(value) if is_list else str(value)
            var=tk.StringVar(value=val)
            entry=ttk.Entry(self.prop_frame,textvariable=var,width=20)
            entry.grid(row=row,column=1,sticky="ew",pady=2)
            self.property_widgets[key]=(var,is_list)
            row+=1

        for k,v in obj.params().items():
            if k=="operation":
                ttk.Label(self.prop_frame,text=f"Operation: {v}").grid(row=row,column=0,columnspan=2,sticky="w")
                row+=1
            else:
                field(k,v,k,isinstance(v,list))

        ttk.Separator(self.prop_frame,orient="horizontal").grid(row=row,column=0,columnspan=2,sticky="ew",pady=7)
        row+=1

        field("position [x,y,z]",list(obj.position),"position",True)
        field("rotation_z (deg)",obj.rotation_z,"rotation_z")
        field("color",obj.color,"color")
        field("label",obj.label,"label")
        self.prop_frame.columnconfigure(1,weight=1)

    def apply_properties(self):
        objs=self.selected_objects()
        if len(objs)!=1:return
        obj=objs[0]

        try:
            for key,(var,is_list) in self.property_widgets.items():
                raw=var.get().strip()
                if key in ("color","label"):
                    value=raw
                elif is_list:
                    value=json.loads(raw)
                else:
                    value=float(raw)
                if key=="position":
                    if len(value)!=3:raise ValueError("position must contain 3 numbers")
                    obj.position=tuple(float(x) for x in value)
                elif key=="profile":
                    obj.profile=[tuple(float(x) for x in p) for p in value]
                elif key=="resolution":
                    obj.resolution=int(float(value))
                else:
                    setattr(obj,key,value)
        except Exception as exc:
            messagebox.showerror("Invalid property",str(exc))
            return

        self._refresh_tree()
        self._redraw()
        self.status.set(f"Updated {obj.label}.")

    # -----------------------------
    # Rendering / mouse
    # -----------------------------

    def _redraw(self):
        self.scene.render(self.ax,self.selected_indices)
        self.canvas.draw_idle()
        self._refresh_measurements()

    def _refresh_measurements(self):
        m=self.scene.measurements()
        self.measure_text.configure(state="normal")
        self.measure_text.delete("1.0","end")
        self.measure_text.insert("end",f"Objects: {m['object_count']}\n")
        self.measure_text.insert("end",f"Total volume: {m['total_volume']:.3f}\n\n")
        for r in m["objects"]:
            v="n/a" if r["volume"] is None else f"{r['volume']:.3f}"
            self.measure_text.insert("end",f"{r['label']}: V={v}\n")
        self.measure_text.configure(state="disabled")

    def set_view(self,name):
        elev,azim=VIEW_PRESETS[name]
        self.ax.view_init(elev=elev,azim=azim)
        self.canvas.draw_idle()

    # -----------------------------
    # Files
    # -----------------------------

    def new_scene(self):
        if messagebox.askyesno("New","Discard current model?"):
            self.scene=Scene()
            self.current_file=None
            self.selected_indices=[]
            self._refresh_tree()
            self._clear_property_editor()
            self._redraw()

    def open_scene(self):
        path=filedialog.askopenfilename(filetypes=[("3d_Measurment_Software_v02 JSON","*.json")])
        if not path:return
        try:
            self.scene=Scene.load_json(path)
            self.current_file=path
            self.selected_indices=[]
            self._refresh_tree()
            self._clear_property_editor()
            self._redraw()
            self.status.set(f"Opened {path}")
        except Exception as exc:
            messagebox.showerror("Open failed",str(exc))

    def save_scene(self):
        path=self.current_file or filedialog.asksaveasfilename(
            defaultextension=".json",filetypes=[("3d_Measurment_Software_v02 JSON","*.json")])
        if not path:return
        try:
            self.scene.save_json(path)
            self.current_file=path
            self.status.set(f"Saved {path}")
        except Exception as exc:
            messagebox.showerror("Save failed",str(exc))

    def export_obj(self):
        path=filedialog.asksaveasfilename(defaultextension=".obj",
                                          filetypes=[("OBJ","*.obj")])
        if path:
            self.scene.export_obj(path)
            self.status.set(f"Exported OBJ -> {path}")

    def export_stl(self):
        path=filedialog.asksaveasfilename(defaultextension=".stl",
                                          filetypes=[("STL","*.stl")])
        if path:
            self.scene.export_stl(path)
            self.status.set(f"Exported STL -> {path}")

    def export_png(self):
        path=filedialog.asksaveasfilename(defaultextension=".png",
                                          filetypes=[("PNG","*.png")])
        if path:
            self.fig.savefig(path,dpi=150)
            self.status.set(f"Saved PNG -> {path}")

    def show_about(self):
        messagebox.showinfo(
            "About",
            "3d_Measurment_Software_v02 — All-in-One Python 3D modeler\n\n"
            "No extra core file is required.\n"
            "Uses Tkinter, NumPy and Matplotlib only.\n\n"
            "Mouse controls:\n"
            "• Left-drag in the 3D view: rotate\n"
            "• Toolbar controls the standard Matplotlib 3D navigation\n"
            "• Select objects in Model Tree to edit properties."
        )


def main():
    app=MeasurementSoftwareApp()
    app.mainloop()


if __name__=="__main__":
    main()
