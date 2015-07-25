libcloudcore
============

.. image:: http://codecov.io/github/Jc2k/libcloudcore/coverage.svg?branch=master :target: http://codecov.io/github/Jc2k/libcloudcore?branch=master

If you find this version of the code online, here be dragons! This is still
very early code.

libcloudcore is a low-level abstraction for multiple cloud service providers.
It is an experiment at how libcloud could be refactored to:

 * Support all API's provided by a service, rather than the subset that matches
   an abstraction.
 * Reduce amount of code needed to support a new provider to the absolute
   minimum.

It is inspired by the botocore API and is:

 * Http library agnostic (with backends planned for asyncio and twisted).
 * Data driven.
 * Introspectable.

The API is inspired by botocore. It provides a low-level API binding. Common
requirements like pagination and waiting for resources to be created are dealth
with, but mapping API's to objects or to a generic abstraction is left to a
higher level library.
