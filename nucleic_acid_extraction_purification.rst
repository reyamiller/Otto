
************************************************
DNA Extraction/Purification and RNA Purification
************************************************

I have written three protocols for extracting and purifying DNA and RNA.
The `DNA Extraction & Purification <protocols/dna_extraction_purification.py>`_ protocol follows steps 6-18 of the Omega Bio-tek Mag-Bind® Blood & Tissue DNA HDQ 96 Kit `Quick Guide <https://ensur.omegabio.com/ensur/contentAction.aspx?key=Production.9383.S2R4E1A3.20230907.294.4929177>`_ for DNA extraction and purification from up to 10 mg tissue.
The `RNA Purification <protocols/total_rna_purification.py>`_ protocol follows the steps given in part III of the Zymo Research Quick-RNA™ MagBead `protocol <https://files.zymoresearch.com/protocols/_r2132_r2133_quick-rna_magbead.pdf>`_.
The `DNA & RNA Extraction <protocols/dna_rna_extraction.py>`_ protocol follows the steps given in part IV of the Zymo Research Quick-DNA/RNA™ MagBead `protocol <https://files.zymoresearch.com/protocols/_r2130_r2131_quick-dna_rna_magbead.pdf>`_.

All three protocols are very similar, so to avoid redundancy I've grouped them together here.

The wells containing RNA samples are specified in the code and can be changed manually or pasted from a spreadsheet.

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

These protocols use both the 8-channel and single-channel pipettes, so there are three parameters for starting tips: ``multi_starting_col``, ``single_starting_row``, and ``single_starting_col``.
Since the 8-channel pipette picks up an entire column of tips at a time, it is best to use separate tip racks for the pipettes.
The starting row for the 8-channel pipette tips is always row A, so we don't need a parameter for that.

The ``run`` function for all three protocols starts by reading the data given for the sample well plate. ``selected_wells`` is a list of every well that contains a sample.

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

Aside from the standard labware on the deck (which differs slightly for each protocol), the three protocols all also load a magnetic plate in the *off-deck** location.
The protocols pause at various points for the user to move this plate on and off the deck.

For DNA Extraction/Purification and Total RNA Purification, this block is defined as follows:

.. code-block:: python

    magnetic_block = protocol.load_labware("96well_plate_2000ul_on_magnet_plate", protocol_api.OFF_DECK)

For DNA/RNA Purification, two separate blocks are defined:

.. code-block:: python

    dna_magnet_plate = protocol.load_labware("96well_plate_2000ul_on_magnet_plate", protocol_api.OFF_DECK)
    rna_magnet_plate = protocol.load_labware("96well_plate_2000ul_on_magnet_plate", protocol_api.OFF_DECK)

Even though the same magnet plate is used for both the DNA and RNA well plates, the protocol is written in this way so that the robot recognizes the difference between *a well plate* and *a well plate on top of the magnetic block*.

Because many similar steps are performed throughout the three protocols, we utilize some custom functions.
The first of these is ``add_and_mix``.

For DNA Extraction/Purification ``add_and_mix`` takes in two parameters: ``vol``, the volume to add to the samples, and ``source``, a list of wells that contain the liquid to be added.
This list can contain just one well, but when dealing with greater numbers of samples, it is possible that multiple reservoir wells will have to contain the same liquid to account for the amount needed. The function automatically determines which well to aspirate from if this is the case.

As its name would suggest, ``add_and_mix`` adds the specified volume of specified liquid to each of the samples and mixes the solution by pipetting up and down repeatedly.

For Total RNA Purification and DNA/RNA Purification, the function has an additional parameter, ``mix_vol``, which indicates the volume to pipette up and down when mixing. By default, ``mix_vol`` is 250µl. For the DNA/RNA Purification protocol, the function has a fourth parameter, ``dest``, which indicates which sample plate to add the solution to.

.. code-block:: python

    def add_and_mix(vol: float, source: list[protocol_api.Well], dest: protocol_api.Labware, mix_vol=250.0):
        for i in range(cols):
            src = source[i // (12 // len(source))]
            if i == cols-1:
                for well in sample_wells[i]:
                    left_pipette.transfer(volume=vol, source=src, dest=dest[well], blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(10, mix_vol))
            else:
                loc = "A" + str(i+1)
                right_pipette.transfer(volume=vol, source=src, dest=dest[loc], blow_out=True, blowout_location="destination well", new_tip="always", mix_after=(10, mix_vol))

The second function is ``aspirate_supernatant``, which aspirates and discards the supernatant in each well after the magnetic particles have been cleared from the solution.

For DNA Extraction/Purification and Total RNA Purification, ``aspirate_supernatant`` has just one parameter, ``num_aspirations``, to determine how many times to perform the process.

In the DNA/RNA Purification protocol, ``aspirate_supernatant`` has two more parameters, ``source`` and ``dest``.
``source`` indicates which sample well to aspirate from, and ``dest`` indicates where the aspirated supernatant should be dispensed.

.. code-block:: python

    def aspirate_supernatant(num_aspirations: int, source: protocol_api.Labware, dest: protocol_api.Labware):
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

These are the only functions needed for the DNA Extraction/Purification protocol, but the Total RNA Purification and DNA/RNA Extraction protocols have a third function, ``add_mix_pellet_aspirate``.
This function calls ``add_and_mix``, transfers the sample plate to the magnetic block, calls ``aspirate supernatant``, and then removes the sample plate from the magnetic block.

For the Total RNA Protocol, ``add_mix_pellet_aspirate`` has just two parameters: ``vol`` and ``source``, the same ones as ``add_and_mix``. (``aspirate_supernatant`` is called with ``num_aspirations`` set to 3.)

For the DNA Extraction/Purification protocol, the function takes in seven parameters:
* ``vol``: The volume to be transferred, in µl, for ``add_and_mix``.
* ``source``: A list of wells containing the liquid to be aspirated for ``add_and_mix``.
* ``dest``: The destination plate in which to dispense the liquid for ``add_and_mix``.
* ``num_aspirations``: The number of times to aspirate the supernatant from any one well for ``aspirate_supernatant``.
* ``source_2``: The plate from which to aspirate the supernatant for ``aspirate_supernatant``.
* ``dest_2``: The location in which to dispense the supernatant for ``aspirate_supernatant``.
* ``remove_magnet``: Whether or not to remove the plate from the magnet at the end of the function. True by default.

.. code-block:: python

    def add_mix_pellet_aspirate(vol: float, source: list[protocol_api.Well], dest: protocol_api.Labware, num_aspirations: int, source_2: protocol_api.Labware, dest_2: protocol_api.Labware, remove_magnet=True):
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

From here each protocol just follows the steps given in their respective guides, making calls to the functions described as necessary.
However, there are multiple points in the protocols that require steps to be performed manually by the user.

Every step that involves putting the sample plate on a magnetic separation device includes manual action.
The protocol pauses so the user can put the magnetic block on the deck.
Note that the robot sees *the well plate* and *the well plate on the magnetic block* as two separate pieces of labware, even though you're just putting the well plate on top of the magnet.

.. code-block:: python

    protocol.move_labware(sample_plate, new_location=protocol_api.OFF_DECK)
    protocol.move_labware(magnetic_block, new_location="6")

The protocols will not continue until the user indicates in the Opentrons app that these manual steps have been completed.