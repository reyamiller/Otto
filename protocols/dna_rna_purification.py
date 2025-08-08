# imports
from opentrons import protocol_api
import csv
import math

# metadata
metadata = {
    "protocolName": "DNA and RNA Purification with Zymo Quick-DNA/RNA MagBead Kit",
    "description": "This is a description of the protocol.",
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
    
    dna_plate = protocol.load_labware("greinerbioonegmbh_96_wellplate_2000ul", 5)
    rna_plate = protocol.load_labware("greinerbioonegmbh_96_wellplate_2000ul", 6)
    sample = protocol.define_liquid(
        name="Sample",
        display_color="#B3E2CD"
    )
    dna_plate.load_liquid(
        wells=selected_wells,
        volume=200,
        liquid=sample
    )
    
    reservoir_1 = protocol.load_labware("nest_12_reservoir_15ml", 2)
    dna_rna_lysis_buffer = protocol.define_liquid(
        name="DNA/RNA Lysis Buffer",
        display_color="#FBB4AE"
    )
    reservoir_1.load_liquid(
        wells=reservoir_1.wells()[0:4],
        volume=500,
        liquid=dna_rna_lysis_buffer
    )
    wash_1 = protocol.define_liquid(
        name="Wash 1",
        display_color="#B3CDE3"
    )
    reservoir_1.load_liquid(
        wells=reservoir_1.wells()[4:8],
        volume=500,
        liquid=wash_1
    )
    wash_2 = protocol.define_liquid(
        name="Wash 2",
        display_color="#DECBE4"
    )
    reservoir_1.load_liquid(
        wells=reservoir_1.wells()[8:12],
        volume=500,
        liquid=wash_2
    )
    reservoir_2 = protocol.load_labware("nest_12_reservoir_15ml", 3)
    dnase_rnase_free_water = protocol.define_liquid(
        name="DNase/RNase-Free Water",
        display_color="#FAE68E"
    )
    reservoir_2.load_liquid(
        wells=reservoir_2.wells()[0:2],
        volume=500,
        liquid=dnase_rnase_free_water
    )
    ethanol = protocol.define_liquid(
        name="Ethanol (95-100%)",
        display_color="#FF9AD0"
    )
    reservoir_2.load_liquid(
        wells=reservoir_2.wells()[2:6],
        volume=500,
        liquid=ethanol
    )
    dnase_i_reaction_mix = protocol.define_liquid(
        name="DNase I Reaction Mix",
        display_color="#9BE3D7"
    )
    reservoir_2.load_liquid(
        wells=[reservoir_2.wells()[6]],
        volume=500,
        liquid=dnase_i_reaction_mix
    )
    dna_rna_prep_buffer = protocol.define_liquid(
        name="DNA/RNA Prep Buffer",
        display_color="#FEC794"
    )
    reservoir_2.load_liquid(
        wells=reservoir_2.wells()[7:9],
        volume=500,
        liquid=dna_rna_prep_buffer
    )
    beads = protocol.define_liquid(
        name="MagBeads",
        display_color="#727272"
    )
    reservoir_2.load_liquid(
        wells=[reservoir_2.wells()[9]],
        volume=100,
        liquid=beads
    )
    
    dna_magnet_plate = protocol.load_labware("96well_plate_2000ul_on_magnet_plate", protocol_api.OFF_DECK)
    rna_magnet_plate = protocol.load_labware("96well_plate_2000ul_on_magnet_plate", protocol_api.OFF_DECK)
    eluted_dna_plate = protocol.load_labware("thermofast_96_wellplate_200ul", 8)
    eluted_rna_plate = protocol.load_labware("thermofast_96_wellplate_200ul", 9)
    
    liquid_waste = protocol.load_labware("nest_1_reservoir_195ml", 7)
    
    tips_1 = protocol.load_labware("opentrons_96_tiprack_300ul", 1)
    left_pipette = protocol.load_instrument("p300_single_gen2", "left", tip_racks=[tips_1])
    tips_2 = protocol.load_labware("opentrons_96_tiprack_300ul", 4)
    right_pipette = protocol.load_instrument("p300_multi_gen2", "right", tip_racks=[tips_2])
    
    def add_and_mix(vol: float, source: list[protocol_api.Well], dest: protocol_api.Labware, mix_vol=250.0):
        """
        Transfers the specified volume of liquid from the specified source to the sample plate and mixes.
        
        :param vol: The volume to be transferred, in µl.
        :param source: A list of wells containing the liquid to be aspirated. `add_and_mix` automatically calculates the index of the source to access.
        :param dest: The destination plate in which to dispense the liquid.
        :param mix_vol: The amount to pipette up and down when mixing.
        """
        for i in range(cols):
            src = source[i // (12 // len(source))]
            if i == cols-1:
                for well in sample_wells[i]:
                    left_pipette.transfer(volume=vol, source=src, dest=dest[well], blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(10, mix_vol))
            else:
                loc = "A" + str(i+1)
                right_pipette.transfer(volume=vol, source=src, dest=dest[loc], blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(10, mix_vol))
    
    def aspirate_supernatant(num_aspirations: int, source: protocol_api.Labware, dest: protocol_api.Labware):
        """
        Aspirates and discards the supernatant after the MagBeads have been pelleted from the solution.
        
        :param num_aspirations: The number of times to aspirate the supernatant from any one well.
        :param source: The plate from which to aspirate the supernatant.
        :param dest: The location in which to dispense the supernatant.
        """
        for i in range(cols):
            if i == cols-1:
                for well in sample_wells[i]:
                    left_pipette.pick_up_tip()
                    for j in range(num_aspirations):
                        left_pipette.aspirate(location=source[well].bottom(z=-1), volume=250)
                        left_pipette.dispense(location=dest[well].bottom(z=5))
                    left_pipette.drop_tip()
            else:
                loc = "A" + str(i+1)
                right_pipette.pick_up_tip()
                for j in range(num_aspirations):
                    right_pipette.aspirate(location=source[loc].bottom(z=-1), volume=250)
                    right_pipette.dispense(location=dest[loc].bottom(z=5))
                right_pipette.drop_tip()
    
    def add_mix_pellet_aspirate(vol: float, source: list[protocol_api.Well], dest: protocol_api.Labware, num_aspirations: int, source_2: protocol_api.Labware, dest_2: protocol_api.Labware, remove_magnet=True):
        """
        Calls `add_and_mix`, transfers the sample plate to the magnetic block, calls `aspirate_supernatant`, and
        removes the sample plate from the magnetic block.
        
        :param vol: The volume to be transferred, in µl, for `add_and_mix`.
        :param source: A list of wells containing the liquid to be aspirated for `add_and_mix`. The index of the source to access is automatically calculated.
        :param dest: The destination plate in which to dispense the liquid for `add_and_mix`.
        :param num_aspirations: The number of times to aspirate the supernatant from any one well for `aspirate_supernatant`.
        :param source_2: The plate from which to aspirate the supernatant for `aspirate_supernatant`.
        :param dest_2: The location in which to dispense the supernatant for `aspirate_supernatant`.
        :param remove_magnet: Whether or not to remove the plate from the magnet at the end of the function.
        """
        add_and_mix(vol, source, dest)
        new_loc = "5"
        if dest == rna_plate:
            new_loc = "6"
        protocol.move_labware(dest, new_location=protocol_api.OFF_DECK)
        protocol.move_labware(source_2, new_location=new_loc)
        protocol.delay(minutes=1)
        aspirate_supernatant(num_aspirations, source_2, dest_2)
        if remove_magnet:
            protocol.move_labware(source_2, new_location=protocol_api.OFF_DECK)
            protocol.move_labware(dest, new_location=new_loc)
    
    # 1. add 500µl (2.5 volumes) DNA/RNA Lysis Buffer to the 200µl sample and mix well
    add_and_mix(500, reservoir_1.wells()[0:4], dna_plate)
    
    # 2. add 30µl MagBinding Beads and mix well for 20 minutes
    for i in range(cols):
        if i == cols-1:
            for well in sample_wells[i]:
                left_pipette.pick_up_tip()
                left_pipette.mix(repetitions=5, volume=40, location=reservoir_2.wells()[9])
                left_pipette.aspirate(30, location=reservoir_2.wells()[9])
                left_pipette.dispense(location=dna_plate[well])
                left_pipette.mix(repetitions=10, volume=250, location=dna_plate[well])
                left_pipette.drop_tip()
        else:
            loc = "A" + str(i+1)
            right_pipette.pick_up_tip()
            right_pipette.mix(repetitions=5, volume=40, location=reservoir_2.wells()[9])
            right_pipette.aspirate(30, location=reservoir_2.wells()[9])
            right_pipette.dispense(location=dna_plate[loc])
            right_pipette.mix(repetitions=10, volume=250, location=dna_plate[loc])
            right_pipette.drop_tip()
    
    # 3. transfer the plate to the magnetic stand until beads (DNA) have pelleted, then transfer the cleared
    # supernatant (RNA) into a new plate.
    protocol.move_labware(dna_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(dna_magnet_plate, new_location="5")
    protocol.delay(minutes=1)
    aspirate_supernatant(3, dna_magnet_plate, rna_plate)
    protocol.move_labware(dna_magnet_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(dna_plate, new_location="5")
    
    # 4. [DNA Purification] Add 500µl MagBead DNA/RNA Wash 1 and mix well. Pellet the beads and discard the supernatant.
    add_mix_pellet_aspirate(500, reservoir_1.wells()[4:8], dna_plate, 3, dna_magnet_plate, liquid_waste)
    
    # 4. [RNA Purification] Add 700µl (1 volume) ethanol (95-100%) (1:1) to the supernatant and mix well.
    add_and_mix(700, reservoir_2.wells()[2:6], rna_plate)
    
    # 5. [DNA Purification] Add 500µl MagBead DNA/RNA Wash 2 and mix well. Pellet the beads and discard the supernatant.
    add_mix_pellet_aspirate(500, reservoir_1.wells()[8:12], dna_plate, 3, dna_magnet_plate, liquid_waste)
    
    # 5. [RNA Purification] Add 30µl/well MagBinding Beads and mix well for 10 minutes.
    for i in range(cols):
        if i == cols-1:
            for well in sample_wells[i]:
                left_pipette.pick_up_tip()
                left_pipette.mix(repetitions=5, volume=40, location=reservoir_2.wells()[9])
                left_pipette.aspirate(30, location=reservoir_2.wells()[9])
                left_pipette.dispense(location=rna_plate[well])
                left_pipette.mix(repetitions=10, volume=250, location=rna_plate[well])
                left_pipette.drop_tip()
        else:
            loc = "A" + str(i+1)
            right_pipette.pick_up_tip()
            right_pipette.mix(repetitions=5, volume=40, location=reservoir_2.wells()[9])
            right_pipette.aspirate(30, location=reservoir_2.wells()[9])
            right_pipette.dispense(location=rna_plate[loc])
            right_pipette.mix(repetitions=10, volume=250, location=rna_plate[loc])
            right_pipette.drop_tip()
    
    # 6. [DNA Purification] Add 500µl ethanol (95-100%) and mix well. Pellet the beads and discard the supernatant.
    add_mix_pellet_aspirate(500, reservoir_2.wells()[2:6], dna_plate, 3, dna_magnet_plate, liquid_waste)
    
    # 6. [RNA Purification] Transfer the plate to the magnetic stand until beads have pelleted, then aspirate and
    # discard the supernatant.
    protocol.move_labware(rna_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(rna_magnet_plate, new_location="6")
    protocol.delay(minutes=1)
    aspirate_supernatant(4, rna_magnet_plate, liquid_waste)
    protocol.move_labware(rna_magnet_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(rna_plate, new_location="6")
    
    # 7. [DNA Purification] Repeat step 6.
    add_mix_pellet_aspirate(500, reservoir_2.wells()[2:6], dna_plate, 3, dna_magnet_plate, liquid_waste)
    
    # 7. [RNA Purification] Add 500µl MagBead DNA/RNA Wash 1 and mix well. Pellet the beads and discard the supernatant.
    add_mix_pellet_aspirate(500, reservoir_1.wells()[4:8], rna_plate, 3, rna_magnet_plate, liquid_waste)
    
    # 8. [DNA Purification] Dry the beads for 10 minutes or until dry.
    protocol.delay(minutes=10)
    
    # 8. [RNA Purification] Add 500µl MagBead DNA/RNA Wash 2 and mix well. Pellet the beads and discard the supernatant.
    add_mix_pellet_aspirate(500, reservoir_1.wells()[8:12], rna_plate, 3, rna_magnet_plate, liquid_waste)
    
    # 9. [DNA Purification] Add 50µl DNase/RNase-Free Water and mix well for 5 minutes.
    add_and_mix(50, reservoir_2.wells()[0:2], dna_plate, 30)
    
    # 9. [RNA Purification] Add 500µl ethanol (95-100%) and mix well. Pellet the beads and discard the supernatant.
    add_mix_pellet_aspirate(500, reservoir_2.wells()[2:6], rna_plate, 3, rna_magnet_plate, liquid_waste)
    
    # 10. [DNA Purification] Transfer the plate to the magnetic stand until beads have pelleted, then aspirate and
    # dispense the eluted DNA to a new plate/tube.
    protocol.move_labware(dna_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(dna_magnet_plate, new_location="5")
    protocol.delay(minutes=1)
    aspirate_supernatant(1, dna_magnet_plate, eluted_dna_plate)
    protocol.move_labware(dna_magnet_plate, new_location=protocol_api.OFF_DECK)
    
    # 10. [RNA Purification] Repeat step 9.
    add_mix_pellet_aspirate(500, reservoir_2.wells()[2:6], rna_plate, 3, rna_magnet_plate, liquid_waste)
    
    # 11. [RNA Purification] DNase I treatment
    # (D1) Add 50µl DNase I Reaction Mix and mix gently for 10 minutes.
    add_and_mix(50, [reservoir_2.wells()[6]], rna_plate, 30)
    # (D2) Add 500µl DNA/RNA Prep Buffer and mix well for 10 minutes. Pellet the beads and discard the supernatant.
    add_mix_pellet_aspirate(500, reservoir_2.wells()[7:9], rna_plate, 3, rna_magnet_plate, liquid_waste)
    # (D3) Repeat steps 9-10.
    add_mix_pellet_aspirate(500, reservoir_2.wells()[2:6], rna_plate, 3, rna_magnet_plate, liquid_waste)
    add_mix_pellet_aspirate(500, reservoir_2.wells()[2:6], rna_plate, 3, rna_magnet_plate, liquid_waste, False)
    
    # 12. [RNA Purification] Dry the beads for 10 minutes or until dry.
    protocol.delay(minutes=10)
    protocol.move_labware(rna_magnet_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(rna_plate, new_location="6")
    
    # 13. [RNA Purification] Add 50µl DNase/RNase-Free Water and mix well for 5 minutes.
    add_and_mix(50, reservoir_2.wells()[0:2], rna_plate, 30)
    
    # 14. [RNA Purification] Transfer the plate to the magnetic stand until beads have pelleted, then aspirate and
    # dispense the eluted RNA to a new plate/tube.
    protocol.move_labware(rna_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(rna_magnet_plate, new_location="6")
    protocol.delay(minutes=1)
    aspirate_supernatant(1, rna_magnet_plate, eluted_rna_plate)