def try_parse_int(s, base=10, val=None):
    try:
        return int(s, base)
    except ValueError:
        return val


target_root_path = r"G:\GE\skin_12_data"
cell_file_path = r"C:\Users\bunny\Desktop\ge_temp\Centroids_Oct_29_21.csv"

# bv_file = open(bv_file_path, 'r')
# bv_lines = bv_file.readlines()

cell_file = open(cell_file_path, 'r')
cell_lines = cell_file.readlines()

cells = {}
type_abr = {
    # "_TRegulatory": "T-Reg",
    "Macrophage": "CD68",
    "CD68": "CD68",
    "TKiller": "T-Killer",
    "TRegulator": "T-Reg",
    "THelper": "T-Helper",
    "P53": "P53",
    "KI67": "KI67",
    "DDB2": "DDB2",
    "Skin mask": "Skin",
    "Blood Vessels": "CD31",
    "CD31": "CD31",
}
headline = "ID,X,Y,Z,cell_type\n"
skin_id = 0

current_region = ""
current_type = ""
for line_content in cell_lines:
    line = line_content.strip().rstrip(",")
    if len(line) == 0:
        continue
    if line.startswith("Region"):
        if line not in cells:
            cells[line] = {}
        current_region = line
        current_type = ""
        continue
    elif line.strip() in type_abr:
        assert current_region != ""
        current_type = type_abr[line]
        cells[current_region][current_type] = []
    elif line.startswith("Label") or line.startswith('x1'):
        continue
    else:
        assert current_region != ""
        assert current_type != ""
        if current_type in type_abr.values():
            if current_type == type_abr["Skin mask"]:
                cells[current_region][current_type].append(f"{skin_id},{line},{current_type}")
                skin_id += 1
            else:
                cells[current_region][current_type].append(f"{line},{current_type}")
        else:
            print(f"{current_region}, {current_type} not in the type dict")

# temp additional data
import os
from os import walk

temp_files = []
temp_names = []
temp_root_path = r"C:\Users\bunny\Desktop\ge_temp\temp_data"
for (dirpath, dirnames, filenames) in walk(temp_root_path):
    temp_files.extend([os.path.join(dirpath, filename) for filename in filenames])
    temp_names.extend([filename for filename in filenames])

# z_max = 0
for i in range(len(temp_files)):
    name = temp_names[i].split('_')[0]
    temp_file_path = temp_files[i]
    current_region = ""
    current_type = type_abr[name]
    cell_file = open(temp_file_path, 'r')
    cell_lines = cell_file.readlines()
    for line_content in cell_lines:
        line = line_content.strip().rstrip(",")
        if len(line) == 0:
            continue
        if line.startswith("Region"):
            if line not in cells:
                cells[line] = {}
            current_region = line
            cells[current_region][current_type] = []
            print(f"refreshing {current_type} - {current_region}")
        else:
            assert current_region != ""
            assert current_type != ""
            if current_type in type_abr.values():
                cells[current_region][current_type].append(f"{line},{current_type}")
                # test z
                # z = float(line.split(',')[3])
                # z_max = max(z, z_max)
            else:
                print(f"{current_region}, {current_type} not in the type dict")
    print("-----------------")
# print(z_max)

# write csv
for region in cells:
    print(region, ":")
    for cell_type in cells[region]:
        print(f"\t{cell_type}: {len(cells[region][cell_type])}")
    region_id = try_parse_int(region[6:])
    if region_id is None:
        print(f"Region name {region} fails to parse")
        break
    target_file_path = target_root_path + rf"\region_{region_id}\centroids.csv"
    csv_file = open(target_file_path, "w")
    csv_file.write(headline)
    for cell_type in cells[region]:
        for line in cells[region][cell_type]:
            csv_file.write(line + "\n")
    csv_file.close()

# format output for excel
for region in cells:
    print(region, "\t", end='')
    for cell_type in ["Macrophage",
                      "TKiller",
                      "TRegulator",
                      "THelper",
                      "P53",
                      "KI67",
                      "DDB2", ]:
        print(f"{len(cells[region][type_abr[cell_type]])}\t", end='')
    print()

layer_stat = True
if layer_stat:
    for region in cells:
        print(region)
        for layer in range(24):
            print(f"Layer {layer}", "\t", end='')
            for cell_type in ["Macrophage",
                              "TKiller",
                              "TRegulator",
                              "THelper",
                              "P53",
                              "KI67",
                              "DDB2", ]:
                result = 0
                for item in cells[region][type_abr[cell_type]]:
                    z = round(float(item.split(',')[3]))
                    if z == layer:
                        result += 1
                print(f"{result}\t", end='')
            print()
        print()
