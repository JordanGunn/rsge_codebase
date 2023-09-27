import os
import shutil
import tkinter as tk
from tkinter import filedialog
import geopandas as gpd
from shapely.geometry import box
import laspy
import subprocess

class LASProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LAS COPY and TILE")

        self.shapefile_path = tk.StringVar()
        self.input_dir_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Path to Shapefile:").grid(row=0, column=0, padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.shapefile_path, width=40).grid(row=0, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_shapefile).grid(row=0, column=2, padx=5, pady=5)

        tk.Label(self.root, text="Input Directory:").grid(row=1, column=0, padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.input_dir_path, width=40).grid(row=1, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_input_dir).grid(row=1, column=2, padx=5, pady=5)

        tk.Label(self.root, text="Output Directory:").grid(row=2, column=0, padx=10, pady=5)
        tk.Entry(self.root, textvariable=self.output_dir_path, width=40).grid(row=2, column=1, padx=10, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_output_dir).grid(row=2, column=2, padx=5, pady=5)

        tk.Button(self.root, text="Execute", command=self.execute).grid(row=3, column=1, padx=10, pady=20)

    def browse_shapefile(self):
        filepath = filedialog.askopenfilename(filetypes=[("Shapefiles", "*.shp")])
        if filepath:
            self.shapefile_path.set(filepath)

    def browse_input_dir(self):
        dirpath = filedialog.askdirectory()
        if dirpath:
            self.input_dir_path.set(dirpath)

    def browse_output_dir(self):
        dirpath = filedialog.askdirectory()
        if dirpath:
            self.output_dir_path.set(dirpath)

    def delete_temp_folder(self, temp_dir_path):
        try:
            shutil.rmtree(temp_dir_path)
            print("Temporary folder deleted.")
        except Exception as e:
            print("Error deleting temporary folder:", e)

    def execute(self):
        shapefile_path = self.shapefile_path.get()
        input_dir_path = self.input_dir_path.get()
        output_dir_path = self.output_dir_path.get()

        temp_dir_path = os.path.join(output_dir_path, "Temp")
        os.makedirs(temp_dir_path, exist_ok=True)

        shape_gdf = gpd.read_file(shapefile_path)
        shape_geometry = shape_gdf.geometry.unary_union

        for root, _, files in os.walk(input_dir_path):
            for filename in files:
                if filename.lower().endswith(".las"):
                    las_filepath = os.path.join(root, filename)
                    if intersects_shapefile(las_filepath, shape_geometry):
                        temp_las_filepath = os.path.join(temp_dir_path, filename)
                        shutil.copy(las_filepath, temp_las_filepath)

        print("LAS files copied to Temp folder.")

        # Run lasclip command with -poly option
        lasclip_cmd = [
            r"C:\LAStools\bin\lasclip.exe",
            "-i", os.path.join(temp_dir_path, "*.las"),
            "-cpu64",
            "-cores", "8",
            "-merged",
            "-split", "MAP_TILE",
            "-poly", shapefile_path,
            "-odir", output_dir_path,
            "-olas"
        ]

        try:
            subprocess.run(lasclip_cmd, check=True)
            print("lasclip command completed.")
            self.delete_temp_folder(temp_dir_path)  # Delete the temporary folder
        except subprocess.CalledProcessError as e:
            print("Error running lasclip:", e)

def intersects_shapefile(las_filepath, shape_geometry):
    las_bounds = get_las_bounds(las_filepath)
    las_bbox = box(*las_bounds)
    return las_bbox.intersects(shape_geometry)

def get_las_bounds(las_filepath):
    las = laspy.file.File(las_filepath, mode="r")
    x_min, x_max = las.header.min[0], las.header.max[0]
    y_min, y_max = las.header.min[1], las.header.max[1]
    return x_min, y_min, x_max, y_max

if __name__ == "__main__":
    root = tk.Tk()
    app = LASProcessingApp(root)
    root.mainloop()