import pygame

from battle_engine.text import ProgressiveText, StyledText


def setup_module():
    pygame.init()


def test_styled_text_attributes():
    st = StyledText("A", (255, 0, 0), "default", 16, 10, 20, char_spacing=3)
    assert st.text == "A"
    assert st.color == (255, 0, 0)
    assert st.char_spacing == 3


def test_progressive_text_instant():
    pt = ProgressiveText(target_text="[instant]Hello")
    assert pt.instant_command is True
    assert pt.current_text == "Hello"
    assert pt.finished is False


def test_progressive_text_incremental():
    pt = ProgressiveText(target_text="Hi", tick_length=1)
    assert pt.current_text == ""

    pt.update()
    assert pt.current_text == "H"

    pt.update()
    assert pt.current_text == "Hi"


def test_progressive_text_finished():
    pt = ProgressiveText(target_text="AB", tick_length=1)
    pt.update()  # A
    pt.update()  # B
    assert not pt.finished
    pt.update()  # finalize
    assert pt.finished


def test_progressive_text_skip():
    pt = ProgressiveText(target_text="Hello World")
    pt.skip()
    assert pt.current_text == "Hello World"


def test_progressive_text_set_text_resets():
    pt = ProgressiveText(target_text="First", tick_length=1)
    pt.update()
    pt.set_text("Second")
    assert pt.current_text == ""


def test_progressive_text_command_stripping():
    pt = ProgressiveText(target_text="[color:FF0000]Red", tick_length=1)
    assert pt.target_text_clean == "Red"


def test_progressive_text_asterisk():
    pt = ProgressiveText(target_text="[asterisk]Hello")
    assert pt.asterisk is True
    assert pt.target_text_clean == "Hello"
