import openmc
import json

def makematerial(material_json,path_to_cross_sections):
    """
    imports previously generated JSON file and creates OpenMC materials object

    Returns: 
        materials: OpenMC materials object 
    """
    materials=openmc.Materials()
    for material_name, properties in material_json.items():
        openmc_material=openmc.Material(name=f"{material_name}")
        openmc_material.set_density('g/cm3', properties['density'])
        for element, fraction in properties['comp'].items():
            openmc_material.add_nuclide(element,fraction)
        materials.append(openmc_material)
    materials.cross_sections=path_to_cross_sections
    return materials
