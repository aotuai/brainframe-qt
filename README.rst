This is the official BrainFrame_ client, written using PyQt5. BrainFrame is a
platform for realtime machine learning and video-analytics that makes inference
easy when using OpenVisionCapsules_ capsules.

.. image:: docs/img/client_screenshot.png
    :align: center
    :width: 75%

.. _BrainFrame: https://aotu.ai/docs/
.. _OpenVisionCapsules: https://github.com/opencv/open_vision_capsules

###############
Getting Started
###############

* Prerequisites_
* `Direct Installation`_
* `Building from source`_
* Running_
* `(Re)distribution`_

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

#######
Running
#######

First, make sure you have the backend installed and running on your server
machine. If not, follow the steps in the Prerequisites_ section.

.. code-block:: bash

    brainframe compose up

************************
From Direct Installation
************************

If you installed the client through `a direct installation`_, simply launch the
client through your typical start/application menu.

    Note: If using the beta Windows client, this is not yet supported. Please
    double click the :code:`.exe` to start the client.

.. _`a direct installation`: `Direct Installation`_

***********
From Source
***********

If running from source, you'll need to install all the client dependencies.

System Dependencies
-------------------

There are a few dependencies that need to be installed globally to your system.
These are the dependencies for :code:`pygobject` and :code:`Qt`.

+------------------+-------------------------------------------------+
| Operating System | Dependency installation command                 |
+==================+=================================================+
| Ubuntu 18.04     | ::                                              |
+------------------+                                                 |
| Ubuntu 20.04     |     apt install \\                              |
|                  |         libcairo2-dev libgirepository1.0-dev \\ |
|                  |         gir1.2-gst-rtsp-server \\               |
|                  |         qtbase5-dev qt5-default qttools5-dev \\ |
|                  |         qtbase5-dev-tools qttools5-dev-tools    |
+------------------+-------------------------------------------------+
| Arch             | ::                                              |
|                  |                                                 |
|                  |     pacman -S --needed \\                       |
|                  |         cairo gobject-introspection \\          |
|                  |         qt5-tools qt5-base                      |
+------------------+-------------------------------------------------+
| Windows          | :code:`TODO`                                    |
+------------------+-------------------------------------------------+

Python Dependencies
-------------------

In order to pull down the Python dependencies, you'll need to install Poetry_.

+------------------+-----------------------------+
| Operating System | Poetry installation         |
+==================+=============================+
| Ubuntu 18.04     | See `Poetry instructions`_  |
+------------------+-----------------------------+
| Ubuntu 20.04     | See `Poetry instructions`_  |
+------------------+-----------------------------+
| Arch             | ::                          |
|                  |                             |
|                  |     pacman -S python-poetry |
+------------------+-----------------------------+
| Windows          | See `Poetry instructions`_  |
+------------------+-----------------------------+

Install the Python dependencies using Poetry.

.. code-block:: bash

    poetry install

Finally, start the client

.. code-block:: bash

    python brainframe_client.py  # Use python3 if on an older system

.. _Poetry: https://github.com/python-poetry/poetry
.. _`Poetry instructions`: https://python-poetry.org/docs/#installation

################
(Re)distribution
################

This repository is targeted for end-users of the BrainFrame Client. If you would
like to (re)distribute the client, refer to :code:`DISTRIBUTION.rst` in the
project root.
