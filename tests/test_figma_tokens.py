from figma_tokens import variables_to_tokens

SAMPLE = {
    "variableCollections": {
        "c1": {"name": "Color", "defaultModeId": "light"},
        "c2": {"name": "Font", "defaultModeId": "base"},
    },
    "variables": {
        "a": {
            "name": "brand/Integrand",
            "variableCollectionId": "c1",
            "valuesByMode": {"light": {"r": 0.345, "g": 0.769, "b": 0.867, "a": 1}},
        },
        "b": {
            "name": "result",
            "variableCollectionId": "c1",
            "valuesByMode": {"light": {"type": "VARIABLE_ALIAS", "id": "VariableID:1:2"}},
        },
        "c": {"name": "title-size", "variableCollectionId": "c2", "valuesByMode": {"base": 40}},
    },
}


def test_colours_become_hex_and_names_use_the_last_path_segment():
    assert variables_to_tokens(SAMPLE)["color"]["integrand"] == "#58C4DD"


def test_aliases_are_skipped():
    assert "result" not in variables_to_tokens(SAMPLE)["color"]


def test_numbers_pass_through_under_their_collection():
    assert variables_to_tokens(SAMPLE)["font"] == {"title-size": 40}
