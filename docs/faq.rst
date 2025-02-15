.. _faq:

FAQ
===

This is a list of Frequently Asked Questions about ``atlas-schema``.  Feel free to
suggest new entries!

How do I...
-----------

... define my singletons?
   Did you get a warning like the following when running your code?

   .. code-block:: bash

      RuntimeWarning: I identified a branch that likely does not have any
      leaves: RandomRunNumber. I will treat this as a 'singleton'. To suppress
      this warning next time, please define your singletons explicitly.

   You can define your singletons by inheriting from :class:`atlas_schema.schema.NtupleSchema`:

   .. code-block:: python

      from atlas_schema.schema import NtupleSchema


      class MySchema(NtupleSchema):
          singletons = {"RandomRunNumber", ...}

   and then simply use ``MySchema`` in place of ``NtupleSchema``.
