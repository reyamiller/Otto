
.. _protocols:

*********
Protocols
*********

General Structure
=================

Each protocol I've written follows a general basic structure with many shared elements.

.. code-block:: python

    from opentrons import protocol_api

This identifies the python file as an Opentrons protocol.

.. code-block:: python

    metadata = {
        "protocolName": "Protocol Name",
        "description": "This is a protocol description.",
        "author": "Reya Miller"
    }

The fields in the metadata dictionary will show up on the Opentrons App when you import the protocol in order to provide more information about it.

.. code-block:: python

    requirements = {"robotType": "OT-2", "apiLevel": "2.22"}

This indicates that the protocol will run on an OT-2 robot with version 2.22 of the Opentrons Python API.

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