import csv
import os
import sys
import pandas as pd
from collections import OrderedDict
from bokeh.io import show, output_file
from bokeh.plotting import figure
from bokeh.models import HoverTool


def read_csv(path):
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')
        _headers = next(reader, None)

        # get column
        _columns = {}
        for h in _headers:
            _columns[h] = []
        for row in reader:
            for h, v in zip(_headers, row):
                _columns[h].append(v)

        for item in _headers:
            print(item)

        return _headers, _columns


if __name__ == '__main__':
    tools_list = "pan," \
                 "box_select," \
                 "lasso_select," \
                 "box_zoom, " \
                 "wheel_zoom," \
                 "reset," \
                 "save," \
                 "help"
    # "hover," \

    input_id = 78
    if len(sys.argv) >= 2:
        input_id = sys.argv[1]
    nuclei_file_name = rf'quant_slide{str(input_id)}_region6.csv'
    output_root_path = r'G:\GE\HubmapDemoDay_Dec14th_2020_Vessel_Nuclei_Segmentation_NucleiQuantification\output'
    nuclei_output_name = nuclei_file_name.replace('region6', 'region6_nuclei')
    nuclei_file_path = os.path.join(output_root_path, nuclei_output_name)
    vessel_output_name = nuclei_file_name.replace('region6', 'region6_vessel')
    vessel_file_path = os.path.join(output_root_path, vessel_output_name)

    output_file("result/distance.html")

    drug_color = OrderedDict([
        ("Item Category", "#0d33ff"),
        ("Item metadata", "#c64737"),
        ("User profile", "black"),
    ])

    gram_color = OrderedDict([
        ("negative", "#e69584"),
        ("positive", "#aeaeb8"),
    ])

    index = 1
    p = figure(match_aspect=True,
               plot_width=int(7454 * index), plot_height=int(4711 * index),
               tools=tools_list, output_backend="svg",
               # title='nuclei/vessel distance',
               )

    p.background_fill_color = None
    p.border_fill_color = None

    p.xgrid.visible = False
    p.ygrid.visible = False
    p.axis.visible = False
    p.background_fill_alpha = 0.0
    p.outline_line_color = None

    # p.image_url(url=[
    #     rf'G:\GE\HubmapDemoDay_Dec14th_2020_Vessel_Nuclei_Segmentation_NucleiQuantification\output\dapi_Slide{str(input_id)}_region6_nucseg.png'],
    #     x=0, y=0, anchor="bottom_left")
    v_headers, v_columns = read_csv(vessel_file_path)
    for i in range(0, len(v_headers)):
        v_columns[v_headers[i]] = [float(value) for value in v_columns[v_headers[i]]]
    v_columns['y'] = [float(value) for value in v_columns['y']]
    max_y = max(v_columns['y'])
    v_columns['y'] = [float(value) for value in v_columns['y']]

    data = dict()
    for header in v_headers:
        data[header] = v_columns[header]
    v_df = pd.DataFrame(data)

    p.circle(x='x', y='y', source=v_df, color='#00e0e0', size=1, alpha=0.7)

    n_headers, n_columns = read_csv(nuclei_file_path)
    for i in range(1, len(n_headers)):
        n_columns[n_headers[i]] = [float(value) for value in n_columns[n_headers[i]]]
    n_columns['y'] = [float(value) for value in n_columns['y']]
    n_columns['vy'] = [float(value) for value in n_columns['vy']]
    n_columns['alpha'] = [(float(value) + 200) / 800 for value in n_columns['distance']]
    # n_columns['color'] = ['#%02x%02x%02x' % (0, int(255 * value * 0.3 / 160), int(255 * (160 - value * 0.3) / 160))
    #                       for value in n_columns['distance']]
    n_columns['color'] = ['#828282' for value in n_columns['distance']]

    data = dict()
    for header in n_headers:
        data[header] = n_columns[header]
        data['alpha'] = n_columns['alpha']
        data['color'] = n_columns['color']
    n_df = pd.DataFrame(data)

    p.segment(x0='x', y0='y', x1='vx', source=n_df, y1='vy', color="ivory", alpha=0.4, line_width=1)
    circle = p.circle(x='x', y='y', source=n_df, color='color', alpha=0.5, size=2.5)
    circle2 = p.circle(x=[0,7454], y=[0,4711], color='red', alpha=1, size=10)

    g1_hover = HoverTool(renderers=[circle], tooltips=[('X', "@x"), ('Y', "@y"), ('distance', "@distance")])
    p.add_tools(g1_hover)

    # p.legend.location = "bottom_right"

    show(p)
