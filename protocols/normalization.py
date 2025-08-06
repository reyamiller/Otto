# imports
from opentrons import protocol_api
import csv

# metadata
metadata = {
    "protocolName": "Normalization",
    "description": "Normalizes the amount of a material in the wells of a plate.\nThis protocol requires the user to change some values in the code. Please see the protocol file for more information.",
    "author": "Reya Miller"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.22"}

# copy and paste from a spreadsheet (see https://docs.google.com/spreadsheets/d/1K7OXYfy0i2oJgIokcdIegjBVeeBMqR_-SODV961FI2k/edit?usp=sharing for a template)
water_volume_data = """
	1	2	3	4	5	6	7	8	9	10	11	12
A	12.4	11.6										
B	11.7	10.7										
C	12.2	10.5										
D	12.0											
E	12.4											
F	12.3											
G	12.4											
H	12.2											
"""
water_volume_data = water_volume_data.replace('\t', ',')

dna_volume_data = """
	1	2	3	4	5	6	7	8	9	10	11	12
A	0.6	1.4										
B	1.3	2.4										
C	0.8	2.5										
D	1.0											
E	0.6											
F	0.7											
G	0.6											
H	0.9											
"""
dna_volume_data = dna_volume_data.replace('\t', ',')

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
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 5)
    water_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", 3)
    water = protocol.define_liquid(
        name="Water",
        description="The liquid being used to dilute the sample.",
        display_color="#0051FF"
    )
    tube_rack.load_liquid(
        wells=["A1"],
        volume=150,
        liquid=water
    )
    
    csv_water_volume = water_volume_data.splitlines()[1:]
    water_volume_reader = csv.DictReader(csv_water_volume)
    wells_used = []
    water_volumes = {}
    for row in water_volume_reader:
        r = row[""]
        for i in range(1,13):
            new_key = r + (str) (i)
            row[new_key] = row.pop(f'{i}')
        del row[""]
        keys = list(row.keys())
        not_blank = []
        for key in keys:
            if row[key] != '':
                not_blank.append(key)
        wells_used.extend(not_blank)
        water_volumes |= row
    
    water_plate.load_liquid(
        wells=wells_used,
        volume=150,
        liquid=water
    )
    
    dna_plate = protocol.load_labware("opentrons_96_wellplate_200ul_pcr_full_skirt", 2)
    
    csv_dna_volume = dna_volume_data.splitlines()[1:]
    dna_volume_reader = csv.DictReader(csv_dna_volume)
    dna_volumes = {}
    for row in dna_volume_reader:
        r = row[""]
        for i in range(1,13):
            new_key = r + (str) (i)
            row[new_key] = row.pop(f'{i}')
        del row[""]
        dna_volumes |= row
    
    dna = protocol.define_liquid(
        name="DNA",
        description="The DNA samples.",
        display_color="#FD9381"
    )
    dna_plate.load_liquid(
        wells=wells_used,
        volume=0,
        liquid=dna
    )
    
    tips = protocol.load_labware("opentrons_96_tiprack_20ul", 6)
    left_pipette = protocol.load_instrument("p20_single_gen2", "left", tip_racks=[tips])
    left_pipette.starting_tip = tips[protocol.params.starting_tip_row + protocol.params.starting_tip_col]
    
    # add the specified volumes of water to the plate
    left_pipette.pick_up_tip()
    for well in wells_used:
        left_pipette.transfer((float) (water_volumes[well]), tube_rack["A1"], water_plate[well], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.drop_tip()
    
    # add the specified volumes of DNA to the plate with water
    for well in wells_used:
        left_pipette.transfer((float) (dna_volumes[well]), dna_plate[well], water_plate[well], blow_out=True, blowout_location="destination well")