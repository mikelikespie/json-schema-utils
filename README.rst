JSON Schema Utilities
=====================

**Work in progress**

This is going to be a suite of utilities for generating JSON schema.

Right now, it is work in progress, but the long-term goal is to allow
for two things:

* JSON Schema generation
* Code generation templating based on JSON schemas

The latter is somewhat inspired by WebKit's use of JSON schema and JSON-RPC 
in their web inspector projects.

The target format of this suite is going to be based on the IETF draft of
`A JSON Media Type for Describing the Structure and Meaning of JSON Documents
<http://tools.ietf.org/html/draft-zyp-json-schema-03>`_ with some caveats:

1.  Only a subset of the specification will be used.  The spec is rather large
    and some of it can be open for interpretation.

    This project will still be a *success* if one can generate code from the
    format used

2.  Even though ``JSON`` schema is described in ``JSON``, ``YAML`` will be used
    as the preferred *human readable* format for viewing these schemas.
