This is the official BrainFrame_ client, written in PyQt5.

.. image:: docs/img/client_screenshot.png
    :align: center
    :width: 75%

.. _BrainFrame: https://aotu.ai/docs/

###############
Getting Started
###############

* Prerequisites_
* `Direct Installation`_
* `Building from source`_
* Usage_
* Distribution_

##############
Prerequisites
##############

In order to use the BrainFrame Client, you'll need to have the BrainFrame
backend installed and running. Check out our docs here_ to get started.

.. _here: https://aotu.ai/docs/getting_started/

###################
Direct Installation
###################

****
Snap
****

Use the :code:`snap` command to install the Snap from the official Snapcraft
repositories. Make sure to change the channel version to whichever version of
the client you want to be using.

.. code-block:: bash

    snap install brainframe-client --channel=0.27/stable

***
AUR
***

    Coming soon

*******
Windows
*******

    Note: The pre-built Windows client is still in beta.

You can download an :code:`.exe` of the `Windows client`_ from our website.

.. _`Windows client`: https://aotu.ai/docs/downloads/#brainframe-client

####################
Building from source
####################

    Note: All build scripts must be run from the root of the project


****
Snap
****

We have provided a script_ that builds the Snap inside a Docker image, and then
extracts the files to the host computer. Make sure you have installed the Python
development dependencies, specifically :code:`docker`.

.. code-block:: bash

    python package/snap/build_snap.py

Use the :code:`--help` flag to get a list of optional arguments (and default
values) for configuration.

Then, install the built Snap.

.. code-block:: bash

    snap install --dangerous dist/brainframe-client_*.snap

The :code:`--dangerous` flag allows Snap to install unsigned local files. This
is necessary as you've built the :code:`.snap` yourself.

.. _script: package/snap/build_snap.py

#####
Usage
#####

If you installed the client through `a direct installation`_, simply launch the
client through your typical start/application menu.

    Note: If using the beta Windows client, this is not yet supported. Please
    double click the :code:`.exe` to start the client.

.. _`a direct installation`: `Direct Installation`_


############
Distribution
############

This repository is targeted for end-users of the BrainFrame Client. If you would
like to (re)distribute the client, refer to :code:`DISTRIBUTION.rst` in the
project root.
