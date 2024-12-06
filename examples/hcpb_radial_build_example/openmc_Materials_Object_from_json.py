import json
import openmc

"This script makes openmc.Material and openmc.Materials objects using .json files created with fusion-material-db"    

def Make_Material(mixed_mat_data):
    '''
    Makes openmc.Material objects for each material in .json file (specified when called).
    Adds density & nuclide information to each Material object
    '''
    mat_list = []
    for material, mat_property in mixed_mat_data.items():
        mat_openmc = openmc.Material(name=f"{material}")
        mat_list.append(mat_openmc)
        mat_openmc.set_density('g/cm3', mat_property.get("density"))
        comp_list = mat_property.get("comp")
        for element, fraction in comp_list.items():
            mat_openmc.add_nuclide(element, fraction)       
    return mat_list

def Make_All_Materials(material_list):
    '''
    Makes openmc.Materials object using output of Make_Material()
    '''
    all_materials = openmc.Materials(material_list)
    all_materials.cross_sections = '../fendl-3.2-hdf5/cross_sections.xml'
    return all_materials 
