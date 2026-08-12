from sqlalchemy.orm import Session
from app.models import Unit


def to_metric_base(value: float, unit: Unit) -> tuple[float, str] | None:
    """
    Convert supported volumetric US units to the unit's metric base.
    Returns (value, metric_unit), e.g. (59.147, "ml").
    """
    if unit.metric_equivalent is None or unit.metric_unit is None:
        return None
    return value * unit.metric_equivalent, unit.metric_unit


def quantities_sufficient(
    db: Session,
    required_quantity: float | None,
    required_unit_id: int | None,
    available_quantity: float | None,
    available_unit_id: int | None,
) -> bool:
    # Unknown quantity means "assume enough" per V1 design.
    if available_quantity is None or required_quantity is None:
        return True

    # If one or both units are unknown, compare raw values conservatively.
    if required_unit_id is None or available_unit_id is None:
        return available_quantity >= required_quantity

    if required_unit_id == available_unit_id:
        return available_quantity >= required_quantity

    required_unit = db.get(Unit, required_unit_id)
    available_unit = db.get(Unit, available_unit_id)
    if not required_unit or not available_unit:
        return True

    required_metric = to_metric_base(required_quantity, required_unit)
    available_metric = to_metric_base(available_quantity, available_unit)

    if not required_metric or not available_metric:
        # Non-convertible units (dash, piece, etc.) are not cross-compared.
        return True

    required_value, required_metric_unit = required_metric
    available_value, available_metric_unit = available_metric
    if required_metric_unit != available_metric_unit:
        return True

    return available_value >= required_value
