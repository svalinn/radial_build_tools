import openmc
import json
import yaml
import argparse
from radial_build_tools import ToroidalModel, RadialBuildPlot
from HCPB_Mix_Materials import make_mat_data

def make_build_dict(mat_info):
    '''
    Builds a dictionary of material names, thicknesses, compositions, plot colors, and tally scores.
    input:
        mat_info : dictionary of material names, compositions, and citations.
    '''
    build_dict = {
        "sol": {
            "thickness": 5,
            "composition": {"Void": 1.0},
            "colour": "#E0E0E0",  # Light grey
            },
        "fw_armor": {
            "thickness": 0.2,
            "colour": "#FFD700",  # Gold
            "scores": ["heating"], 
            },
        "fw": {
            "thickness": 3.8,
            "colour": "#DAA520",  # Goldenrod
            "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
            },
        "breeder": {
            "thickness": 50,
            "description": "Thickness Varies",
            "colour": "#B22222",  # Firebrick
            "scores": ["tbr", "heating"],
            },
        "bw": {
            "thickness": 10,
            "colour": "#8B0000",  # Dark red
            "scores": ["tbr", "heating","fast_fluence"],
            },
        "manifold": {
            "thickness": 20,
            "colour": "#5F9EA0",  # Cadet blue
            },  
        "hts": {
            "thickness": 10.5,
            "description": "Thickness Varies",
            "colour": "#00FF00",  # Green
            "scores": ["heating"],
            },
        "gap_1": {
            "thickness": 1,
            "colour": "#F5F5F5",  # White smoke
            },
        "vv_fill": {
            "thickness": 10,
            "colour": "#778899",  # Light slate grey
            "scores": ["heating"],
            },
        "gap_2": {
            "thickness": 2,
            "colour": "#E0FFFF",  # Light cyan
            }, 
        "lts": {
            "thickness": 10.5,
            "description": "Thickness Varies",
            "colour": "#00FA9A",  # Medium spring green
            "scores": ["heating"],
            },
        "thermal_insulator": {
            "thickness": 10,
            "colour": "#B0E0E6",  # Powder blue
            "scores": ["heating"],
            },
        "coil_pack": {
            "thickness": 53,
            "colour": "#FF4500",  # Orange red
            "scores": ["heating"],
            },
    }
    for component in list(build_dict.keys()):
        if component in list(mat_info.keys()):
            build_dict[component]['composition'] = mat_info[component]['composition']
            build_dict[component]['material_name'] = component
    return build_dict
    
def make_toroidal_model(materials_xml_file, major_radius, minor_radius_z, minor_radius_xy, build_dict):
        # openmc Materials object:
        materials = openmc.Materials.from_xml(materials_xml_file)
        toroidal_model = ToroidalModel(
        build_dict, major_radius, minor_radius_z, minor_radius_xy, materials)
        mat_geom, cell_dict = toroidal_model.get_openmc_model()
        return mat_geom, cell_dict

def plot_radial_build(radial_plot_name, build_dict):
        radial_build_plot = RadialBuildPlot(build_dict, title=radial_plot_name, size=(15, 5))
        radial_build_plot.plot_radial_build()
        radial_build_plot.to_png()
        return radial_build_plot

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--HCPB_YAML', default = 'HCPB_YAML.yaml', help="Path (str) to YAML containing inputs for HCPB build dictionary & mix materials")
    parser.add_argument('--radial_plot_name', default = 'HCPB_Toroidal_Model', help="Desired filename of radial build plot")
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
    build_dict = make_build_dict(mat_info)
    mat_geom, cell_dict = make_toroidal_model(yaml_inputs['filenames']['mat_xml'],
                                         yaml_inputs['geom']['major_radius'],
                                         yaml_inputs['geom']['minor_radius_z'],
                                         yaml_inputs['geom']['minor_radius_xy'],
                                         build_dict)
    plot_radial_build(args.radial_plot_name, build_dict)
    mat_geom.export_to_model_xml(yaml_inputs['filenames']['model_xml_name'])
    
if __name__ == "__main__":
    main()    
