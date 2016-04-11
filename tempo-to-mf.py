# Tempo Automation JSON (from Upverter) to
# Copyright 2016 Severin Ibarluzea

import sys

if len(sys.argv) != 2 and len(sys.argv) != 3:
    print("USAGE: tempo-to-mf <tempo.json> [component key file]")
    sys.exit()

import json

tempo = json.load(open(sys.argv[1]))

# ----------------------------
# GENERATE/READ KEY FILE
# ----------------------------

comp_keys = None
if len(sys.argv) == 3:
    comp_keys = json.load(open(sys.argv[2]))
else:
    print("You did not specify a key file, beginning generation...")
    print("You will be asked for the MPN for each component type in the file")
    comp_keys = {}
    for comp_id in tempo["components"]:
        print("\n")
        comp = tempo["components"][comp_id]
        print("Component {}".format(comp_id))
        print("Manufacturer: {}".format(comp["Manufacturer"]))
        mf_name = raw_input("Macrofab MPN (\"SKIP\" to skip):")
        if mf_name.lower().strip() == "skip": continue
        smd = raw_input("SMD (S) or Throughole (T)? [SMD]:")
        value = raw_input("Value:")
        footprint = raw_input("Footprint (e.g. 0403):")
        comp_keys[comp_id] = {
            "MPN": mf_name,
            "Type": smd == "T" and 2 or 1,
            "Value": value,
            "Footprint": footprint
        }
    print("\nWriting the key file to \"keyfile.json\"")
    json.dump(comp_keys, open("keyfile.json",'w'))


# ----------------------------
# GENERATE XYRS FILE
# ----------------------------

lines = [
    ["#Designator","X-Loc","Y-Loc","Rotation","Side","Type","X-Size","Y-Size","Value","Footprint","Populate","MPN"]
]
for placement in tempo["placements"]:
    if placement["ComponentId"] not in comp_keys:
        continue
    cinfo = comp_keys[placement["ComponentId"]]
    lines.append([
        placement['DesignName'], # Designator
        placement['BoardLocationX'] * 1000, #X-Loc
        placement['BoardLocationY'] * 1000, #Y-Loc
        placement['Rotation'], # Rotation
        placement['Layer'], # Side
        cinfo['Type'], # Type
        0, 0, # X-Size, Y-Size
        cinfo['Value'], # Value
        cinfo['Footprint'], # Footprint
        1, # Populate (yes)
        cinfo["MPN"] # MPN
    ])

# ----------------------------
# WRITE OUTPUT FILE
# ----------------------------

print("Writing to output file \"output.XYRS\"")
open("output.XYRS",'w').write("\n".join(["\t".join(map(str, l)) for l in lines]))
