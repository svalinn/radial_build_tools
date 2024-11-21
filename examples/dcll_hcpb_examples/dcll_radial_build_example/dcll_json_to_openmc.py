import openmc
import json

def makematerial(material_json,path_to_cross_sections):
    mat_list=[]
    for material, property in material_json.items():
        openmc_material=openmc.Material(name=f"{material}")
        mat_list.append(openmc_material)
        openmc_material.set_density('g/cm3', property.get('density'))
        composition=property.get('comp')
        for element, fraction in composition.items():
            openmc_material.add_nuclide(element,fraction)
    materials=openmc.Materials(mat_list)
    materials.cross_sections=path_to_cross_sections
    return materials
