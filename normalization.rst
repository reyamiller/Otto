
.. _normalization:

*************
Normalization
*************

The `Normalization <protocols/normalization.py>`_ protocol normalizes the amount of material in the wells of a plate based on values that are pre-specified by the user.

The easiest way to input these values is to copy and paste from a spreadsheet. See `this <https://docs.google.com/spreadsheets/d/1K7OXYfy0i2oJgIokcdIegjBVeeBMqR_-SODV961FI2k/edit?usp=sharing>`_ link for a template.

.. code-block:: python

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

A water plate is defined based on ``water_volume_data``. The protocol uses ``csv`` to read the data.

.. code-block:: python

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

A similar process is used to define the sample plate.

The robot first adds the specified volumes of water to the corresponding wells of the water plate. Note that this step only uses one pipette tip.

.. code-block:: python

    left_pipette.pick_up_tip()
    for well in wells_used:
        left_pipette.transfer((float) (water_volumes[well]), tube_rack["A1"], water_plate[well], new_tip="never", blow_out=True, blowout_location="destination well")
    left_pipette.drop_tip()

Then the specified volumes of sample are transferred to the corresponding wells of the water plate.

.. code-block:: python

    for well in wells_used:
        left_pipette.transfer((float) (dna_volumes[well]), dna_plate[well], water_plate[well], blow_out=True, blowout_location="destination well")