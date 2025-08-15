# imports
from opentrons import protocol_api
import csv
import math

# metadata
metadata = {
    "protocolName": "Total RNA Purification with Zymo Quick-RNA™ MagBinding Beads",
    "description": "Follows the steps given for part III of the Zymo Research Quick-RNA™ MagBead protocol.\nThis protocol requires the user to change some values in the code in order to specify which wells contain samples. Please see the protocol file for more information.",
    "author": "Reya Miller"
}

# requirements
requirements = {"robotType": "OT-2", "apiLevel": "2.22"}

# copy and paste from a spreadsheet or manually change values here to specify which wells contain samples
# IMPORTANT: ensure that one column is fully filled before moving on to the next one
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
        description="The starting column for the 8-channel pipette tips (slot 5).",
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
        description="The starting row for the single-channel pipette tips (slot 4).",
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
        description="The starting column for the single-channel pipette tips (slot 4).",
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
    # get all the necessary information about which wells contain samples
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
    
    # define liquids and labware
    sample_plate = protocol.load_labware("greinerbioonegmbh_96_wellplate_2000ul", 6)
    sample = protocol.define_liquid(
        name="Sample",
        display_color="#7FC97F"
    )
    sample_plate.load_liquid(
        wells=selected_wells,
        volume=200,
        liquid=sample
    )
    
    reservoir_1 = protocol.load_labware("nest_12_reservoir_15ml", 3)
    rna_lysis_buffer = protocol.define_liquid(
        name="RNA Lysis Buffer",
        display_color="#60D9E9"
    )
    reservoir_1.load_liquid(
        wells=[reservoir_1.wells()[0]],
        volume=500,
        liquid=rna_lysis_buffer
    )
    ethanol = protocol.define_liquid(
        name="Ethanol (95-100%)",
        display_color="#F781BF"
    )
    reservoir_1.load_liquid(
        wells=[reservoir_1.wells()[1]],
        volume=1000,
        liquid=ethanol
    )
    rna_prep_buffer = protocol.define_liquid(
        name="RNA Prep Buffer",
        display_color="#B687D3"
    )
    reservoir_1.load_liquid(
        wells=[reservoir_1.wells()[2]],
        volume=1000,
        liquid=rna_prep_buffer
    )
    dnase_rnase_free_water = protocol.define_liquid(
        name="DNase/RNase-Free Water",
        display_color="#99D6CB"
    )
    reservoir_1.load_liquid(
        wells=[reservoir_1.wells()[3]],
        volume=500,
        liquid=dnase_rnase_free_water
    )
    
    # reservoir_2 = protocol.load_labware("nest_12_reservoir_15ml", 3)
    wash_1 = protocol.define_liquid(
        name="Wash 1",
        display_color="#FDB462"
    )
    reservoir_1.load_liquid(
        wells=[reservoir_1.wells()[4]],
        volume=1000,
        liquid=wash_1
    )
    wash_2 = protocol.define_liquid(
        name="Wash 2",
        display_color="#FFED6F"
    )
    reservoir_1.load_liquid(
        wells=[reservoir_1.wells()[5]],
        volume=1000,
        liquid=wash_2
    )
    # reservoir_2.load_liquid(
    #     wells=reservoir_2.wells()[8:12],
    #     volume=1000,
    #     liquid=ethanol
    # )
    
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 2)
    dnase_i_reaction_mix = protocol.define_liquid(
        name="DNase I Reaction Mix",
        display_color="#E41A1C"
    )
    tube_rack.load_liquid(
        wells=["D6"],
        volume=500,
        liquid=dnase_i_reaction_mix
    )
    
    beads_plate = protocol.load_labware("thermofast_96_wellplate_200ul", 1)
    magbinding_beads = protocol.define_liquid(
        name="MagBinding Beads",
        display_color="#3F3F3F"
    )
    beads_plate.load_liquid(
        wells=selected_wells,
        volume=100,
        liquid=magbinding_beads
    )
    
    eluted_rna_plate = protocol.load_labware("thermofast_96_wellplate_200ul", 8)
    
    tips_1 = protocol.load_labware("opentrons_96_tiprack_300ul", 4)
    tips_2 = protocol.load_labware("opentrons_96_tiprack_300ul", 5)
    right_pipette = protocol.load_instrument("p300_multi_gen2", "right", tip_racks=[tips_2])
    right_pipette.starting_tip = tips_2["A" + protocol.params.multi_starting_col]
    left_pipette = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[tips_1, tips_2])
    left_pipette.starting_tip = tips_1[protocol.params.single_starting_row + protocol.params.single_starting_col]
    
    liquid_waste = protocol.load_labware("nest_1_reservoir_195ml", 9)
    magnetic_block = protocol.load_labware("96well_plate_2000ul_on_magnet_plate", protocol_api.OFF_DECK)
    
    def add_and_mix(vol: float, source: list[protocol_api.Well], mix_vol=200):
        """
        Transfers the specified volume of liquid from the specified source to the sample plate and mixes.
        
        :param vol: The volume to be transferred, in µl.
        :param source: A list of wells containing the liquid to be aspirated. `add_and_mix` automatically calculates the index of the source to access.
        :param mix_vol: The volume to be aspirated and dispensed when mixing.
        """
        for i in range(cols):
            src = source[i // (12 // len(source))]
            if i == cols-1:
                for well in sample_wells[i]:
                    left_pipette.transfer(volume=vol, source=src, dest=sample_plate[well], blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(50, mix_vol))
            else:
                loc = "A" + str(i+1)
                right_pipette.transfer(volume=vol, source=src, dest=sample_plate[loc], blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(50, mix_vol))
    
    def aspirate_supernatant(num_aspirations=3):
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
    
    def add_mix_pellet(vol: float, source: list[protocol_api.Well], mix_vol=200.0, num_aspirations=3, remove_magnet=True):
        """
        Calls `add_and_mix(vol, source)`, then transfers the beads to the magnetic stand
        and waits for the beads to pellet before discarding the cleared supernatant and
        then taking the sample plate off the magnetic stand.
        
        :param vol: The volume to be transfered, in µl.
        :param source: A list of wells containing the liquid to be aspirated. The index of the source to access is calculated automatically.
        :param mix_vol: The volume to be aspirated and dispensed when mixing.
        :param num_aspirations: The number of times to aspirate the supernatant from any one well.
        :param remove_magnet: Whether or not to remove the samples from the magnet plate at the end of the function.
        """
        add_and_mix(vol, source, mix_vol)
        protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
        protocol.move_labware(magnetic_block, new_location="6")
        protocol.delay(minutes=1)
        aspirate_supernatant(num_aspirations)
        if remove_magnet:
            protocol.move_labware(magnetic_block, new_location=protocol_api.OFF_DECK)
            protocol.move_labware(sample_plate, new_location="6")
    
    def mix_beads(pipette: protocol_api.InstrumentContext, well: protocol_api.Well):
        if pipette == left_pipette:
            height = 0
            for j in range(50):
                left_pipette.aspirate(volume=250, location=sample_plate[well].bottom(z=height))
                left_pipette.dispense(location=sample_plate[well].bottom(z=height))
                height += 2
        else:
            height = 0
            for j in range(50):
                right_pipette.aspirate(volume=250, location=sample_plate[well].bottom(z=height))
                right_pipette.dispense(location=sample_plate[well].bottom(z=height))
                height += 2
    
    # # 1. Add 200µl (1 volume) RNA Lysis Buffer to 200µL sample and mix well.
    add_and_mix(200, [reservoir_1.wells()[0]])
    
    # # 2. Add 400µl ethanol (95-100%) to the sample and mix well.
    add_and_mix(400, [reservoir_1.wells()[1]])
    
    # 3. Add 30µl MagBinding Beads and mix well for 20 minutes.
    for i in range(cols):
        if i == cols-1:
            for well in sample_wells[i]:
                left_pipette.pick_up_tip()
                left_pipette.mix(repetitions=5, volume=40, location=beads_plate[well])
                left_pipette.aspirate(volume=30, location=beads_plate[well])
                left_pipette.dispense(location=sample_plate[well])
                mix_beads(left_pipette, well)
                left_pipette.drop_tip()
        else:
            loc = "A" + str(i+1)
            right_pipette.pick_up_tip()
            right_pipette.mix(repetitions=5, volume=40, location=beads_plate[loc])
            right_pipette.aspirate(volume=30, location=beads_plate[loc])
            right_pipette.dispense(location=sample_plate[loc])
            mix_beads(right_pipette, loc)
            right_pipette.drop_tip()
    
    # 4. Transfer the plate/tube to the magnetic stand until beads have pelleted, then
    # aspirate and discard the cleared supernatant.
    protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(magnetic_block, new_location="6")
    protocol.delay(minutes=10) # wait for beads to pellet
    aspirate_supernatant(4) # aspirate and discard cleared supernatant
    # take sample plate off of magnetic block
    protocol.move_labware(magnetic_block, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(sample_plate, new_location="6")
    
    # 5. Add 500µl MagBead DNA/RNA Wash 1 and mix well. Pellet the beads and discard
    # the supernatant.
    add_mix_pellet(500, [reservoir_1.wells()[4]])
    
    # 6. Add 500µl MagBead DNA/RNA Wash 2 and mix well. Pellet the beads and discard
    # the supernatant.
    add_mix_pellet(500, [reservoir_1.wells()[5]])
    
    # 7. Add 500µl ethanol (95-100%) and mix well. Pellet the beads and discard the
    # supernatant.
    add_mix_pellet(500, [reservoir_1.wells()[1]])
    
    # 8. Repeat step 7.
    add_mix_pellet(500, [reservoir_1.wells()[1]])
    
    # 9. DNase I treatment
    # (D1) Add 50µl DNase I Reaction Mix and mix gently for 10 minutes.
    add_and_mix(50, [tube_rack["D6"]], 50)
    # (D2) Add 500µl RNA Prep Buffer and mix well for 10 minutes. Pellet the beads and discard the supernatant.
    add_mix_pellet(500, [reservoir_1.wells()[2]])
    # (D3) Repeat steps 7-8.
    add_mix_pellet(500, [reservoir_1.wells()[1]])
    add_mix_pellet(500, [reservoir_1.wells()[1]], remove_magnet=False)
    
    # 10. Dry the beads for 10 minutes or until dry.
    protocol.delay(minutes=10)
    protocol.move_labware(magnetic_block, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(sample_plate, new_location="6")
    
    # 11. To elute RNA from the beads, add ≥50µl DNase/RNase-Free Water and mix well for 5 minutes.
    add_and_mix(55, [reservoir_1.wells()[3]], 50)
    protocol.delay(minutes=5)
    
    # 12. Transfer the plate to the magnetic stand until beads have pelleted, then aspirate and dispense the
    # eluted RNA to a new plate/tube.
    protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(magnetic_block, new_location="6")
    protocol.delay(minutes=1)
    for i in range(cols):
        if i == cols-1:
            for well in sample_wells[i]:
                left_pipette.transfer(50, source=magnetic_block[well], dest=eluted_rna_plate[well])
        else:
            loc = "A" + str(i+1)
            right_pipette.transfer(50, source=magnetic_block[loc], dest=eluted_rna_plate[loc])