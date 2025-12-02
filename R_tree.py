#GAVRIILIA-MICHAILIA POLYCHRONIOU,5084
import sys
import json

def read_coords(file1):
    file_1 = open(file1, 'r')

    coords = []

    for line in file_1:
        coord = tuple(map(float,line.strip().split(',')))
        coords.append(coord)

    file_1.close()

    return coords

def read_offsets(file2):

    file_2 = open(file2, 'r')

    offsets = []

    for line in file_2:
        id_str,start,end = line.strip().split(',')
        offset = (int(id_str),int(start),int(end))
        offsets.append(offset)

    file_2.close()

    return offsets
    
def minimum_bounding_rectangle(coords):
    
    x_coords = [x for x,y in coords]  #all x
    y_coords = [y for x,y in coords]  #all y

    x_min = min(x_coords)
    x_max = max(x_coords)
    y_min = min(y_coords)
    y_max = max(y_coords)
    
    return [x_min,x_max,y_min,y_max] #returns the mbr list

def polygons_with_mbr(file1,file2):
    coords = read_coords(file1)
    offsets = read_offsets(file2)

    polygons_mbr_lst = []

    for id_object, start, end in offsets:
        polygon = coords[start : end + 1]
        mbr = minimum_bounding_rectangle(polygon)
        polygons_mbr_lst.append({'ID':id_object, 'MBR':mbr})

    return polygons_mbr_lst

_DIVISORS = [180.0 / 2 ** n for n in range(32)]

def __part1by1_32(n):
    n &= 0x0000ffff                  # base10: 65535,      binary: 1111111111111111,                 len: 16
    n = (n | (n << 8))  & 0x00FF00FF # base10: 16711935,   binary: 111111110000000011111111,         len: 24
    n = (n | (n << 4))  & 0x0F0F0F0F # base10: 252645135,  binary: 1111000011110000111100001111,     len: 28
    n = (n | (n << 2))  & 0x33333333 # base10: 858993459,  binary: 110011001100110011001100110011,   len: 30
    n = (n | (n << 1))  & 0x55555555 # base10: 1431655765, binary: 1010101010101010101010101010101,  len: 31

    return n

def interleave_latlng(lat, lng):
    if not isinstance(lat, float) or not isinstance(lng, float):
        print('Usage: interleave_latlng(float, float)')
        raise ValueError("Supplied arguments must be of type float!")

    if (lng > 180):
        x = (lng % 180) + 180.0
    elif (lng < -180):
        x = (-((-lng) % 180)) + 180.0
    else:
        x = lng + 180.0
    if (lat > 90):
        y = (lat % 90) + 90.0
    elif (lat < -90):
        y = (-((-lat) % 90)) + 90.0
    else:
        y = lat + 90.0

    morton_code = ""
    for dx in _DIVISORS:
        digit = 0
        if (y >= dx):
            digit |= 2
            y -= dx
        if (x >= dx):
            digit |= 1
            x -= dx
        morton_code += str(digit)

    return morton_code

def polygons_with_zorder (file1,file2):
    coords = read_coords(file1)
    offset_data = read_offsets(file2)

    polygon_objects = []

    for polygon_id,start,end in offset_data:
        polygon = coords[start : end + 1]
        mbr = minimum_bounding_rectangle(polygon)

        center_x = (mbr[0] + mbr[1]) / 2 #compute center of MBR - x
        center_y = (mbr[2] + mbr[3]) / 2 #compute center of MBR - y

        z_order = interleave_latlng(center_y,center_x)

        polygon_objects.append({'ID':polygon_id, 'MBR':mbr, 'z_order':z_order})

    polygon_objects.sort(key=get_zorder)

    return polygon_objects

def get_zorder(obj):
    zorder = obj['z_order']
    return zorder

def new_mbrs(mbr_lst):
    x_min = [mbr[0] for mbr in mbr_lst]
    x_max = [mbr[1] for mbr in mbr_lst]

    y_min = [mbr[2] for mbr in mbr_lst]
    y_max = [mbr[3] for mbr in mbr_lst]

    new_x_min = min(x_min)
    new_x_max = max(x_max)

    new_y_min = min(y_min)
    new_y_max = max(y_max)
            
    return [new_x_min,new_x_max,new_y_min,new_y_max]

node_capacity = 20
node_min_registers = 8

def create_nodes(objects, is_leaf, next_node_id):
    nodes_lst = [] #store nodes
    i = 0
    while i < len(objects):
        end = i + node_capacity
        
        if (len(objects) - end < node_min_registers and len(objects) - i > node_capacity):
            end = len(objects) - node_min_registers
            
        group = objects[i:end]
        
        entries = []
        
        for item in group:
            entries.append([item['ID'], item['MBR']])
            
        total_mbrs = [entry[1] for entry in entries]  
        total_node_mbr = new_mbrs(total_mbrs)  #total mbr of a node
        
        node = {'nonleaf': int(not is_leaf),  #dictionary with all information for a node
                'node_id': next_node_id,
                'entries': entries,
                'MBR': total_node_mbr }
        
        nodes_lst.append(node)
        next_node_id += 1
        i = end
        
    return nodes_lst, next_node_id

def make_rtree(entries):
    next_node_id = 0
    
    leaf_nodes, next_node_id = create_nodes(entries, is_leaf = True, next_node_id = next_node_id)

    rtree_levels = [leaf_nodes] #add level of leafs

    current_level = leaf_nodes
    
    while (len(current_level) > 1):
        parent_entries = []

        for node in current_level:
            entry = {'ID': node['node_id'],
                     'MBR': node['MBR']}
            parent_entries.append(entry)

        current_level, next_node_id = create_nodes(parent_entries, is_leaf = False, next_node_id = next_node_id)
        rtree_levels.append(current_level)
        
    return rtree_levels[::-1]  

def write_rtree_to_file(tree_levels):
    file_3 = open('Rtree.txt','w')

    all_nodes = []
    for level in tree_levels:
        for node in level:
            all_nodes.append(node)
            
    all_nodes.sort(key = get_node_id)

    for node in all_nodes:
        line = [node['nonleaf'], node['node_id'], node['entries']]
        file_3.write(json.dumps(line) + '\n')
        
    file_3.close()

def get_node_id(node):
    node_id = node['node_id']
    return node_id

coords = sys.argv[1]
offsets = sys.argv[2]

polygons = polygons_with_zorder(coords, offsets)
tree_levels = make_rtree(polygons)

for level, nodes in enumerate(reversed(tree_levels)):
    if (len(nodes) > 1):
        plural = "nodes"
    else:
        "node"
    print(str(len(nodes)) + " " + plural + " at level " + str(level))

write_rtree_to_file(tree_levels)



    
        
        

