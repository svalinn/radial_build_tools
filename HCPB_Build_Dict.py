import openmc
from radial_build_tools import ToroidalModel, RadialBuildPlot
from openmc_Materials_Object_from_json import *

with open('mixedPureFusionMatsHCPB_libv1.json', 'r') as mixed_mat_json:
    mixed_mat = json.load(mixed_mat_json)

major_radius = 800
minor_radius_z = 114
minor_radius_xy = 114
scoring_layer_thickness = 0.5

make_mat = Make_Material(mixed_mat)
# openmc Materials object:
materials = Make_All_Materials(make_mat)

build_dict = {
    "sol": {
        "thickness": 5,
        "composition": {"Void": 1.0},
        "colour": "#E0E0E0",  # Light grey
      
    },
    "fw_armor": {
        "thickness": 0.2,
        #"composition": mixed_materials["FWWArmor"]["vol_fracs"],
        "material_name": "fw_armor",
        "colour": "#FFD700",  # Gold
        "scores": ["heating"], 
    },
    "fw": {
        "thickness": 3.8,
        #"composition": mixed_materials["FW"]["vol_fracs"],
        "material_name": "fw",
        "colour": "#DAA520",  # Goldenrod
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "breeder": {
        "thickness": 50,
        "composition": {"BreederHCPB": 1.0},
        "material_name": "breeder",
        "description": "Thickness Varies",
        "colour": "#B22222",  # Firebrick
        "scores": ["tbr", "heating"],
    },
    "bw": {
        "thickness": 10,
        "composition": {"BWHCPB": 1.0},
        "material_name": "bw",
        "colour": "#8B0000",  # Dark red
        "scores": ["tbr", "heating","fast_fluence"],
    },
    "manifold_front_plate": {
        "thickness": 5,
        "composition": {"EUROFER97": 1.0},
        "material_name": "manifold_front_plate",
        "colour": "#4682B4",  # Steel blue
        "scores": ["heating"],
    },
    "manifold": {
        "thickness": 10,
        "composition": {"HeT410P80": 1.0},
        "material_name": "manifold",
        "colour": "#5F9EA0",  # Cadet blue
    },
    "manifold_back_plate": {
        "thickness": 5,
        "composition": {"EUROFER97": 1.0},
        "material_name": "manifold_back_plate",
        "colour": "#4682B4",  # Steel blue
        "scores": ["heating"],
    },
    "hts_front_plate": {
        "thickness": scoring_layer_thickness,
        "material_name": "hts_front_plate",
        #"description": "for scoring, same composition as HTS",
        "colour": "#32CD32",  # Lime green
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "hts": {
        "thickness": 9,
        #"composition":  mixed_materials["FNSFIBSR"]["vol_fracs"],
        "material_name": "hts",
        "description": "Thickness Varies",
        "colour": "#00FF00",  # Green
        "scores": ["heating"],
    },
    "hts_back_plate": {
        "thickness": scoring_layer_thickness,
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
        #"composition": mixed_materials["VVFill"]["vol_fracs"],
        "material_name": "vv_front_plate",
        "colour": "#A9A9A9",  # Dark grey
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "vv_fill": {
        "thickness": 6,
        "composition": {"VVFill": 1.0},
        "material_name": "vv_fill",
        "colour": "#778899",  # Light slate grey
        "scores": ["heating"],
    },
    "vv_back_plate": {
        "thickness": 2,
        "composition": {"SS316L": 1.0},
        "material_name": "vv_back_plate",
        "colour": "#A9A9A9",  # Dark grey
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "gap_2": {
        "thickness": 2,
        "composition": {"AirSTP": 1.0},
        "material_name": "gap_2",
        "colour": "#E0FFFF",  # Light cyan
    },
    "lts_front_plate": {
        "thickness": scoring_layer_thickness,
        #"composition": {"LTS": 1.0},
        "material_name": "lts_front_plate",
        #"description": "For scoring, same composition as LTS",
        "colour": "#7FFFD4",  # Aquamarine
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "lts": {
        "thickness": 9,
        "composition": {"LTS": 1.0},
        "material_name": "lts",
        "description": "Thickness Varies",
        "colour": "#00FA9A",  # Medium spring green
        "scores": ["heating"],
    },
    "lts_back_plate": {
        "thickness": scoring_layer_thickness,
        #"composition": {"LTS": 1.0},
        "material_name": "lts_back_plate",
        #"description": "For scoring, same composition as LTS",
        "colour": "#7FFFD4",  # Aquamarine
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "thermal_insulator": {
        "thickness": 10,
        "composition": {"AirSTP": 1.0},
        "material_name": "thermal_insulator",
        "colour": "#B0E0E6",  # Powder blue
        "scores": ["heating"],
    },
    "coil_pack_front_plate": {
        "thickness": scoring_layer_thickness,
        "material_name": "coil_pack_front_plate",
        #"description": "cell for scoring peak values, same composition as coil_pack",
        "colour": "#FF6347",  # Tomato
        "scores": ["fast_fluence", "cu_dpa", "heating"],
    },
    "coil_pack": {
        "thickness": 52,
        "composition": {"coils": 1.0},
        "material_name": "coil_pack",
        "colour": "#FF4500",  # Orange red
        "scores": ["heating"],
    },
}

toroidal_model = ToroidalModel(
    build_dict, major_radius, minor_radius_z, minor_radius_xy, materials
)
