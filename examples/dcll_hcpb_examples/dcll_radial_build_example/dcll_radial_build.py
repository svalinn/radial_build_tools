import openmc
from radial_build_tools import ToroidalModel, RadialBuildPlot
from dcll_json_to_openmc import makematerial
import json

major_radius = 800
minor_radius_z = 114
minor_radius_xy = 114
scoring_layer_thickness = 0.5

with open('mixedMaterialsDCLL_libv1.json','r') as material_json:
    mixed_materials= json.load(material_json)

materials=makematerial(mixed_materials,'/filespace/l/lygre/cnergresearch/data/endfb-viii.0-hdf5/cross_sections.xml')


build_dict = {
    "sol": {"thickness": 5, 
        "composition": {"Void": 1.0}
    },
    "fw_armor": {"thickness": 0.2,
        "scores": ["heating"],
    },
    "fw": {
        "thickness": 3.8,
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "be_multiplier": {
        "thickness": 0,
        "scores": ["heating"],
    },
    "breeder": {
        "thickness": 50,
        "scores": ["tbr", "heating"],
    },
    "bw": {
        "thickness": 2,
        "scores": ["fast_fluence", "heating"],
    },
    "manifold": {
        "thickness": 6,
        "scores": ["heating"],
    },
    "hts_front_plate": {
        "thickness": scoring_layer_thickness,
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "hts": {
        "thickness": 10 - 2 * scoring_layer_thickness,
        "scores": ["heating"],
    },
    "hts_back_plate": {
        "thickness": scoring_layer_thickness,
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "gap_1": {"thickness": 1, "composition": {"Void": 1.0}},
    "vv_front_plate": {
        "thickness": 2,
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "vv_fill": {
        "thickness": 6,
        "scores": ["heating"],
    },
    "vv_back_plate": {
        "thickness": 2,
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "gap_2": {
        "thickness": 2,
    },
    "lts_front_plate": {
        "thickness": scoring_layer_thickness,
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "lts": {
        "thickness": 10 - 2 * scoring_layer_thickness,
        "scores": ["heating"],
    },
    "lts_back_plate": {
        "thickness": scoring_layer_thickness,
        "scores": ["fast_fluence", "he_prod", "fe_dpa", "heating"],
    },
    "thermal_insulator": {
        "thickness": 10,
        "scores": ["heating"],
    },
    "coil_pack_front_plate": {
        "thickness": scoring_layer_thickness,
        "scores": ["fast_fluence", "cu_dpa", "heating"],
    },
    "coil_pack": {
        "thickness": 52,
        "scores": ["heating"],
    },
}


for layer_name, properties in build_dict.items():
    if "composition" not in properties.keys():
        properties["material_name"] = layer_name

toroidal_model = ToroidalModel(
    build_dict, major_radius, minor_radius_z, minor_radius_xy, materials
)
model, cells = toroidal_model.get_openmc_model()
model.export_to_model_xml()

# make a radial build plot of the model
rbp = RadialBuildPlot(build_dict, title="Toroidal Model DCLL", size=(4, 3))
rbp.plot_radial_build()
rbp.to_png()