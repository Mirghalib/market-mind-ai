"""Tests for the JSONValidator module."""
import copy

import pytest

from app.services.ai.exceptions import ValidationError
from app.services.ai.validators.json_validator import JSONValidator, ValidationErrorItem
from tests.sample_data import VALID_MARKETING_STRATEGY


@pytest.fixture
def validator() -> JSONValidator:
    return JSONValidator()


@pytest.fixture
def valid_data() -> dict:
    return copy.deepcopy(VALID_MARKETING_STRATEGY)


def test_valid_payload_passes(validator: JSONValidator, valid_data: dict) -> None:
    result = validator.validate(valid_data)

    assert result["marketingStrategy"]["overview"] == "Test strategy"


def test_valid_payload_returns_data_unchanged(
    validator: JSONValidator, valid_data: dict
) -> None:
    result = validator.validate(valid_data)

    assert result == valid_data


def test_missing_top_level_section_is_reported(
    validator: JSONValidator, valid_data: dict
) -> None:
    del valid_data["recommendedTools"]

    with pytest.raises(ValidationError) as excinfo:
        validator.validate(valid_data)

    errors = excinfo.value.errors
    assert any(
        e.field == "recommendedTools" and e.error_type == "missing_field"
        for e in errors
    )


def test_missing_nested_field_is_reported(
    validator: JSONValidator, valid_data: dict
) -> None:
    del valid_data["customerPersona"]["painPoints"]

    with pytest.raises(ValidationError) as excinfo:
        validator.validate(valid_data)

    errors = excinfo.value.errors
    assert any(
        e.field == "customerPersona.painPoints" and e.error_type == "missing_field"
        for e in errors
    )


def test_all_missing_fields_are_reported_individually(validator: JSONValidator) -> None:
    with pytest.raises(ValidationError) as excinfo:
        validator.validate({})

    errors = excinfo.value.errors
    missing = [e for e in errors if e.error_type == "missing_field"]

    # Every required top-level section must be reported (and cascade
    # down to the nested required fields, so > 18 missing_field items).
    top_level = [e.field for e in missing if "." not in e.field]
    assert set(top_level) == {
        "executiveSummary",
        "marketingScore",
        "marketingStrategy",
        "customerPersona",
        "swotAnalysis",
        "marketOverview",
        "seoKeywords",
        "contentCalendar",
        "advertisementIdeas",
        "emailCampaign",
        "socialMediaStrategy",
        "competitorAnalysis",
        "implementationRoadmap",
        "weeklyMilestones",
        "estimatedROI",
        "riskMitigation",
        "finalRecommendations",
        "recommendedTools",
        "businessAnalysis",
        "marketingFunnel",
        "influencerStrategy",
        "growthOpportunities",
        "futureScaling",
    }
    assert len(missing) > 18


def test_missing_new_section_is_reported(
    validator: JSONValidator, valid_data: dict
) -> None:
    del valid_data["estimatedROI"]

    with pytest.raises(ValidationError) as excinfo:
        validator.validate(valid_data)

    errors = excinfo.value.errors
    assert any(
        e.field == "estimatedROI" and e.error_type == "missing_field"
        for e in errors
    )


def test_unexpected_field_is_reported(validator: JSONValidator, valid_data: dict) -> None:
    valid_data["hackedField"] = "x"

    with pytest.raises(ValidationError) as excinfo:
        validator.validate(valid_data)

    errors = excinfo.value.errors
    assert any(
        e.field == "hackedField" and e.error_type == "unexpected_field"
        for e in errors
    )


def test_wrong_type_is_reported_with_full_path(
    validator: JSONValidator, valid_data: dict
) -> None:
    valid_data["marketingStrategy"]["budgetAllocation"][0]["percentage"] = "100"

    with pytest.raises(ValidationError) as excinfo:
        validator.validate(valid_data)

    errors = excinfo.value.errors
    assert any(
        e.field == "marketingStrategy.budgetAllocation.0.percentage"
        and e.error_type == "wrong_type"
        for e in errors
    )


def test_enum_mismatch_is_reported(validator: JSONValidator, valid_data: dict) -> None:
    valid_data["marketingStrategy"]["channels"][0]["priority"] = "critical"

    with pytest.raises(ValidationError) as excinfo:
        validator.validate(valid_data)

    errors = excinfo.value.errors
    assert any(
        e.field == "marketingStrategy.channels.0.priority"
        and e.error_type == "invalid_value"
        for e in errors
    )


def test_non_object_input_is_rejected(validator: JSONValidator) -> None:
    with pytest.raises(ValidationError) as excinfo:
        validator.validate(["not", "an", "object"])

    first = excinfo.value.errors[0]
    assert first.error_type == "wrong_type"
    assert first.field == "<root>"


def test_find_errors_returns_structured_items_without_raising(
    validator: JSONValidator, valid_data: dict
) -> None:
    del valid_data["swotAnalysis"]

    errors = validator.find_errors(valid_data)

    assert errors
    assert all(isinstance(e, ValidationErrorItem) for e in errors)
    first = errors[0]
    assert first.field and first.error_type and first.message
