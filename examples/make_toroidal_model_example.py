import openmc
from radial_build_tools import ToroidalModel, RadialBuildPlot

# torus parameters
major_radius = 500
plasma_minor_z_radius = 300
plasma_minor_xy_radius = 100

# Define tungsten
W = openmc.Material(name="Tungsten")
W.add_element("W", 1.0)
W.set_density("g/cm3", 19.35)

# Define reduced-activation ferritic martensitic (RAFM) steel
RAFM = openmc.Material(name="RAFM")
RAFM.add_element("Fe", 0.895, "wo")
RAFM.add_element("Cr", 0.09, "wo")
RAFM.add_element("W", 0.015, "wo")
RAFM.set_density("g/cm3", 7.8)

# Define lead-lithium eutectic coolant/breeder
PbLi = openmc.Material(name="PbLi")
PbLi.add_element("Pb", 83.0, "ao")
PbLi.add_element("Li", 17.0, "ao", enrichment=90.0, enrichment_target="Li6")
PbLi.set_density("g/cm3", 9.806)

materials = openmc.Materials([RAFM, PbLi, W])

build = {
    "sol": {
        "thickness": [4,200],
        "description": "Vacuum",
    },
    "FW": {
        "thickness": [12,30],
        "material_name": RAFM.name,
        "description": RAFM.name,
        "color": "#e0218a",
    },
    "Breeder": {
        "thickness": [8,25],
        "material_name": PbLi.name,
        "description": PbLi.name,
        "scores": ["flux", "H3-production"],
    },
    "bogus layer": {
        "thickness": 0,
        "description": "this layer will be skipped due to zero thickness",
    },
    "shield": {
        "thickness": [9,30],
        "material_name": W.name,
        "description": W.name,
    },
}
ang_1 = 60 #Toroidal plane 1 defined by angle ang_1 and toroidal plane 2 defined by angle ang_2 to create Toroidal sector
ang_2 = 120
toroidal_model = ToroidalModel(
    build,
    major_radius,
    plasma_minor_z_radius,
    plasma_minor_xy_radius,
    materials,
    ang_1=ang_1,
    ang_2=ang_2,
)
model, cells = toroidal_model.get_openmc_model()
plot = openmc.Plot()
plot.filename = "xz_slice.png"
plot.basis = "xz"
plot.origin = (0.0, 0.0, 0.0)
plot.width = (
    3 *major_radius, 
    3 * major_radius,
)
plot.pixels = (1000, 1000)
plot.color_by = "material"

model.plots = openmc.Plots([plot])
model.export_to_model_xml()
openmc.plot_geometry()
# make a radial build plot of the model
rbp = RadialBuildPlot(build, title="Toroidal Model Example", size=(4, 3))
rbp.plot_radial_build()
rbp.to_png()
