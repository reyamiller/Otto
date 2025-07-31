# imports
from opentrons import protocol_api

# metadata
metadata = {
    "protocolName": "Dilution",
    "description": "Dilutes a sample in 5 solutions of different specified volumes.",
    "author": "Reya Miller"
}

requirements = {"robotType": "OT-2", "apiLevel": "2.22"}

def add_parameters(parameters: protocol_api.Parameters):
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
    for i in range(1, 6):
        name = "volume_" + (str) (i)
        display = "Volume " + (str) (i)
        desc = "The volume of dilutent in solution " + (str) (i) + "."
        parameters.add_float(
            variable_name=name,
            display_name=display,
            description=desc,
            default=(i*10),
            minimum=1,
            maximum=100,
            unit="µL"
        )
    parameters.add_float(
        variable_name="sample_volume",
        display_name="Sample volume",
        description="The volume of the sample added to each solution.",
        default=1,
        minimum=1,
        maximum=20,
        unit="µL"
    )

def run(protocol: protocol_api.ProtocolContext):
    # place a 96 20µl tip rack in slot 6 of the robot deck
    tips = protocol.load_labware("opentrons_96_tiprack_20ul", 6)
    # place a 24 tube rack with 1.5ml safelock snapcap in slot 3 of the robot deck
    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 3)
    # the diluent (water) goes in slot D2 of the tube rack
    diluent_tube = tube_rack["D2"]
    diluent = protocol.define_liquid(
        name="Diluent",
        description="The liquid being used to dilute the sample.",
        display_color="#0051FF"
    )
    tube_rack.load_liquid(
        wells=["D2"],
        volume=150,
        liquid=diluent
    )
    # the sample being diluted goes in slot D1 of the tube rack
    main_sample_tube = tube_rack["D1"]
    main_sample = protocol.define_liquid(
        name="Main sample",
        description="The sample being diluted.",
        display_color="#FD9381"
    )
    tube_rack.load_liquid(
        wells=["D1"],
        volume=150,
        liquid=main_sample
    )
    
    # add a single-channel 20µL pipette to the left mount and use the specified tip rack
    left_pipette = protocol.load_instrument("p20_single_gen2", "left", tip_racks=[tips])
    left_pipette.starting_tip = tips[protocol.params.starting_tip_row + protocol.params.starting_tip_col]
    
    # transfer various amounts of the diluent into the first 5 slots of the tube rack
    left_pipette.pick_up_tip()
    left_pipette.transfer(protocol.params.volume_1, diluent_tube, tube_rack["A1"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.transfer(protocol.params.volume_2, diluent_tube, tube_rack["A2"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.transfer(protocol.params.volume_3, diluent_tube, tube_rack["A3"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.transfer(protocol.params.volume_4, diluent_tube, tube_rack["A4"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.transfer(protocol.params.volume_5, diluent_tube, tube_rack["A5"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.drop_tip()
    
    # transfer [sample_volume]µL of the sample to each of the slots of diluent
    for i in range(5):
        loc = "A" + (str) (i+1)
        left_pipette.transfer(protocol.params.sample_volume, main_sample_tube, tube_rack[loc], blow_out=True, blowout_location="destination well")