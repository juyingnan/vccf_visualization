import os
import sys
import pandas as pd
import numpy as np
import ast
from tqdm import tqdm
from skimage.draw import polygon_perimeter, line
from vitessce.data_utils import multiplex_img_to_ome_tiff
from skimage.morphology import disk, dilation


def generate_cell_mask(mask, value, vertices, is_line=False):
    if is_line:
        rr, cc = line(int(vertices[0][1]), int(vertices[0][0]),
                      int(vertices[1][1]), int(vertices[1][0]))
        mask[rr, cc] = value
    else:
        rr, cc = polygon_perimeter([v[1] for v in vertices], [v[0] for v in vertices])
        mask[rr, cc] = value


def convert_str_to_list(row):
    return [list(i) for i in ast.literal_eval(row)]


def generate_mask_arr(type_list, table, mask_shape, is_line=False):
    # initialize an empty mask for each cell type
    masks = {cell_type: np.zeros(mask_shape, dtype=np.uint8) for cell_type in type_list}
    for index, row in tqdm(table.iterrows(), total=len(table), desc='Processing rows'):
        generate_cell_mask(masks[row['type']], color_dict[row['type']], row['vertices'], is_line=is_line)
    # Create an ordered list of masks
    mask_list = [masks[cell_type] for cell_type in type_list]
    # Stack masks into a 3D array. The new array has shape (n, m, len(cell_types)),
    # where n and m are the dimensions of the original masks.

    # make the line thicker by dilation
    for i in range(len(mask_list)):
        selem = disk(1)
        mask_list[i] = dilation(mask_list[i], selem)

    bitmask_stack = np.dstack(mask_list)
    return bitmask_stack


# Default region_index
region_index = '00a67c839'
scale = 1

# Check if at least one command-line argument is given
if len(sys.argv) >= 2:
    # Use the given argument as region_index
    region_index = sys.argv[1]
if len(sys.argv) >= 3:
    # Use the given argument as scale
    scale = float(sys.argv[2])

# Construct the path to the nuclei file
nuclei_root_path = rf'G:\HuBMAP\Vignette_GFTU_kidney'
nuclei_file_name = f'{region_index}_all_coordinates.csv'
nuclei_file_path = os.path.join(nuclei_root_path, nuclei_file_name)

cell_table = pd.read_csv(nuclei_file_path)

# convert the vertices column from string to list
cell_table['vertices'] = cell_table['vertices'].apply(convert_str_to_list)
cell_table['vertices'] = cell_table['vertices'].apply(lambda x: [[int(i[0] * scale), int(i[1] * scale)] for i in x])

cell_types = ["Ground Truth", "Tom", "Gleb", "Whats goin on", "Deeplive.exe", "Deepflash2"]
color_dict = {"Ground Truth": 1, "Tom": 2, "Gleb": 3, "Whats goin on": 4, "Deeplive.exe": 5, "Deepflash2": 6}

# determine the shape of your canvas
# height should be the max value of cell_table['vertices']
# width should be the max value of cell_table['vertices']
height = max([max([v[1] for v in vertices]) for vertices in cell_table['vertices']]) + 30
width = max([max([v[0] for v in vertices]) for vertices in cell_table['vertices']]) + 30
# height and width from command-line arguments
if len(sys.argv) >= 4:
    width = int(sys.argv[3])
if len(sys.argv) >= 5:
    height = int(sys.argv[4])
shape = (height, width)
shape = tuple(map(int, shape))

print("Generating cell masks...")
cell_mask_stack = generate_mask_arr(cell_types, cell_table, shape)

# Ensure the axes are in the CYX order by transposing the array
bitmask_arr = np.transpose(cell_mask_stack, (2, 0, 1))

# Save the masks
print("Saving masks...")
multiplex_img_to_ome_tiff(bitmask_arr, cell_types, nuclei_file_path.replace('csv', 'ome.tif'), axes="CYX")
