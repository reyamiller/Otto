
*****************************
DNA Extraction & Purification
*****************************

The `DNA Extraction & Purification <protocols/dna_extraction_purification.py>`_ protocol follows steps 6-18 of the Omega Bio-tek Mag-Bind® Blood & Tissue DNA HDQ 96 Kit Quick Guide for DNA extraction and purification from up to 10 mg tissue.

The wells containing tissue are specified in the code, and can be changed manually or pasted from a spreadsheet.

Note that columns must be filled in order, and one column must be full before moving on to the next one.

.. code-block:: python

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

This protocol uses both the 8-channel and single-channel pipettes, so there are three parameters for starting tips: ``multi_starting_col``, ``single_starting_row``, and ``single_starting_col``.
Since the 8-channel pipette picks up an entire column of tips at a time, it is best to use separate tip racks for the pipettes. The starting row for the 8-channel pipette tips is always row A, so we don't need a parameter for that.

The ``run`` function starts by reading the data given for the sample well plate. ``selected_wells`` is a list of every well that contains a sample.

.. code-block:: python

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

Then the number of columns in the plate that contain samples, ``cols``, is calculated by integer division of the number of wells used by 8 (the number of wells in a column).

.. code-block:: python

    cols = math.ceil(len(selected_wells) / 8)

The last thing to do with the wells data is to create ``sample_wells``, which is a list of length ``cols`` in which every item is itself a list representing one column of the well plate.

.. code-block:: python

    sample_wells = []
    for i in range(cols):
        start_index = 8 * i
        if i == cols-1:
            sample_wells.insert(i, selected_wells[start_index:])
        else:
            sample_wells.insert(i, selected_wells[start_index:start_index+8])

Aside from the standard labware on the deck, the protocol also loads a magnetic plate in the *off-deck* location.
The protocol pauses at various points for the user to move this plate on and off the deck.

.. code-block:: python

    magnetic_block = protocol.load_labware("96well_plate_2000ul_on_magnet_plate", protocol_api.OFF_DECK)

Because many similar steps are performed throughout this protocol, we utilize two custom functions. The first of these is ``add_and_mix``.
``add_and_mix`` takes in two parameters: ``vol``, the volume to add to the samples, and ``source``, a list of wells that contain the liquid to be added. This list can contain just one well, but when dealing with greater numbers of samples, it is possible that multiple reservoir wells will have to contain the same liquid to account for the amount needed. The function automatically determines which well to aspirate from if this is the case.
As its name would suggest, ``add_and_mix`` adds the specified volume of specified liquid to each of the samples and mixes the solution by pipetting up and down repeatedly.

.. code-block:: python

    def add_and_mix(vol: float, source: list[protocol_api.Well]):
        src = source[i // (12 // len(source))]
        if i == cols-1:
            for well in sample_wells[i]:
                left_pipette.transfer(volume=vol, source=src, dest=sample_plate[well], blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(10, 250))
        else:
            loc = "A" + str(i+1)
            right_pipette.transfer(volume=vol, source=src, dest=loc, blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(10, 250))

The second function is ``aspirate_supernatant``, which aspirates and discards the supernatant in each well after the Mag-Bind® particles have been cleared from the solution.
``aspirate_supernatant`` has one parameter, ``num_aspirations``, to determine how many times to perform this process.

.. code-block:: python

    def aspirate_supernatant(num_aspirations: int):
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

From here the protocol just follows the steps as given in the Quick Guide, making calls to ``add_and_mix`` and ``aspirate_supernatant`` as needed accordingly.
However, there are multiple points in the protocol that require steps to be performed manually by the user.

For instance, after adding the AL Buffer and HDQ Binding Buffer, the protocol pauses so the user can add the binding beads to the samples.

.. code-block:: python

    protocol.pause("Add binding beads.")

Every step that involves putting the well plate on a magnetic separation device is also a manual action. The protocol pauses so the user can put the magnetic block on the deck.
Note that the robot sees the well plate and the well plate on the magnetic block as two separate pieces of labware, even though you're just putting the well plate on top of the magnet.

.. code-block:: python

    protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(magnetic_block, new_location="6")

The protocol will not continue until the user indicates in the Opentrons app that these manual steps have been completed.