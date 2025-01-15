import openmc
import json
import yaml
import argparse
import material_db_tools as mdbt

'''
This script specifies the composition of each HCPB component and its corresponding citation.
mdbt.mix_by_volume is called to mix individual materials and generate a new .json file.
'''

def make_mat_data(): 
    '''    
    Specfies volume fraction and corresponding citation for each radial component.
    '''
    #Volume fractions of constituent materials and corresponding citations
    mat_info = {
    'fw_armor' : {
        'composition' : {"W": 1.00},
        'citation' : "ZhouEUDEMOHCPB_2023"
        },
    'fw' : {
        'composition' : {"W": 0.1, "EUROFER97" : 0.9},
        'citation' : "ZhouEUDEMOHCPB_2023"
        },
    'breeder' : {
        'composition' : {"Be12Ti": 0.8, "Li4SiO4Li60.0":0.14837, "Li2TiO3Li60.0":0.05163},
        'citation' : "ZhouEUDEMOHCPB_2023"
        },
    'bw' : {
        'composition' : {"MF82H" : 0.8, "HeNIST" : 0.2},
        'citation' : "DavisFusEngDes_2018"  
        },
    'manifold' : {
        'composition' : {"HeT410P80": 1.00},
        'citation' : "DavisFusEngDes_2018"
        },
    'hts' : {
        'composition' : {"MF82H": 0.20, "HeNIST": 0.28, "BMF82H" : 0.52},
        'citation' : "DavisFusEngDes_2018"
        },
    'vv_fill' : {
        'composition' : {"HeNIST" : 0.4, "Cr3FS" : 0.6},
        'citation' : "DavisFusEngDes_2018"
        },
    'gap_2' : {
        'composition' : {"AirSTP": 1.0},
        'citation' : "ZhouEUDEMOHCPB_2023"
        },
    'lts' : {
        'composition' : {"Cr3FS": 0.39, "BMF82H": 0.29, "Water": 0.32},
        'citation' : "DavisFusEngDes_2018"
        },
    'thermal_insulator':{
        'composition' : {'AirSTP': 1.0},
        'citation' : "ZhouEUDEMOHCPB_2023"
        },
    'coil_pack': {
        'composition' : {"JK2LBSteel": 0.3, "Cu": 0.25, "TernaryNb3Sn" : 0.25, "Eins" : 0.1, "HeNIST" : 0.1},
        'citation' : "DavisFusEngDes_2018"
        },       
    }    
    return mat_info

def make_mixed_mat_lib(mat_info, pure_mat_json):
    '''
    Creates dictionary consisting of material name, composition, and citation.
    
    pure_mat_json : path to .json containing pure material compositions
    '''
    mat_data = {} 
    for mat_name, comp_cit in mat_info.items():
        mat_data[mat_name] = {
            'vol_fracs' : comp_cit['composition'],
            'mixture_citation' : comp_cit['citation'],
            }

    # Load material library
    mat_lib = mdbt.MaterialLibrary()
    mat_lib.from_json(pure_mat_json)

    # Create PyNE material library object
    mixmat_lib = mdbt.MaterialLibrary()
    for mat_name, mat_input in mat_data.items():
        mixmat_lib[mat_name] = mdbt.mix_by_volume(
            mat_lib, mat_input["vol_fracs"], mat_input["mixture_citation"]
        )
    return mixmat_lib
    
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--HCPB_YAML', default = 'HCPB_YAML.yaml', help="Path (str) to YAML containing inputs for HCPB build dictionary & mix materials")
    args = parser.parse_args()
    return args
    
def read_yaml(args):
    with open(args.HCPB_YAML, 'r') as hcpb_yaml:
        yaml_inputs = yaml.safe_load(hcpb_yaml)
    return yaml_inputs
    
def main():
    args = parse_args()
    yaml_inputs = read_yaml(args)
    mat_info = make_mat_data()
    mixmat_lib = make_mixed_mat_lib(mat_info,
                                    yaml_inputs['filenames']['pure_mat_json'])
    # write OpenMC Materials xml 
    mixmat_lib.write_openmc(yaml_inputs['filenames']['mat_xml'])

if __name__ == "__main__":
    main()    
