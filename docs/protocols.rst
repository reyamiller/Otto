
.. _protocols:

*********
Protocols
*********

General Structure
=================

Each protocol I've written follows a general basic structure with many shared elements.

This import line identifies the python file as an Opentrons protocol.

.. code-block:: python

    from opentrons import protocol_api

The fields in the metadata dictionary will show up on the Opentrons App when you import the protocol in order to provide more information about it.

.. code-block:: python

    metadata = {
        "protocolName": "Protocol Name",
        "description": "This is a protocol description.",
        "author": "Reya Miller"
    }

The requirements indicate that the protocol will run on an OT-2 robot with version 2.22 of the Opentrons Python API.

.. code-block:: python

    requirements = {"robotType": "OT-2", "apiLevel": "2.22"}

.. _add-parameters-function:

The ``add_parameters()`` function
---------------------------------

.. code-block:: python

    def add_parameters(parameters: protocol_api.Parameters):

The ``add_parameters()`` function allows for greater control of protocols without the need to write extra code. These parameters are entered in the Opentrons app before running the protocol.

All of my protocols contain at least two parameters, ``starting_tip_row`` and ``starting_tip_col``, which specify which tip the pipette should pick up first. This is useful when using a partially-filled tip rack; otherwise the robot assumes there is a tip at slot ``A1`` of the rack.

.. code-block:: python

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

By default, the values for these parameters are ``A`` and ``1``, respectively.

.. _run-function:

The ``run()`` function
----------------------

The ``run()`` function contains the all of the code for the actual protocol steps.

.. code-block:: python

    def run(protocol: protocol_api.ProtocolContext):

The protocol context argument is used to add labware and hardware to the protocol.

.. _dilution:

Dilution
========

The `Dilution </protocols/dilution.py>`_ protocol dilutes a sample in 5 solutions of different specified volumes.

Both the volume of the sample and the volumes of diluent are defined in the ``add_parameters()`` function to allow for user customization.

By default, 1µl of sample is added to solutions containing 10, 20, 30, 40, and 50 µl of diluent, respectively.

.. code-block:: python

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
            unit="µl"
        )
    parameters.add_float(
        variable_name="sample_volume",
        display_name="Sample volume",
        description="The volume of the sample added to each solution.",
        default=1,
        minimum=1,
        maximum=20,
        unit="µl"
    )

Setting Up
----------

The first thing to do in the ``run()`` function is to define all of the labware and hardware that will be used.

An Opentrons 24 Tube Rack with Eppendorf 1.5 mL Safe-Lock Snapcap is placed in slot 3 of the deck.

.. code-block:: python

    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 3)

The diluent, water, goes into slot D2 of the tube rack.

.. code-block:: python

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

Defining liquids isn't necessary, but it makes it easier to identify what goes where in the Opentrons app.

The sample to be diluted goes into slot D1 of the tube rack.

.. code-block:: python

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

A 96 20µl tip rack is placed in slot 6 of the deck.

.. code-block:: python

    tips = protocol.load_labware("opentrons_96_tiprack_20ul", 6)

Use the single-channel P20 pipette in the left pipette mount and specify the tip rack and starting tip.

The P20 is used instead of the P300 due to the relatively small volumes being pipetted.

.. code-block:: python

    left_pipette = protocol.load_instrument("p20_single_gen2", "left", tip_racks=[tips])
    left_pipette.starting_tip = tips[protocol.params.starting_tip_row + protocol.params.starting_tip_col]

Now that we have all of the necessary labware and hardware, Otto can start pipetting.

The specified amounts of diluent are added to the first five slots of the tube rack.

.. code-block:: python

    left_pipette.pick_up_tip()
    left_pipette.transfer(protocol.params.volume_1, diluent_tube, tube_rack["A1"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.transfer(protocol.params.volume_2, diluent_tube, tube_rack["A2"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.transfer(protocol.params.volume_3, diluent_tube, tube_rack["A3"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.transfer(protocol.params.volume_4, diluent_tube, tube_rack["A4"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.transfer(protocol.params.volume_5, diluent_tube, tube_rack["A5"], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.drop_tip()

Note that we only need one tip for this process, which is why ``new_tip="never"`` is specified.

Then the specified sample volume is transferred to each of the slots of diluent.

.. code-block:: python

    for i in range(5):
        loc = "A" + (str) (i+1)
        left_pipette.transfer(protocol.params.sample_volume, main_sample_tube, tube_rack[loc], blow_out=True, blowout_location="destination well")

end of protocol