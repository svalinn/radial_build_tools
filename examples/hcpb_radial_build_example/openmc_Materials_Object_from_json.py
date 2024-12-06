import json
import openmc

"This script makes openmc.Material and openmc.Materials objects using .json files created with fusion-material-db"    

def make_material(mixed_mat_data):
    '''
    Makes openmc.Material objects for each material in .json file (specified when called).
    Adds density & nuclide information to each Material object
    inputs: 
        mixed_mat_data : JSON created by HCPB_Mix_Materials
    outputs:
        mat_list : list of OpenMC Material objects
    '''
    mat_list = []
    for material, mat_property in mixed_mat_data.items():
        mat_openmc = openmc.Material(name=material)
        mat_list.append(mat_openmc)
        mat_openmc.set_density('g/cm3', mat_property.get("density"))
        comp_list = mat_property.get("comp")
        for element, fraction in comp_list.items():
            mat_openmc.add_nuclide(element, fraction)       
    return mat_list

def make_all_materials(material_list):
    '''
    Makes openmc.Materials object using output of Make_Material()
    inputs:
        material_list : list of OpenMC Material objects
    outputs:
        all_materials : OpenMC Materials object 
    '''
    all_materials = openmc.Materials(material_list)
    all_materials.cross_sections = '../fendl-3.2-hdf5/cross_sections.xml'
    return all_materials 
