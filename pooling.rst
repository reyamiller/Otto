
.. _pooling:

*******
Pooling
*******

The `Pooling <protocols/pooling.py>`_ protocol pools liquid from user-specified wells into a single tube.

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

When we define the sample plate, we can now indicate that the water is in the wells specified by ``selected_wells``.

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

Before starting, there should be water in a tube in well ``A1`` of the tube rack.

The robot transfers ``x`` µl of water to well ``A2``, where ``x`` = 100 - the number of samples.

.. code-block:: python

    left_pipette.transfer(volume=(100 - len(selected_wells)), source=tube_rack["A1"], dest=tube_rack["A2"], blow_out=True, blowout_location="destination well")

Then 1µl of each sample gets pooled into the tube at well ``A2``.

.. code-block:: python

    for well in selected_wells:
        left_pipette.transfer(volume=1, source=dna_plate[well], dest=tube_rack["A2"], blow_out=True, blowout_location="destination well")

Accuracy
========