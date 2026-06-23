import stat
import openmc
from radial_build_tools import ToroidalModel,RadialBuildPlot
import matplotlib.pyplot as plt
from pathlib import Path
import pandas as pd
# torus parameters
major_radius = 800
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
PbLi.add_element("Pb", 63.0, "ao")
PbLi.add_element("Li", 37.0, "ao", enrichment=90.0, enrichment_target="Li6")
PbLi.set_density("g/cm3", 9.806)
materials = openmc.Materials([RAFM, PbLi, W])


#wall definition
#inner_radius = 50.0   # cm (plasma region)
#outer_radius = 55.0   # cm (tungsten wall thickness = 5 cm)
#inner_sphere = openmc.Sphere(r=inner_radius, boundary_type="transmission")
#outer_sphere = openmc.Sphere(r=outer_radius, boundary_type="vacuum")
#wall_region = +inner_sphere & -outer_sphere
#wall = openmc.Cell(name="tungsten_wall", fill=W, region=wall_region)

results=[]

for thickness in range(10, 71, 10): #cm)
    build = {
        "inboard": {
            "sol": {
                "thickness": 5,
                "description": "Vacuum",
            },
            "FW": {
                "thickness": 4,
                "material_name": RAFM.name,
                "description": RAFM.name,
                "color": "#e0218a",
            },
            "Breeder": {
                "thickness": thickness, #cm, thickness of the breeder layer
                "material_name": PbLi.name,
                "description": PbLi.name,
        
            },
            "bogus layer": {
                "thickness": 0,
                "description": "this layer will be skipped due to zero thickness",
            },
            "shield": {
                "thickness": 30, #cm, thickness of the shield layer
                "material_name": W.name,
                "description": W.name,
            },
        },
        "outboard": {
            "sol": {
                "thickness": 5,
                "description": "Vacuum",
            },
            "FW": {
                "thickness": 4,
                "material_name": RAFM.name,
                "description": RAFM.name,
                "color": "#e0218a",
            },
            "Breeder": {
                "thickness": thickness, #cm, thickness of the breeder layer
                "material_name": PbLi.name,
                "description": PbLi.name,
        
            },
            "bogus layer": {
                "thickness": 0,
                "description": "this layer will be skipped due to zero thickness",
            },
            "shield": {
                "thickness": 30, #cm, thickness of the shield layer
                "material_name": W.name,
                "description": W.name,
            },
        }
    }
    toroidal_model = ToroidalModel(
        build,
        major_radius,
        plasma_minor_z_radius,
        plasma_minor_xy_radius,
        materials,
)
#settings

    model, cells = toroidal_model.get_openmc_model()
    shield_cell = cells["outboard_shield"]
    breeder_cell = cells["outboard_Breeder"]
    model.settings = openmc.Settings()

    radius =openmc.stats.Discrete([major_radius],[1]) # cm, source is located at the center of the plasma region

    angle = openmc.stats.Uniform(a=0., b=2* 3.14)

    z_values = openmc.stats.Discrete([0], [1])

    source = openmc.IndependentSource(
        space=openmc.stats.CylindricalIndependent(r=radius, phi=angle, z=z_values, origin=(0.0, 0.0, 0.0)),
        angle=openmc.stats.Isotropic(),
        energy=openmc.stats.muir(e0=14080000.0, m_rat=5.0, kt=20000.0)
    )

    source.energy = openmc.stats.Discrete([14.1e6], [1.0])  # eV [1,0] here means that all neutrons are emitted with 14.1 MeV energy

    source.angle = openmc.stats.Isotropic()

    tallies = openmc.Tallies()
    flux_tally = openmc.Tally(name="flux")
    flux_tally.filters = [openmc.CellFilter(shield_cell)]
    flux_tally.scores = ["flux"]

    tbr_tally = openmc.Tally(name='TBR')
    tbr_tally.filters = [openmc.CellFilter(breeder_cell)]
    tbr_tally.scores = ['H3-production'] # Covvers both Li6 and Li7, as they both produce tritium.
    cell_filter= [openmc.CellFilter(breeder_cell)]

#tbr_tally.nuclides = ['Li6', 'Li7']-

    tallies = openmc.Tallies([flux_tally,tbr_tally])
    model.tallies = tallies

    model.settings.source = source
    model.settings.run_mode = "fixed source"
    model.settings.batches = 2
    model.settings.particles =1000
    model.settings.survival_biasing = True
    model.export_to_model_xml()s
    sp_filename=model.run()

    with openmc.StatePoint(sp_filename) as sp:
        flux_tally = sp.get_tally(name="flux")
        tbr_tally = sp.get_tally(name="TBR")

    results.append({
        "thickness": thickness,
        "flux": flux_tally.mean.sum(),
        "tbr": tbr_tally.mean.sum()
    })
    
df = pd.DataFrame({
    "nuclide": tbr_tally.nuclides,
    "mean": tbr_tally.mean.flatten(),
    "std. dev.": tbr_tally.std_dev.flatten()
})
sp.close()

    
df_2=pd.DataFrame(results) 


#print(df_2)
df_2.plot(x="thickness", y="flux", kind="line")
plt.xlabel("Breeder Thickness (cm)")
plt.ylabel("Flux")
plt.title("Flux vs Breeder Thickness")
plt.grid(True)
df_2.plot(x="thickness", y="tbr", kind="line")
plt.xlabel("Shield Thickness (cm)")
plt.ylabel("Tritium Breeding Ratio (TBR)")
plt.title("TBR and Flux vs Breeder Thickness")
plt.grid(True)


plt.show()
sp= openmc.StatePoint("statepoint.20.h5")

model.tallies = tallies# make a radial build plot of the model

rbp = RadialBuildPlot(build, title="Toroidal Model Example", size=(4, 3))

rbp.plot_radial_build()

rbp.to_png()
