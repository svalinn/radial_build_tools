import openmc
import json
import yaml
import argparse
from radial_build_tools import ToroidalModel, RadialBuildPlot
from HCPB_Mix_Materials import material_comp

def make_build_dict(scoring_layer_thickness):
    build_dict = {
    "sol": {
        "thickness": 5,
        "composition": {"Void": 1.0},
        "colour": "#E0E0E0",  # Light grey
      
    },
    "fw_armor": {
        "thickness": 0.2,
        "composition" : material_comp['fw_armor'],
        "material_name": "fw_armor",
        "colour": "#FFD700",  # Gold
        "scores": ["heating"], 
    },
    "fw": {
        "thickness": 3.8,
        "composition" : material_comp['fw'],
        "material_name": "fw",
        "colour": "#DAA520",  # Goldenrod
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "breeder": {
        "thickness": 50,
        "composition" : material_comp['breeder'],
        "material_name": "breeder",
        "description": "Thickness Varies",
        "colour": "#B22222",  # Firebrick
        "scores": ["tbr", "heating"],
    },
    "bw": {
        "thickness": 10,
        "composition": material_comp['bw'],
        "material_name": "bw",
        "colour": "#8B0000",  # Dark red
        "scores": ["tbr", "heating","fast_fluence"],
    },
    "manifold_front_plate": {
        "thickness": 5,
        "composition": material_comp['manifold_front_plate'],
        "material_name": "manifold_front_plate",
        "colour": "#4682B4",  # Steel blue
        "scores": ["heating"],
    },
    "manifold": {
        "thickness": 10,
        "composition": material_comp['manifold'],
        "material_name": "manifold",
        "colour": "#5F9EA0",  # Cadet blue
    },
    "manifold_back_plate": {
        "thickness": 5,
        "composition": material_comp['manifold_back_plate'],
        "material_name": "manifold_back_plate",
        "colour": "#4682B4",  # Steel blue
        "scores": ["heating"],
    },
    "hts_front_plate": {
        "thickness": 1,
        "composition" : material_comp['hts_front_plate'],
        "material_name": "hts_front_plate",
        #"description": "for scoring, same composition as HTS",
        "colour": "#32CD32",  # Lime green
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "hts": {
        "thickness": 9,
        "composition" : material_comp['hts'],
        "material_name": "hts",
        "description": "Thickness Varies",
        "colour": "#00FF00",  # Green
        "scores": ["heating"],
    },
    "hts_back_plate": {
        "thickness": scoring_layer_thickness,
        "composition" : material_comp['hts_back_plate'],
        "material_name": "hts_back_plate",
        #"description": "for scoring, same composition as HTS",
        "colour": "#32CD32",  # Lime green
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "gap_1": {
        "thickness": 1,
        "composition": {"Void": 1.0},
        "colour": "#F5F5F5",  # White smoke
    },
    "vv_front_plate": {
        "thickness": 2,
        "composition" : material_comp['vv_front_plate'],
        "material_name": "vv_front_plate",
        "colour": "#A9A9A9",  # Dark grey
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "vv_fill": {
        "thickness": 6,
        "composition" : material_comp['vv_fill'],
        "material_name": "vv_fill",
        "colour": "#778899",  # Light slate grey
        "scores": ["heating"],
    },
    "vv_back_plate": {
        "thickness": 2,
        "composition": material_comp['vv_back_plate'],
        "material_name": "vv_back_plate",
        "colour": "#A9A9A9",  # Dark grey
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "gap_2": {
        "thickness": 2,
        "composition": material_comp['gap_2'],
        "material_name": "gap_2",
        "colour": "#E0FFFF",  # Light cyan
    },
    "lts_front_plate": {
        "thickness": scoring_layer_thickness,
        "composition" : material_comp['lts_front_plate'],
        "material_name": "lts_front_plate",
        #"description": "For scoring, same composition as LTS",
        "colour": "#7FFFD4",  # Aquamarine
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "lts": {
        "thickness": 9,
        "composition" : material_comp['lts'],
        "material_name": "lts",
        "description": "Thickness Varies",
        "colour": "#00FA9A",  # Medium spring green
        "scores": ["heating"],
    },
    "lts_back_plate": {
        "thickness": 1,
        "composition" : material_comp['lts_back_plate'],
        "material_name": "lts_back_plate",
        #"description": "For scoring, same composition as LTS",
        "colour": "#7FFFD4",  # Aquamarine
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "thermal_insulator": {
        "thickness": 10,
        "composition": material_comp['thermal_insulator'],
        "material_name": "thermal_insulator",
        "colour": "#B0E0E6",  # Powder blue
        "scores": ["heating"],
    },
    "coil_pack_front_plate": {
        "thickness": 1,
        "composition" : material_comp['coil_pack_front_plate'],
        "material_name": "coil_pack_front_plate",
        #"description": "cell for scoring peak values, same composition as coil_pack",
        "colour": "#FF6347",  # Tomato
        "scores": ["fast_fluence", "cu_dpa", "heating"],
    },
    "coil_pack": {
        "thickness": 52,
        "composition" : material_comp['coil_pack'],
        "material_name": "coil_pack",
        "colour": "#FF4500",  # Orange red
        "scores": ["heating"],
    },
}
    return build_dict
    
def make_toroidal_model(materials_xml_file, major_radius, minor_radius_z, minor_radius_xy, build_dict):
        # openmc Materials object:
        materials = openmc.Materials.from_xml(materials_xml_file)
        toroidal_model = ToroidalModel(
        build_dict, major_radius, minor_radius_z, minor_radius_xy, materials)
        return toroidal_model

def plot_radial_build(radial_plot_name, build_dict):
        radial_build_plot = RadialBuildPlot(build_dict, title=radial_plot_name, size=(15, 5))
        radial_build_plot.plot_radial_build()
        radial_build_plot.to_png()
        return radial_build_plot

def main():
    def parse_args():
        parser = argparse.ArgumentParser()
        parser.add_argument('--HCPB_YAML', default = 'HCPB_YAML.yaml', help="Path (str) to YAML containing inputs for HCPB build dictionary & mix materials")
        args = parser.parse_args()
        return args
    
    def read_yaml(args):
        with open(args.HCPB_YAML, 'r') as hcpb_yaml:
            yaml_inputs = yaml.safe_load(hcpb_yaml)
        return yaml_inputs
   
    args = parse_args()
    yaml_inputs = read_yaml(args)
    build_dict = make_build_dict(yaml_inputs['geom']['scoring_layer_thickness'])
    toroidal_model = make_toroidal_model(yaml_inputs['filenames']['mat_xml'],
                                         yaml_inputs['geom']['major_radius'],
                                         yaml_inputs['geom']['minor_radius_z'],
                                         yaml_inputs['geom']['minor_radius_xy'],
                                         build_dict)
    plot_radial_build(yaml_inputs['filenames']['radial_plot_name'], build_dict)

if __name__ == "__main__":
    main()    