# imports
from opentrons import protocol_api
import csv
import math

# metadata
metadata = {
    "protocolName": "DNA Extraction and Purification from up to 10mg Tissue",
    "description": "After lysing samples, follows the directions as given in the Omega Bio-tek Mag-Bind® Blood & Tissue DNA HDQ 96 Kit.\nThis protocol requires the user to change some values in the code in order to specify which wells contain samples. Please see the protocol file for more information.",
    "author": "Reya Miller"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.22"}

# copy and paste from a spreadsheet or manually change values here to specify which wells contain samples
# IMPORTANT: ensure that one column is full before moving on to the next one
sample_wells_data = """
	1	2	3	4	5	6	7	8	9	10	11	12
A	TRUE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE
B	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE
C	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE
D	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE
E	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE
F	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE
G	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE
H	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE	FALSE
"""
sample_wells_data = sample_wells_data.replace('\t', ',')

def add_parameters(parameters: protocol_api.Parameters):
    parameters.add_str(
        variable_name="multi_starting_col",
        display_name="Multi starting column",
        description="The starting column for the 8-channel pipette tips (first tip rack in slot 4).",
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
    parameters.add_str(
        variable_name="single_starting_row",
        display_name="Single starting row",
        description="The starting row for the single-channel pipette tips (slot 7).",
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
        variable_name="single_starting_col",
        display_name="Single starting column",
        description="The starting column for the single-channel pipette tips (slot 7).",
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

# the actual protocol
def run(protocol: protocol_api.ProtocolContext):
    csv_wells_data = sample_wells_data.splitlines()[1:]
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
    
    cols = math.ceil(len(selected_wells) / 8)
    
    sample_wells = []
    for i in range(cols):
        start_index = 8 * i
        if i == cols-1:
            sample_wells.insert(i, selected_wells[start_index:])
        else:
            sample_wells.insert(i, selected_wells[start_index:start_index+8])
    
    sample_plate = protocol.load_labware("greinerbioonegmbh_96_wellplate_2000ul", 6)
    sample = protocol.define_liquid(
        name="Sample",
        display_color="#0DFF00"
    )
    sample_plate.load_liquid(
        wells=selected_wells,
        volume=10,
        liquid=sample
    )
    
    reservoir_1 = protocol.load_labware("nest_12_reservoir_15ml", 3)
    al_buffer = protocol.define_liquid(
        name="AL Buffer",
        display_color="#E6DD5F"
    )
    reservoir_1.load_liquid(
        wells=["A1", "A2", "A3", "A4"],
        volume=10000,
        liquid=al_buffer
    )
    binding_buffer = protocol.define_liquid(
        name="HDQ Binding Buffer",
        display_color="#F58880"
    )
    reservoir_1.load_liquid(
        wells=["A5", "A6", "A7", "A8"],
        volume=15000,
        liquid=binding_buffer
    )
    vhb_buffer = protocol.define_liquid(
        name="VHB Buffer",
        display_color="#A973E6"
    )
    reservoir_1.load_liquid(
        wells=["A9", "A10", "A11", "A12"],
        volume=15000,
        liquid=vhb_buffer
    )
    
    reservoir_2 = protocol.load_labware("nest_1_reservoir_195ml", 2)
    spm_buffer = protocol.define_liquid(
        name="SPM Buffer",
        display_color="#4D7CE3"
    )
    reservoir_2.load_liquid(
        wells=["A1"],
        volume=1000,
        liquid=spm_buffer
    )
    
    reservoir_3 = protocol.load_labware("nest_1_reservoir_195ml", 1)
    elution_buffer = protocol.define_liquid(
        name="Elution Buffer",
        display_color="#F36CBF"
    )
    reservoir_3.load_liquid(
        wells=["A1"],
        volume=1000,
        liquid=elution_buffer
    )
    
    liquid_waste = protocol.load_labware("nest_1_reservoir_195ml", 9)
    
    tips_1 = protocol.load_labware("opentrons_96_tiprack_300ul", 4)
    tips_2 = protocol.load_labware("opentrons_96_tiprack_300ul", 5)
    tips_3 = protocol.load_labware("opentrons_96_tiprack_300ul", 7)
    right_pipette = protocol.load_instrument("p300_multi_gen2", "right", tip_racks=[tips_2, tips_3])
    right_pipette.starting_tip = tips_2["A" + protocol.params.multi_starting_col]
    left_pipette = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[tips_1])
    left_pipette.starting_tip = tips_1[protocol.params.single_starting_row + protocol.params.single_starting_col]
    
    magnetic_block = protocol.load_labware("96well_plate_2000ul_on_magnet_plate", protocol_api.OFF_DECK)
    dna_plate = protocol.load_labware("thermofast_96_wellplate_200ul", 8)
    
    def add_and_mix(vol: float, source: list[protocol_api.Well]):
        """
        Transfers the specified volume of liquid from the specified source to the sample plate and mixes.
        
        :param vol: The volume to be transferred, in µl.
        :param source: A list of wells containing the liquid to be aspirated. `add_and_mix` automatically calculates the index of the source to access.
        """
        for i in range(cols):
            src = source[i // (12 // len(source))]
            if i == cols-1:
                for well in sample_wells[i]:
                    left_pipette.transfer(volume=vol, source=src, dest=sample_plate[well], blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(10, 250))
            else:
                loc = "A" + str(i+1)
                right_pipette.transfer(volume=vol, source=src, dest=loc, blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(10, 250))
    
    def aspirate_supernatant(num_aspirations: int):
        """
        Aspirates and discards the supernatant after the Mag-Bind Particles have been cleared from the solution.
        
        :param num_aspirations: The number of times to aspirate the supernatant from any one well.
        """
        for i in range(cols):
            if i == cols-1:
                for well in sample_wells[i]:
                    left_pipette.pick_up_tip()
                    for j in range(num_aspirations):
                        left_pipette.aspirate(location=magnetic_block[well].bottom(z=-1), volume=250)
                        left_pipette.dispense(location=liquid_waste["A1"].bottom(z=5))
                    left_pipette.drop_tip()
            else:
                loc = "A" + str(i+1)
                right_pipette.pick_up_tip()
                for j in range(num_aspirations):
                    right_pipette.aspirate(location=magnetic_block[loc].bottom(z=-1), volume=250)
                    right_pipette.dispense(location=liquid_waste["A1"].bottom(z=5))
                right_pipette.drop_tip()
    
    # add 230µL AL Buffer
    # mix (pipette up and down 20x)
    add_and_mix(230, [reservoir_1["A1"], reservoir_1["A2"], reservoir_1["A3"], reservoir_1["A4"]])
    
    # add 320µL Binding Buffer diluted with 100% isopropanol
    src = [reservoir_1["A5"], reservoir_1["A6"], reservoir_1["A7"], reservoir_1["A8"]]
    for i in range(cols):
        if i == cols-1:
            for well in sample_wells[i]:
                left_pipette.transfer(volume=320, source=src[i//(12//len(src))], dest=sample_plate[well], blow_out=True, blowout_location="destination well", new_tip="always")
        else:
            loc = "A" + str(i+1)
            right_pipette.transfer(volume=320, source=src[i//(12//len(src))], dest=sample_plate[loc], blow_out=True, blowout_location="destination well", new_tip="always")
    # pause to manually add binding beads
    protocol.pause("Add binding beads.")
    # mix
    for i in range(cols):
        if i == cols-1:
            for well in sample_wells[i]:
                left_pipette.pick_up_tip()
                left_pipette.mix(repetitions=20, volume=250, location=sample_plate[well])
                left_pipette.drop_tip()
        else:
            loc = "A" + str(i+1)
            right_pipette.pick_up_tip()
            right_pipette.mix(repetitions=20, volume=250, location=sample_plate[loc])
    
    # place plate on magnetic separation device
    protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(magnetic_block, new_location="6")
    # let sit until the Mag-Bind Particles are completely cleared from solution
    protocol.delay(minutes=1)
    
    # aspirate and discard the cleared supernatant
    aspirate_supernatant(4)
    
    # remove plate from magnetic separation device
    protocol.move_labware(magnetic_block, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(sample_plate, new_location="6")
    
    # steps 8-10 of the Quick Guide
    def vhb_buffer():
        # add 600µL VHB Buffer diluted with 100% ethanol
        add_and_mix(600, [reservoir_1["A9"], reservoir_1["A10"], reservoir_1["A11"], reservoir_1["A12"]])
        
        # place plate on magnetic separation device
        protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
        protocol.move_labware(magnetic_block, new_location="6")
        # let sit until the Mag-Bind Particles are completely cleared from solution
        protocol.delay(minutes=1)
    
        # aspirate and discard the cleared supernatant
        aspirate_supernatant(4)
        
        # remove plate from magnetic separation device
        protocol.move_labware(magnetic_block, new_location=protocol_api.OFF_DECK)
        protocol.move_labware(sample_plate, new_location="6")
    
    # steps 8-11
    for i in range(2):
        vhb_buffer()
    
    # add 600µL SPM Buffer diluted with 100% ethanol
    # mix
    add_and_mix(600, [reservoir_2["A1"]])
    
    # place plate on magnetic separation device
    protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(magnetic_block, new_location="6")
    # let sit until the Mag-Bind Particles are completely cleared from solution
    protocol.delay(minutes=1)
    
    # aspirate and discard the cleared supernatant
    aspirate_supernatant(4)
    
    # leave the plate on the magnetic separation device and wait 1 minute
    protocol.delay(minutes=1)
    
    # remove residual liquid
    aspirate_supernatant(2)
    
    # dry the Mag-Bind Particles HDQ for an additional 10 minutes
    protocol.delay(minutes=10)
    
    # remove plate from magnetic separation device
    protocol.move_labware(magnetic_block, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(sample_plate, new_location="6")
    
    # add 110µL Elution Buffer
    add_and_mix(110, [reservoir_3["A1"]])
    
    # place plate on magnetic separation device
    protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(magnetic_block, new_location="6")
    # let sit until the Mag-Bind Particles are completely cleared from solution
    protocol.delay(minutes=1)
    
    # transfer the cleared supernatant containing purified DNA to a 96-well microplate
    for i in range(cols):
        if i == cols-1:
            for well in sample_wells[i]:
                left_pipette.transfer(100, source=magnetic_block[well], dest=dna_plate[well])
        else:
            loc = "A" + str(i+1)
            right_pipette.transfer(100, source=magnetic_block[loc], dest=dna_plate[loc])