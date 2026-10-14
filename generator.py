"""Synthetic XRF-like spectrum generation for the AMD MindOre AI MVP."""

from __future__ import annotations

from typing import Any

import numpy as np


ENERGY_MIN_KEV = 0.0
ENERGY_MAX_KEV = 10.0
SPECTRUM_POINTS = 100


def _gaussian_peak(energy: np.ndarray, center: float, amplitude: float, width: float) -> np.ndarray:
	"""Return a Gaussian emission line evaluated over the scan window."""
	return amplitude * np.exp(-0.5 * ((energy - center) / width) ** 2)


def generar_muestra_espectral(id_muestra: str, tipo_mineral: str) -> dict[str, Any]:
	"""Generate a synthetic 0-10 keV spectrum and representative assay grades.

	The requested arsenic K-beta line at 11.7 keV is modeled but falls outside
	this MVP's 0-10 keV scan window, so it is not visible in the sampled data.
	"""
	if tipo_mineral not in {"Cu_alto", "Estéril", "Arsénico_Alto"}:
		raise ValueError(
			"tipo_mineral debe ser 'Cu_alto', 'Estéril' o 'Arsénico_Alto'."
		)

	rng = np.random.default_rng()
	energy = np.linspace(ENERGY_MIN_KEV, ENERGY_MAX_KEV, SPECTRUM_POINTS)
	signal = np.full(SPECTRUM_POINTS, 0.025)

	# Shared iron response and mineral-specific emission lines.
	signal += _gaussian_peak(energy, center=6.40, amplitude=0.22, width=0.10)
	if tipo_mineral == "Cu_alto":
		signal += _gaussian_peak(energy, center=8.04, amplitude=1.8, width=0.12)
		simulated_grades = {
			"Cu_pct": round(float(rng.uniform(1.0, 2.5)), 3),
			"Fe_pct": round(float(rng.uniform(2.0, 8.0)), 3),
			"Au_gpt": round(float(rng.uniform(0.05, 0.8)), 3),
			"As_pct": round(float(rng.uniform(0.01, 0.25)), 3),
		}
	elif tipo_mineral == "Arsénico_Alto":
		signal += _gaussian_peak(energy, center=11.70, amplitude=2.2, width=0.16)
		simulated_grades = {
			"Cu_pct": round(float(rng.uniform(0.02, 0.35)), 3),
			"Fe_pct": round(float(rng.uniform(1.0, 6.0)), 3),
			"Au_gpt": round(float(rng.uniform(0.0, 0.3)), 3),
			"As_pct": round(float(rng.uniform(0.6, 2.0)), 3),
		}
	else:
		signal += _gaussian_peak(energy, center=8.04, amplitude=0.045, width=0.15)
		simulated_grades = {
			"Cu_pct": round(float(rng.uniform(0.0, 0.15)), 3),
			"Fe_pct": round(float(rng.uniform(0.1, 1.5)), 3),
			"Au_gpt": round(float(rng.uniform(0.0, 0.05)), 3),
			"As_pct": round(float(rng.uniform(0.0, 0.1)), 3),
		}

	# Gaussian detector/thermal noise; clamp at zero because counts cannot be negative.
	intensity = np.clip(signal + rng.normal(0.0, 0.018, SPECTRUM_POINTS), 0.0, None)
	spectral_wave = [
		{"energy_keV": round(float(x), 4), "intensity": round(float(y), 6)}
		for x, y in zip(energy, intensity)
	]

	return {
		"sample_id": str(id_muestra),
		"mineral_type": tipo_mineral,
		"spectral_wave": spectral_wave,
		"simulated_grades": simulated_grades,
	}
