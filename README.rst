libcloudcore
============

libcloudcore is a low-level abstraction for multiple cloud service providers.

It is:

 * Http library agnostic.
 * Data driven.
 * Introspectable.


The API is inspired by botocore. It provides a low-level API binding. Common
requirements like pagination and waiting for resources to be created are dealth
with, but mapping API's to objects or to a generic abstraction is left to a
higher level library.
