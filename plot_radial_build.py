import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors
import yaml
import argparse

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
        line_len =len(comp_string+mat_string)-(comp_string+mat_string).find('\n')

        if line_len > max_characters:
            comp_string += '\n' + mat_string
        else:
            comp_string += mat_string

    return comp_string[0:-2]

def plot_radial_build(build, title, colors = None, 
                      max_characters = 35, max_thickness = 1e6, size = (8,4), 
                      unit = 'cm'):
    """
    Creates a radial build plot, with layers scaled between a minimum and
        maximum pixel width to preserve readability
    
    Arguments:
        build (dict): {"layer name": {"thickness": (float),
                                      "composition": {
                                        "material name": fraction (float)
                                }
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
    
        comp_string = build_composition_string(layer['composition'],
                                               max_characters)

        newlines = comp_string.count('\n')

        min_thickness = (min_lines + newlines) * min_line_height

        thickness = min(max(layer['thickness'], min_thickness), max_thickness)
            
        ax.add_patch(Rectangle(ll,thickness, height, facecolor = color, 
                               edgecolor = "black"))

        #put the text in
        centerx = (ll[0]+ll[0]+thickness)/2+1
        centery = (height)/2
        plt.text(centerx, centery, 
                 f'{name}: {thickness} {unit}\n{comp_string}', 
                 rotation = "vertical", ha = "center", va = "center", wrap=True)

        #update lower left corner
        ll[0] = ll[0]+float(thickness)

        total_thickness += thickness

    ax.set_xlim(-1, total_thickness+1)
    ax.set_axis_off()
    plt.title(title)
    plt.savefig(title.replace(' ',"") + '.png',dpi=200)
    plt.close()

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
