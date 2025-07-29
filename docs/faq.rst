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
      leaves: 'RandomRunNumber'. I will treat this as a 'singleton'. To
      suppress this warning next time, please define your singletons
      explicitly. [singleton-undefined]

   You can define your singletons by inheriting from :class:`atlas_schema.schema.NtupleSchema`:

   .. code-block:: python

      from atlas_schema.schema import NtupleSchema


      class MySchema(NtupleSchema):
          singletons = {"RandomRunNumber", ...}

   and then simply use ``MySchema`` in place of ``NtupleSchema``.


... define custom collections?
   If you get a ``TypeError`` about the size of an array not matching the size of a form

   .. code-block:: bash

      TypeError: size of array (10058) is less than size of form (87106)

   then there is likely a few common reasons for this. One potential issue is that you're hit by a bug in ``athena`` which you cannot recover from due to corrupted files: https://github.com/scikit-hep/coffea/issues/1083 . However, another situation that triggers this error is due to zipping up incompatible branches into the same collection. ``atlas-schema`` tries very hard to automatically group up related collections for you, but sometimes you're using an ntuple that does not follow consistent conventions for the branch names. In this case, you will need to define your own custom schema. Please see :class:`atlas_schema.schema.NtupleSchema` for more details.

... handle missing singletons?
   Sometimes singletons can be missing from a file you process, such as if you are processing many different files with different structures. These warnings tend to look like:

   .. code-block:: bash

      RuntimeWarning: Missing singletons : ['singleton']. [singleton-missing]

  ``atlas-schema`` tries to be smart and let you know when you have singletons that need to be defined, and will also catch branches or collections you define that are not actually in the file. In most cases, these warnings are harmless and are to let you know about inconsistencies in how you run your code.
