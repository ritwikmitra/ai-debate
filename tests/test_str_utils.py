from ai_debate.utils import list_to_str


def test_list_to_str_joins_items_with_newlines():
    assert list_to_str(["first", "second"]) == "first\nsecond"


def test_list_to_str_handles_empty_lists():
    assert list_to_str([]) == ""
