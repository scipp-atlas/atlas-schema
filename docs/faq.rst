.. _faq:

FAQ
===

This is a list of Frequently Asked Questions about ``atlas-schema``.  Feel free to
suggest new entries!

How do I...
-----------

... define my singletons?
   You can define your singletons by inheriting from :class:`atlas_schema.schema.NtupleSchema`:

   .. code-block:: python

      from atlas_schema.schema import NtupleSchema


      class MySchema(NtupleSchema):
          singletons = {"RandomRunNumber", ...}

   and then simply use ``MySchema`` in place of ``NtupleSchema``.
