The official BrainFrame client, written in PyQt

Installation
======================

Snap
---------------

Use the :code:`snap` command to install the Snap from the official Snapcraft
repositories. Make sure to change the channel version to whichever version of
the client you want to be using.

.. code-block:: bash

    snap install brainframe-client --channel=0.27/stable


Build
======================

.. note::
    All build scripts must be run from the root of the project


Snap
---------------

.. note::
    Make sure you have installed the Python development dependencies,
    specifically :code:`docker`.

We have provided a script that builds the Snap inside a Docker image, and then
extracts the files to the host computer.

.. code-block:: bash

    python build/snap/build_snap.py

.. tip::
    Use the :code:`--help` flag to get a list of optional arguments for configuration.
