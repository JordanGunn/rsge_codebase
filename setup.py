import setuptools

setuptools.setup(
    include_package_data=True,
    name="rsge_toolbox",
    python_requires=">=3.9.0",
    version="1.0.0",
    description="A collection of geospatial tools developed by the RSGE group at GeoBC.",
    url=r"https://github.com/brettedw/RSGE_codebase/tree/master/LiDAR",
    author="Remote Sensing and Geomatics Engineering (RSGE), GeoBC, B.C. Ministry",
    packages=[
        "rsge_toolbox",
        "rsge_toolbox.lidar",
        "rsge_toolbox.util",
        "rsge_toolbox.raster"
    ],
    install_requires=[
        "laspy>=2.4.1", "lazrs>=0.5.0", "numpy>=1.23.1", "pandas>=1.4.3"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent"
    ]
)
