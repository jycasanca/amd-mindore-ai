"""Decision agent for routing mineral samples to downstream processes."""

from __future__ import annotations

from typing import Any


class MiningAgent:
    """Apply transparent metallurgical routing rules to a sample assay.

    The public analyze_spectrum interface can later delegate to an LLM API
    (for example vLLM on an AMD GPU) without changing the Streamlit client.
    """

    def analyze_spectrum(self, sample_data: dict[str, Any]) -> dict[str, str]:
        """Return a routing decision and a concise explanation for a sample."""
        grades = sample_data.get("simulated_grades", {})
        try:
            arsenic_pct = float(grades["As_pct"])
            copper_pct = float(grades["Cu_pct"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(
                "sample_data debe incluir leyes numéricas 'As_pct' y 'Cu_pct'."
            ) from exc

        # Keep decision policy behind this method so an LLM-backed policy can
        # replace it while preserving the input/output contract.
        if arsenic_pct > 0.5:
            decision = "DESVIAR A DEPOSITO DE ALTA PENALIZACIÓN"
            justification = (
                f"El arsénico ({arsenic_pct:.3f} % As) supera 0.5 %; "
                "se evita contaminación y penalización económica."
            )
        elif copper_pct >= 1.0:
            decision = "ENVIAR A PLANTA CONCENTRADORA (MOLIENDA)"
            justification = (
                f"La ley de cobre ({copper_pct:.3f} % Cu) es igual o superior "
                "a 1.0 %, por lo que se prioriza la concentración."
            )
        elif copper_pct >= 0.2:
            decision = "ENVIAR A PAD DE LIXIVIACIÓN"
            justification = (
                f"La ley de cobre ({copper_pct:.3f} % Cu) está entre 0.2 % y "
                "1.0 %; se deriva a lixiviación para mineral marginal."
            )
        else:
            decision = "BOTADERO (DESMONTE/ESTÉRIL)"
            justification = (
                f"La ley de cobre ({copper_pct:.3f} % Cu) es inferior a 0.2 % "
                "y no justifica procesamiento."
            )

        return {"decision": decision, "justification": justification}