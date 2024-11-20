## Workflow for using `radial_build_tools` and `fusion-materials-db`
1. Create Materials Dictionary file
    1. Each dictionary entry should be of the form: `"<part_name>":{"composition":{<composition>}, "citation":"<citation>"},` ,adding `"density_factor"` when needed
    2. Export to .json file
    3. An example is `dcll_materials.py`
2. Create build file
    1. Import json to openmc function `dcll_json_to_openmc.py`
    2. Import `ToroidalModel` from `radial_build_tools`
    2. Set major and minor radii 
    3. Call json to openmc function with json file and path to cross_sections file
    4. Create nested build dictionary of the form:
    ```
    "<part_name>": {"thickness": <thickness>,
        "scores": ["<score>"],
    },
    ``` 
    5. If layer is void add `"composition": {"Void": 1.0}` to the dictionary
    6. Call `TorodialModel`
    7. An example is `dcll_radial_build`