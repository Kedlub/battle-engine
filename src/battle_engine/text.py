import random

import pygame

from .fonts import draw_text, draw_text_size

ColorTuple = tuple[int, int, int]


class StyledText:
    def __init__(
        self,
        text: str,
        color: ColorTuple,
        font_name: str,
        font_size: int,
        x: int,
        y: int,
        char_spacing: int = 0,
    ) -> None:
        self.text = text
        self.color = color
        self.font_name = font_name
        self.font_size = font_size
        self.x = x
        self.y = y
        self.char_spacing = char_spacing


class ProgressiveText:
    def __init__(
        self,
        target_text: str = "",
        max_width: int = 100,
        font_name: str = "default",
        font_size: int = 27,
        x: int = 0,
        y: int = 0,
        tick_length: int = 2,
        blip_sound: str | None = "txt_default",
    ) -> None:
        self.target_text = target_text
        self.current_text: str = ""
        self.max_width = max_width
        self.font_name = font_name
        self.font_size = font_size
        self.lines: list[str] = []
        self.x = x
        self.y = y
        self.color: ColorTuple = (255, 255, 255)
        self.tick_length = tick_length
        self.tick: int = 0
        self.finished: bool = False
        self.char_spacing: int = 2
        self.instant_command: bool = False
        self.asterisk: bool = False
        self.target_command_positions: dict[int, list[str]] = {}
        self.target_text_clean: str = ""
        self.blip_sound: str | None = blip_sound
        self._blip_channel: pygame.mixer.Channel | None = None
        self.set_text(target_text)

    def preprocess_target_text(
        self,
        target_text: str,
    ) -> tuple[dict[int, list[str]], str]:
        index = 0
        command_positions: dict[int, list[str]] = {}
        clean_text = ""

        while index < len(target_text):
            if target_text[index] == "[":
                command_start = index
                command_end = target_text.find("]", command_start)

                if command_end != -1:
                    commands = target_text[command_start + 1 : command_end].split("][")

                    if len(clean_text) not in command_positions:
                        command_positions[len(clean_text)] = []

                    for cmd in commands:
                        command_positions[len(clean_text)].append(cmd)

                    index = command_end + 1
                    continue

            clean_text += target_text[index]
            index += 1

        return command_positions, clean_text

    def update(self) -> None:
        if len(self.current_text) < len(self.target_text_clean):
            self.finished = False
            self.tick += 1
            if self.tick >= self.tick_length or self.instant_command:
                pos = len(self.current_text)
                char = self.target_text_clean[pos]
                self.current_text += char
                self.tick = 0

                # Process sound commands at this position
                cmd_list = self.target_command_positions.get(pos)
                if cmd_list:
                    for cmd in cmd_list:
                        if cmd.startswith("sound:"):
                            value = cmd.split(":", 1)[1]
                            self.blip_sound = None if value == "none" else value

                # Play blip on a dedicated channel so each new blip
                # cuts off the previous one (matches Undertale behavior)
                if self.blip_sound and not self.instant_command and not char.isspace():
                    from .sound import SoundManager

                    sm = SoundManager()
                    sound = sm._sounds.get(self.blip_sound)
                    if sound is not None:
                        if self._blip_channel is None:
                            self._blip_channel = pygame.mixer.find_channel()
                        if self._blip_channel is not None:
                            category = sm._categories.get(self.blip_sound)
                            if category is not None:
                                sound.set_volume(sm.get_volume(category))
                            self._blip_channel.play(sound)
        elif not self.finished:
            self.finished = True

    def draw(self, surface: pygame.Surface) -> None:
        styled_texts: list[StyledText] = []
        x_offset = self.x
        y_offset = self.y
        current_color = self.color
        current_font_name = self.font_name
        current_char_spacing = self.char_spacing

        for idx, char in enumerate(self.current_text):
            cmd_list = self.target_command_positions.get(idx)

            if cmd_list:
                for cmd in cmd_list:
                    key, value = cmd.split(":", 1) if ":" in cmd else (cmd, None)

                    if key == "color" and value is not None:
                        r, g, b = (int(value[i : i + 2], 16) for i in (0, 2, 4))
                        current_color = (r, g, b)
                    elif key == "font" and value is not None:
                        current_font_name = value
                    elif key == "charspacing" and value is not None:
                        current_char_spacing = int(value)
                    elif key == "sound":
                        pass  # handled in update()

            if char == "\n":
                line_height = draw_text_size(
                    "A", self.font_size, font_name=current_font_name
                )[1]
                x_offset = self.x
                y_offset += line_height
                continue

            char_width, char_height = draw_text_size(
                char, self.font_size, font_name=current_font_name
            )

            if char == " ":
                word_end_idx = self.current_text.find(" ", idx + 1)
                next_word = self.current_text[
                    idx + 1 : word_end_idx
                    if word_end_idx != -1
                    else len(self.current_text)
                ]
                next_word_width = draw_text_size(
                    next_word, self.font_size, font_name=current_font_name
                )[0]

                if x_offset + next_word_width > self.max_width:
                    x_offset = self.x
                    y_offset += char_height

            styled_text = StyledText(
                char,
                current_color,
                current_font_name,
                self.font_size,
                x_offset,
                y_offset,
            )
            styled_texts.append(styled_text)

            x_offset += char_width + current_char_spacing

        for styled_text in styled_texts:
            draw_text(
                surface,
                styled_text.text,
                styled_text.font_size,
                styled_text.color,
                styled_text.x,
                styled_text.y,
                font_name=styled_text.font_name,
            )

    def skip(self) -> None:
        self.current_text = self.target_text

    def set_text(self, text: str) -> None:
        self.target_text = text
        self.current_text = ""

        # Pick a concrete default blip variant for this text
        if self.blip_sound == "txt_default":
            self.blip_sound = random.choice(["txt_default1", "txt_default2"])

        if "[instant]" in self.target_text:
            self.instant_command = True
            self.target_text = self.target_text.replace("[instant]", "")

        if "[asterisk]" in self.target_text:
            self.asterisk = True
            self.target_text = self.target_text.replace("[asterisk]", "")

        self.target_command_positions, self.target_text_clean = (
            self.preprocess_target_text(self.target_text)
        )

        if self.instant_command:
            self.current_text = self.target_text_clean
