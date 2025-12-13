import pytest
from services.tx_processor import SimplifiedRecord


@pytest.fixture
def record():
    return SimplifiedRecord(
        details="Payment for invoice",
        recipient="ACME Corp",
        operation_amount=123.45,
        sender="",
        sender_account="",
        recipient_account="PL123",
        date=None,  # type: ignore
        amount=123.45
    )


def test_pretty_print_default_includes_all_fields(record):
    output = record.pretty_print()

    assert "details: Payment for invoice" in output
    assert "sender: " in output          # puste też są
    assert "operation_amount: 123.45" in output


def test_pretty_print_only_meaningful(record):
    output = record.pretty_print(only_meaningful=True)

    assert "details: Payment for invoice" in output
    assert "recipient: ACME Corp" in output
    assert "operation_amount: 123.45" in output

    assert "sender:" not in output
    assert "sender_account:" not in output


def test_pretty_print_include_whitelist(record):
    output = record.pretty_print(
        include={"details", "operation_amount"}
    )

    assert output == (
        "details: Payment for invoice\n"
        "operation_amount: 123.45"
    )


def test_pretty_print_exclude_blacklist(record):
    output = record.pretty_print(
        exclude={"sender", "sender_account"}
    )

    assert "sender:" not in output
    assert "sender_account:" not in output
    assert "recipient_account: PL123" in output


def test_include_has_priority_over_only_meaningful(record):
    output = record.pretty_print(
        include={"sender"},
        only_meaningful=True
    )

    # include mówi „drukuj”, nawet jeśli puste
    assert output == "sender: "
