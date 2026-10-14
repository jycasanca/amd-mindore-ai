# AMD MindOre AI

**Track:** Intelligent Industry | **Hackathon:** AMD

AMD MindOre AI is a real-time mineral characterization and sorting MVP. It
simulates X-ray fluorescence (XRF) measurements, estimates representative
mineral grades, and recommends a downstream route before material reaches
energy-intensive processing stages.

## System Architecture

The prototype uses a small multi-agent pipeline with clear component
boundaries:

1. **Spectral Generator** (`generator.py`) simulates a 100-point XRF response
	over 0-10 keV, including detector noise and representative Cu, Fe, and As
	grades.
2. **Characterization and Routing Agent** (`agent.py`) evaluates the simulated
	assay against transparent metallurgical thresholds and returns a decision
	with its justification. Its stable interface is designed to support a
	future LLM-backed implementation using vLLM on AMD GPU infrastructure.
3. **Operator Dashboard** (`app.py`) lets users select a rock type, trigger a
	scan, inspect its spectrum and assay, and review the routing recommendation.

This is a simulation for demonstration, not a certified assay or autonomous
plant-control system. The requested arsenic line at 11.7 keV is outside the
current 0-10 keV scan window; a production instrument would need a wider scan
range to observe it directly. In this MVP, the simulated As grade still drives
the high-penalty routing rule.

## Installation

Python 3.9 or newer is recommended.

```bash
pip install streamlit matplotlib numpy
```

## Run

```bash
streamlit run app.py
```

## Intelligent Industry Impact

Grinding and classification consume a substantial share of a mine's operating
energy. Early characterization can help route high-grade ore to the
concentrator, marginal material to leaching, and waste or penalty-bearing
material away from unnecessary processing. In a deployed system, this
decision-support loop could reduce avoidable comminution and improve energy
used per unit of recovered metal. The actual savings depend on orebody,
instrument performance, plant configuration, and recovery trade-offs; they
must be measured in a site pilot rather than assumed from this simulation.
