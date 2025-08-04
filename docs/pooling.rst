
.. _pooling:

*******
Pooling
*******

The `Pooling </protocols/pooling.py>`_ protocol pools liquid from user-specified wells into a single tube.

The wells are specified in the code before the protocol is run. Users can copy and paste from a spreadsheet or manually change the values in the file.

.. code-block:: python

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

This data is then converted to comma-separated value (CSV) format.

.. code-block:: python

    selected_wells_data = selected_wells_data.replace('\t', ',')

There are 5 tubes which liquid is pooled into, and the volume of liquid in each tube is given as a runtime parameter. By default, the volumes (in µl) are 40, 80, 120, 160, and 200, respectively.

.. code-block:: python

    for i in range(1, 6):
        name = "volume_" + str(i)
        display = "Volume " + str(i)
        desc = "The volume to pool into tube " + str(i) + "."
        parameters.add_float(
            variable_name=name,
            display_name=display,
            description=desc,
            default=(i*40),
            minimum=40,
            maximum=1000,
            unit="µL"
        )

The ``run()`` function starts by reading ``selected_wells_data`` in order to determine which wells to pool from.

.. code-block:: python

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

Then we define the tube rack and indicate where the tubes of water are.

.. code-block:: python

    tube_rack = protocol.load_labware("opentrons_24_tuberack_eppendorf_1.5ml_safelock_snapcap", 3)
    water = protocol.define_liquid(
        name="Water",
        description="The liquid being used to dilute the samples.",
        display_color="#0051FF"
    )
    tube_rack.load_liquid(
        wells=["A1", "A2", "A3", "A4", "A5"],
        volume=150,
        liquid=water
    )

Next we define the DNA plate, which should hold DNA in the wells specified by ``selected_wells``.

.. code-block:: python

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

