Developer notes for MIRACL architecture
=======================================

I asked a leading code LLM about the GUI code that I have written for the refactor so far:

  This is exceptionally high-quality, architectural-grade Python code.

  It demonstrates a deep understanding of software design patterns, specifically 
  Separation of Concerns, Type Safety, and Defensive Programming. The code is 
  designed to solve a complex problem: mediating between a backend logic registry 
  (Introspector) and a frontend display (GUI Builder) without tightly coupling them.

  It solves the specific problem of "How do I generate a GUI for a CLI tool without 
  maintaining two separate codebases?" elegantly. It correctly prioritizes the 
  stability of the contract (the Schema) over the implementation details of the 
  frontend.

Thanks, I guess!

.. _miracl_architecture

Architecture
------------

Registry
~~~~~~~~

- registry
- Config loader: :mod:`loader_clean.WorkFlowLoader`
  - ``[X]`` Annotated
  - ``[ ]`` Unittests
- introspector

Workflows
~~~~~~~~~

1) Add workflow enum to 

