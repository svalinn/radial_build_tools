import openmc
import json
from radial_build_tools import ToroidalModel, RadialBuildPlot
from HCPB_Mix_Materials import material_comp

major_radius = 800
minor_radius_z = 114
minor_radius_xy = 114
scoring_layer_thickness = 0.5

# openmc Materials object:
materials = openmc.Materials.from_xml("mixedPureFusionMatsHCPB_libv1.xml")

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

toroidal_model = ToroidalModel(
    build_dict, major_radius, minor_radius_z, minor_radius_xy, materials
)

rbp = RadialBuildPlot(build_dict, title="HCPB Toroidal Model", size=(15, 5))
rbp.plot_radial_build()
rbp.to_png()