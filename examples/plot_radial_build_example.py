import plot_radial_build

build_dict = {
    # here is a layer with no optional data incluede
    "sol": {},

    # here is a layer where only thickness is included
    "FW_armor": {"thickness": 0.2},

    "FW": {'thickness': 3.8, 'composition': {"MF82H": 0.34, "HeT410P80": 0.66}},

    # here is a layer where only a description is included
    "breeder": {'description': "Composition and thickness vary"},

    'BW': {'thickness': 2, 'composition': {"MF82H": 0.80, "HeT410P80": 0.20}},

    # here is a layer where thickness and description are included
    'manifolds': {'thickness': 10, "description": "composition varies"},

    'HTS': {'description': "Composition and thickness vary"},

    # here is a layer where only composition is inclued
    'gap_1': {'composition': {"Void": 1.0}},

    'vv_front_plate': {'thickness': 2, 'composition': {"SS316L": 1.0}},

    'vv_fill': {'thickness': 6, 'composition': {"SS316L": 0.6, 
                                                "HeT410P80": 0.4}},

    'vv_back_plate': {'thickness': 2, 'composition': {"SS316L": 1.0}},

    'gap_2': {'thickness': 2, 'composition': {"Void": 1.0}},

    'LTS': {'description': "Composition and thickness vary"},

    'Thermal Insulator (Gap)': {'thickness': 10, 
                                'composition': {"Void": 1.0}},

    # here is a layer with all optional data included
    'Coil Pack': {'thickness': 52.5, 'composition': {"SS316L": 0.7435, 
                                                     "HTS TAPE": 0.0622, 
                                                     "Cu": 0.1307, 
                                                     "Solder": 0.0438, 
                                                     "HeT410P80": 0.0288},
                  'description': '[combines winding pack and coil case]'}
}

# note that since this is quite a detailed radial build, the default figure
# size was insufficient
radial_build = plot_radial_build.radial_build(build_dict, 'Example Radial Build',
                  max_characters=39, size=(10, 4))

# create the radial build plot png
radial_build.plot_radial_build()

# save the plot configuration as a yml file
radial_build.write_yml()

