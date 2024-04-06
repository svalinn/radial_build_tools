import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import matplotlib.colors

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
        line_len =len(comp_string)-(comp_string+mat_string).rfind('\n')

        if line_len > max_characters:
            comp_string += '\n' + mat_string
        else:
            comp_string += mat_string

    return comp_string[0:-2]

def plot_radial_build(build, Title = "Radial Build", colors = None, 
                      max_characters = 35, max_thickness = None, size = (8,4), 
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
    for layer, color in zip(build, colors):

        comp_string = build_composition_string(build[layer]['composition'],
                                               max_characters)
        newlines = comp_string.count('\n')

        # adjust thicknesses
        if max_thickness is not None:
            if build[layer]['thickness'] > max_thickness:
                
                build[layer]['thickness'] = max_thickness

        if build[layer]['thickness'] < (2 + newlines)*min_line_height:
            thickness = (2 + newlines)*min_line_height
        else:
            thickness = build[layer]['thickness']

        ax.add_patch(Rectangle(ll,thickness, height, facecolor = color, 
                               edgecolor = "black"))

        #put the text in
        centerx = (ll[0]+ll[0]+thickness)/2+1
        centery = (height)/2
        plt.text(centerx, centery, 
                 f'{layer}: {thickness} {unit} \n {comp_string}', 
                 rotation = "vertical", ha = "center", va = "center", wrap=True)

        #update lower left corner
        ll[0] = ll[0]+float(thickness)

        total_thickness += thickness

    ax.set_xlim(-1, total_thickness+1)
    ax.set_axis_off()
    plt.title(Title)
    plt.savefig(Title.replace(' ',"") + '.png',dpi=200)

    plt.close()


def main():
    #example
    build = {
        "SOL":{'thickness':4, "composition":{"Vacuum":1}},
        "FW":{'thickness':4, "composition":{"MF82H":0.34,"He":0.66}},
        "Breeder":{"thickness":50, "composition":{"FNSFDCLL":1.0}},
        "BW":{'thickness':4, "composition":{"MF82H":0.8,"He":0.8}},
        "HTS":{"thickness":20,
            "composition":{'WC':0.69, "He":0.26, "MF82H":0.05}},
        "VV":{"thickness":10, 'composition':{"SS316L":1.0}},
        "LTS":{"thickness":20, 
            'composition':{"Water":0.3, "WC":0.33, "SS316L":0.3}},
        "Winding Pack": {"thickness":63, 
                         'composition':{'Cu':0.43, 'JK2LB':0.29, 'He':0.14,
                            'Nb3Sn':0.06, 'Insulator':0.08}}
    }
    
    plot_radial_build(build, Title="Example Radial Build", max_thickness=40)



if __name__ == "__main__":
    main()
