import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors
import yaml
import argparse

def wrap_text(text, max_characters):
    """
    loop thru text, if line length is too long, go back and replace the 
    previous space with a linebreak

    Arguments: 
        text (str): text to wrap
        max_characters (int): line length limit

    returns:
        text (str): wrapped text
    """

    character_counter = 0
    for index, character in enumerate(text):
        
        character_counter += 1
        if character == ' ':
            space_index = index
        elif character == '\n':
            character_counter = 0

        if character_counter > max_characters:
            text = text[:space_index]+'\n'+text[space_index+1:]
            character_counter = 0

    return text

def build_composition_string(composition, max_characters):
    """
    Assembles string from composition dict for use in radial build plot

    Arguments:
        composition (dict): "material name (str)":volume_fraction (float)

    Returns:
        comp_string (string): formatted string with material definition
    """

    comp_string = ''
    for material, fraction in composition.items():
        
        mat_string = f'{material}: {round(fraction*100,3)}%, '
        comp_string += mat_string
        
    comp_string = wrap_text(comp_string, max_characters)

    return comp_string[0:-2]+'\n'

def write_yaml(build, title, colors, max_characters, max_thickness, size, unit):
    """
    Writes yml file defining radial build plot generated. File will be called
    title.yml

    Arguments:
        build (dict): build dict used in plot_radial_build
        title (string): title for plot and filename to save to
        colors (list of str): list of matplotlib color strings. 
            If specific colors are desired for each layer they can be added here
        max_characters (float): maximum length of a line before wrapping the 
            text
        max_thickness (float): maximum thickness of layer to display, useful
            for reducing the total size of the figure.
        size (iter of float): figure size, inches. (width, height)
        unit (str): Unit of thickness values
    """
    
    data_dict = {}
    data_dict['build'] = build
    data_dict['title'] = title
    data_dict['colors'] = colors
    data_dict['max_characters'] = max_characters
    data_dict['max_thickness'] = max_thickness
    data_dict['size'] = size
    data_dict['unit'] = unit

    filename = title.replace(' ',"") + '.yml'

    with open(filename, 'w') as file:
        yaml.safe_dump(data_dict, file, default_flow_style=False)

    

def plot_radial_build(build, title, colors = None, 
                      max_characters = 35, max_thickness = 1e6, size = (8,4), 
                      unit = 'cm', write_yml=True):
    """
    Creates a radial build plot, with layers scaled between a minimum and
        maximum pixel width to preserve readability
    
    Arguments:
        build (dict): {"layer name": {"thickness": (float) optional,
                                    "composition": (dict) optional {
                                    "material name": fraction (float)
                                    }
                                    "description": (str) optional
                            }
                        }
        title (string): title for plot and filename to save to
        colors (list of str): list of matplotlib color strings. 
            If specific colors are desired for each layer they can be added here
        max_characters (float): maximum length of a line before wrapping the 
            text
        max_thickness (float): maximum thickness of layer to display, useful
            for reducing the total size of the figure.
        size (iter of float): figure size, inches. (width, height)
        unit (str): Unit of thickness values
    """

    char_to_height = 1.15
    min_line_height = 8
    min_lines = 2
    height = char_to_height*max_characters

    if colors is None: 
        colors = list(matplotlib.colors.XKCD_COLORS.values())[0:len(build)]

    #initialize list for lower left corner of each layer rectangle
    ll = [0,0]
    plt.figure(1, figsize=size)
    plt.tight_layout()
    ax = plt.gca()
    ax.set_ylim(0,height+1)

    total_thickness = 0
    for (name, layer), color in zip(build.items(), colors):
        
        if 'thickness' not in layer:
            layer['thickness'] = min_line_height
            thickness_str = ''
        else:
            thickness_str = f': {layer['thickness']} {unit}'

        if 'composition' not in layer:
            comp_string = ''
        else:
            comp_string = build_composition_string(layer['composition'],
                                               max_characters)
            
        if 'description' not in layer:
            description_str = ''
        else:
            description_str = wrap_text(f'{layer['description']}', max_characters)
        
        text = f'{name}{thickness_str}\n{comp_string}{description_str}'
        text = wrap_text(text, max_characters)
        if text[-1] == '\n':
            text = text[0:-1]

        newlines = text.count('\n')

        min_thickness = (min_lines + newlines) * min_line_height

        thickness = min(max(layer['thickness'], min_thickness), max_thickness)
            
        ax.add_patch(Rectangle(ll,thickness, height, facecolor = color, 
                               edgecolor = "black"))

        #put the text in
        centerx = ll[0] + thickness/2 + 1
        centery = height/2
                 
        plt.text(centerx, centery, text, rotation = "vertical", ha = "center",
                 va = "center")

        ll[0] += float(thickness)

        total_thickness += thickness

    ax.set_xlim(-1, total_thickness+1)
    ax.set_axis_off()
    plt.title(title)
    plt.savefig(title.replace(' ',"") + '.png',dpi=200)
    plt.close()

    if write_yaml:
        write_yaml(build, title, colors, max_characters, max_thickness, size, 
                   unit)

def parse_args():
    """Parser for running as a script
    """
    parser = argparse.ArgumentParser(prog='plot_radial_build')

    parser.add_argument(
        'filename', help='YAML file defining radial build'
    )

    return parser.parse_args()

def read_yaml(filename):
    """Reads yaml file to extract title and build variables
    """
    with open(filename) as file:
        data = yaml.safe_load(file)
    
    return data

def main():

    #default data for running from command line
    data_default = {
        'title':'Radial Build',
        'colors':None,
        'max_characters':35,
        'max_thickness':1e6,
        'size':(8,4),
        'unit': 'cm'
    }

    args = parse_args()
    data = read_yaml(args.filename)

    data_dict = data_default.copy()
    data_dict.update(data)
    
    plot_radial_build(data_dict['build'], data_dict['title'], 
                      data_dict['colors'], data_dict['max_characters'],
                      data_dict['max_thickness'], data_dict['size'],
                      data_dict['unit'])

if __name__ == "__main__":
    main()
