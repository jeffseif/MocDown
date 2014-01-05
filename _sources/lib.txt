Source code documentation for MocDown extensions
================================================

RbwrTh
------

RbwrTh.py is a MocDown external library.  It modifies the default MocDown coolant update calculation, fuel processing, and cycle multiplication factor methods for simulation of the RBWR-Th core design.

.. automodule:: RbwrTh
   :members:

RbwrAc
------

RbwrAc.py is a MocDown external library which serves as an extension to RbwrTh.py.  Only the fuel processing method is modified.

.. automodule:: RbwrAc
   :members:

PECS-Check
----------

PecsCheck.py is a benchmark for code-to-code comparison with PECS.  It inherits MocDown and modifies some depletion and recycling methods to emulate the PECS simulation.

.. automodule:: PecsCheck
   :members:
