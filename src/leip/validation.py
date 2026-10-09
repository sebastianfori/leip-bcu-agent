from .agent import Extraction, reference_extraction


def validate(extraction: Extraction, table: dict) -> None:
    expected = {o.cell_id: o.model_dump() for o in reference_extraction(table).observations}
    actual = {o.cell_id: o.model_dump() for o in extraction.observations}
    if len(actual) != len(extraction.observations) or actual != expected:
        raise ValueError("La extracción no coincide en cobertura, valor, semántica o evidencia con las celdas de la fuente.")
