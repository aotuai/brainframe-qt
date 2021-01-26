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

    Note: All build scripts must be run from the root of the project


Snap
---------------

We have provided a script that builds the Snap inside a Docker image, and then
extracts the files to the host computer. Make sure you have installed the Python
development dependencies, specifically :code:`docker`.

.. code-block:: bash

    python package/snap/build_snap.py

Use the :code:`--help` flag to get a list of optional arguments (and default
values) for configuration.

Then, install the built Snap.

.. code-block:: bash

    snap install --dangerous dist/brainframe-client_*.snap

The :code:`--dangerous` flag allows Snap to install local files.


Distribution
======================

The *source code* for the BrainFrame Client is released under the BSD 3-Clause
License (see :code:`LICENSE` at the project root). You are free to modify and/or
distribute the *source code* however you see fit, as long you comply with its
license.

However, distribution of a complete BrainFrame client (built or unbuilt) with
dependencies is a bit tricky, due to licensing of some of these dependencies.
Currently, the client depends on Gstly, an internal, proprietary library Aotu
uses to manage GStreamer-based video streaming [#]_. The client *also* depends
on PyQt5. When we, Aotu, distribute our client binaries_, we do so under the
`PyQt5 commercial license`_, which we pay for. PyQt is also distributed under
the GPL, which this project defaults to using (but Aotu does not use for
deployment).

PyQt (licensed under the GPL) and Gstly (with its proprietary licensing) are in
conflict with one another, and cannot be distributed at the same time. If you
want to simply use the client, source or built, for your own *internal* use
(i.e. *without distribution*) there is nothing for you to be concerned with
here. However, if want to *distribute* the client, you will need to take one of
a few possible routes of action:

* Pay for the PyQt commercial license for yourself. This is charged on a per
  developer cost, not a per user/customer.
* Modify your distribution to no longer rely on Gstly, and then distribute the
  client in compliance with PyQt's GPL license.
* Distribute the source of the BrainFrame client, without dependencies. Then,
  have your end-users install the dependencies, including PyQt themselves on
  their own machines.

If you have any concerns, please contact an IP lawyer at your own discretion.
This is not legal advice.

.. [#] You can learn how we make Gstly available in the otherwise-open-source
       BrainFrame client, check out our blog here_.

.. _here: https://aotu.ai/en/blog/2021/01/19/publishing-a-proprietary-python-package-on-pypi-using-poetry/
.. _binaries: https://aotu.ai/docs/downloads/#brainframe-client
.. _`PyQt5 Commercial license`: https://riverbankcomputing.com/commercial/pyqt
