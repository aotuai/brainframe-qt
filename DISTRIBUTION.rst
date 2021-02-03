This file discusses some licensing concerns with the (re)distribution of the
BrainFrame Client, and is only relevant if you'd like to do so. If you are
simply interested in using the client without (re)distribution, see the
:code:`README.rst` file at the project root.

The *source code* for the BrainFrame Client is released under the BSD 3-Clause
License (see the :code:`LICENSE` file at the project root).

However, distribution of a complete BrainFrame Client (built or unbuilt) *with
dependencies* is a bit tricky, due to the licensing of some of these
dependencies. Currently, the client depends on Gstly, an internal, proprietary
library Aotu.ai uses to manage GStreamer-based video streaming [#]_. The client
*also* depends on PyQt5. Without a commercial license, PyQt is available under
the GPL.

We plan on removing the dependency on Gstly in the near future. But for now, if
you'd like to distribute the complete BrainFrame Client, with dependencies, the
PyQt Commercial License is available for purchase at Riverbank Computing's
website_.

If you have any concerns, please contact an IP lawyer at your own discretion.
This file does not constitute legal advice.

.. [#] You can learn how we make Gstly available in the otherwise-open-source
       BrainFrame client in our blog here_.

.. _here: https://aotu.ai/en/blog/2021/01/19/publishing-a-proprietary-python-package-on-pypi-using-poetry/
.. _binaries: https://aotu.ai/docs/downloads/#brainframe-client
.. _website: https://riverbankcomputing.com/commercial/buy
