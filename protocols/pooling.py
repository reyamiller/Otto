# imports
from opentrons import protocol_api
import csv

# metadata
metadata = {
    "protocolName": "Pooling",
    "description": "Pools liquid from user-specified wells into a single tube.\nThis protocol requires the user to change some values in the code. Please see the protocol file for more information.",
    "author": "Reya Miller"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.22"}

# copy and paste from a spreadsheet or manually change the values here to specify wells to pool from
# see https://docs.google.com/spreadsheets/d/1xxteNo-ELEXkcBVYScM2-33683Ea6CttAoCTvS-vjFQ/edit?usp=sharing for template
selected_wells_data = """
	1	2	3	4	5	6	7	8	9	10	11	12
A	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	FALSE
B	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	FALSE
C	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	FALSE
D	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	FALSE
E	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	FALSE
F	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	FALSE
G	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	FALSE
H	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	TRUE	FALSE	FALSE
"""
selected_wells_data = selected_wells_data.replace('\t', ',')

def add_parameters(parameters: protocol_api.Parameters):
    # if necessary, tell the robot the location of the first available tip on the tip rack
    parameters.add_str(
        variable_name="starting_tip_row",
        display_name="Starting tip row",
        description="The row of the tip to start with on the tip rack.",
        choices=[
            {"display_name": "A", "value": "A"},
            {"display_name": "B", "value": "B"},
            {"display_name": "C", "value": "C"},
            {"display_name": "D", "value": "D"},
            {"display_name": "E", "value": "E"},
            {"display_name": "F", "value": "F"},
            {"display_name": "G", "value": "G"},
            {"display_name": "H", "value": "H"}
        ],
        default="A"
    )
    parameters.add_str(
        variable_name="starting_tip_col",
        display_name="Starting tip column",
        description="The column of the tip to start with on the tip rack.",
        choices=[
            {"display_name": "1", "value": "1"},
            {"display_name": "2", "value": "2"},
            {"display_name": "3", "value": "3"},
            {"display_name": "4", "value": "4"},
            {"display_name": "5", "value": "5"},
            {"display_name": "6", "value": "6"},
            {"display_name": "7", "value": "7"},
            {"display_name": "8", "value": "8"},
            {"display_name": "9", "value": "9"},
            {"display_name": "10", "value": "10"},
            {"display_name": "11", "value": "11"},
            {"display_name": "12", "value": "12"}
        ],
        default="1"
    )

def run(protocol: protocol_api.ProtocolContext):
    # read the selected wells data to determine which wells to pool from
    csv_wells_data = selected_wells_data.splitlines()[1:]
    wells_data_reader = csv.DictReader(csv_wells_data)
    selected_wells = []
    for row in wells_data_reader:
        r = row[""]
        for i in range(1,13):
            new_key = r + str(i)
            row[new_key] = row.pop(f'{i}')
        del row[""]
        keys = list(row.keys())
        true_keys = []
        for key in keys:
            if row[key] == "TRUE":
                true_keys.append(key)
        selected_wells.extend(true_keys)
    
    # define the tube rack and indicate where the tube of water is
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 3)
    water = protocol.define_liquid(
        name="Water",
        description="The liquid being used to dilute the samples.",
        display_color="#0051FF"
    )
    tube_rack.load_liquid(
        wells=["A1"],
        volume=150,
        liquid=water
    )
    
    # define the DNA plate, which should hold DNA in the wells specified by selected_wells
    dna_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", 2)
    dna = protocol.define_liquid(
        name="DNA",
        description="The DNA samples.",
        display_color="#FD9381"
    )
    dna_plate.load_liquid(
        wells=selected_wells,
        volume=100,
        liquid=dna
    )
    
    # define pipette and tip rack
    tips_1 = protocol.load_labware("opentrons_96_tiprack_20ul", 6)
    tips_2 = protocol.load_labware("opentrons_96_tiprack_20ul", 5)
    tips_3 = protocol.load_labware("opentrons_96_tiprack_20ul", 9)
    left_pipette = protocol.load_instrument("p20_single_gen2", "left", tip_racks=[tips_1, tips_2, tips_3])
    left_pipette.starting_tip = tips_1[protocol.params.starting_tip_row + protocol.params.starting_tip_col]
    
    # add x µl of water to the eppendorf tube, where x = (100 - number of samples)
    left_pipette.transfer(volume=(100 - len(selected_wells)), source=tube_rack["A1"], dest=tube_rack["A2"], blow_out=True, blowout_location="destination well")
    
    # pool the DNA from the selected wells of the plate into the eppendorf tube with water
    for well in selected_wells:
        left_pipette.transfer(volume=1, source=dna_plate[well], dest=tube_rack["A2"], blow_out=True, blowout_location="destination well")