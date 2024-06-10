import openmc
from radial_build_tools import ToroidalModel

# wistell d esque values
a = 800
b = 300
c = 100
# Define tungsten
W = openmc.Material(name="Tungsten")
W.add_element("W", 1.0)
W.set_density("g/cm3", 19.35)

# Define reduced-activation ferritic martensitic (RAFM) steel
RAFM = openmc.Material(name="RAFM")
RAFM.add_element("Fe", 0.895, "wo")  # number, 'wo' --> weight ratio
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
    "sol": {"thickness": 5, "material": None, "description": "Vacuum"},
    "FW": {"thickness": 4, "material": RAFM, "description": RAFM.name},
    "Breeder": {"thickness": 20, "material": PbLi, "description": PbLi.name},
    "bogus layer": {"thickness":0, "description":'this layer will be skipped'},
    "shield": {"thickness": 20, "material": W, "description": W.name},
}

toroidal_model = ToroidalModel(build, 1000, 100, 100)
model, cells = toroidal_model.get_openmc_model()
model.export_to_model_xml()

# make a radial build plot of the model
toroidal_model.get_radial_build_plot(
    title="Toroidal Model Example", size=(4, 3)
).to_png()
