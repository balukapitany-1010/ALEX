import pytest

from alex.esg.domain.option import Option


def test_option_can_be_created():
    option = Option(
        option_id="3737695_1",
        label="Igen",
    )

    assert option.option_id == "3737695_1"
    assert option.label == "Igen"


def test_option_rejects_empty_option_id():
    with pytest.raises(ValueError):
        Option(
            option_id="",
            label="Igen",
        )




def test_option_rejects_empty_label():
    with pytest.raises(ValueError):
        Option(
            option_id="3737695_1",
            label="",
        )