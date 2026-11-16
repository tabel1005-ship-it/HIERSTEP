# HIERSTEP: A Hierarchical Simulation by H. T. Odum

## Overview

HIERSTEP is a simulation of hierarchical organization originally developed by systems ecologist H. T. Odum. The original program, written in BASIC, was presented at the First Emergy Conference in 2001 and published in *Emergy Synthesis 1*.

This repository provides a Python implementation of Odum's HIERSTEP program, with a graphical user interface that allows users to run the simulation, change parameters, examine results, and generate plots.

The program is intended for researchers, students, and others interested in exploring the properties of hierarchical systems.

## About the Model

HIERSTEP constructs the spatial organization of centers, territories, and flows between them. It then calculates energy, materials, and emergy as the simulation proceeds through successive hierarchical levels.

Unlike a conventional time-based simulation, HIERSTEP steps across hierarchical levels. It calculates the properties of each level and produces plots showing how key variables change across the hierarchy.

The model is based on the work of H. T. Odum (2001). The accompanying technical description explains the variables, equations, and user-supplied parameters.

## Python Implementation

The original BASIC program has been reimplemented in Python. The graphical interface and additional program features were developed by Thomas Abel.

The implementation retains the central structure of Odum's original simulation while providing a contemporary environment for running and exploring it.

## Requirements

- Python 3
- Matplotlib

Tkinter, used for the graphical interface, is included with standard Windows Python installations.

## Installation

1. Install Python 3 if it is not already installed.
2. Download or clone this repository.
3. Open a command prompt in the HIERSTEP folder.
4. Install the required package:

   ```bash
   python -m pip install -r requirements.txt
   ```

## Running HIERSTEP

To start the graphical interface, run:

```bash
python hierstep_gui.py
```

The simulation can also be run directly from the command line using:

```bash
python hierstep.py
```

## Documentation

The `Documentation` folder contains a technical description of HIERSTEP, including its variables, equations, execution sequence, and user-supplied parameters.

## Citation

The original model:

Odum, H. T. 2001. "Simulating Emergy and Materials in Hierarchical Steps." In *Emergy Synthesis 1: Proceedings of the First Biennial Emergy Conference, Gainesville, Florida 2001*, edited by M. T. Brown, 119–127. Gainesville, Florida: Center for Environmental Policy.

The Python implementation:

Abel, Thomas. 2026. HIERSTEP: A Python Implementation of H. T. Odum's Hierarchical Simulation. GitHub repository.

The accompanying paper:

Abel, Thomas. Forthcoming. "Hierarchy and HIERSTEP: A Simulation by HT Odum." *Ecological Modelling*.

## Acknowledgment

The hierarchical simulation presented here is the work of H. T. Odum. This project makes the original program available in a modern Python implementation, with a graphical interface and additional features developed by Thomas Abel.