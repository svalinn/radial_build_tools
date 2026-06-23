import openmc
# -------------------------
# MATERIALS
# -------------------------
tungsten = openmc.Material(name="tungsten")
tungsten.add_element("W", 1.0)
tungsten.set_density("g/cm3", 19.25)

materials = openmc.Materials([tungsten])
#2. GEOMETRY
#    sphere = plasma + wall
inner_radius = 50.0   # cm (plasma region)
outer_radius = 55.0   # cm (tungsten wall thickness = 5 cm)
inner_sphere = openmc.Sphere(r=inner_radius, boundary_type="vacuum")
outer_sphere = openmc.Sphere(r=outer_radius, boundary_type="vacuum")
# regions
plasma_region = -inner_sphere
wall_region = +inner_sphere & -outer_sphere
outside_region = +outer_sphere
# cells
plasma = openmc.Cell(name="plasma", region=plasma_region)
wall = openmc.Cell(name="tungsten_wall", fill=tungsten, region=wall_region)
outside = openmc.Cell(name="outside", region=outside_region)
geometry = openmc.Geometry([plasma, wall, outside])
geometry = openmc.Geometry([plasma, wall, outside])
vacuum = openmc.Material(name="vacuum")
vacuum.set_density("g/cm3", 1e-25)  # near-zero density
vacuum.add_nuclide("H1", 1.0)

materials = openmc.Materials([tungsten, vacuum])
plasma = openmc.Cell(fill=vacuum, region=plasma_region)
outside = openmc.Cell(fill=vacuum, region=outside_region)
# 3. SETTINGS (FUSION SOURCE)
settings = openmc.Settings()
settings.run_mode = "fixed source"
settings.particles = 5000
settings.batches = 20
# 14.1 MeV neutron point source (D-T fusion)
source = openmc.IndependentSource()
source.space = openmc.stats.Point((0, 0, 0))
source.energy = openmc.stats.Discrete([14.1e6], [1.0])  # eV
source.angle = openmc.stats.Isotropic()
settings.source = source
# 4. TALLIES (optional but useful)
tallies = openmc.Tallies()
flux_tally = openmc.Tally(name="flux")
flux_tally.filters = [
    openmc.CellFilter(wall)
]
flux_tally.scores = ["flux"]
tallies.append(flux_tally)
# 5. MODEL
model = openmc.Model(geometry, materials, settings, tallies)
model.run()