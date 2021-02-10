This file discusses some licensing concerns with the (re)distribution of the
BrainFrame Client, and is only relevant if you'd like to do so. If you are
simply interested in using the client without (re)distribution, see the
:code:`README.rst` file at the project root.

The *source code* for the BrainFrame Client is released under the BSD 3-Clause
License (see the :code:`LICENSE` file at the project root).

However, distribution of a BrainFrame Client (built or unbuilt) *with
dependencies* requires careful adherence to the licensing of the project's
dependencies. Currently, the client depends on Gstly, proprietary Aotu.ai
library [#]_. The client also depends on PyQt5 which, without a commercial
license, is only available for distribution under the GPL.

While we plan on removing the dependency on Gstly in the near future, the PyQt
Commercial License is available for purchase at Riverbank Computing's website_.

Please note that this file does not constitute legal advice.

.. [#] You can learn more about Gstly (and how we include it in the
       otherwise-open-source BrainFrame client) in our blog here_.

.. _here: https://aotu.ai/en/blog/2021/01/19/publishing-a-proprietary-python-package-on-pypi-using-poetry/
.. _binaries: https://aotu.ai/docs/downloads/#brainframe-client
.. _website: https://riverbankcomputing.com/commercial/buy
