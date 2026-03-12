import pygame


def draw_gradient(
    surface: pygame.Surface,
    alpha: int,
    num_blocks: int,
    color: tuple[int, int, int],
    max_height: float,
) -> None:
    width = surface.get_width()
    height = surface.get_height()
    block_height = max_height / num_blocks
    for index in range(num_blocks):
        color_a = (color[0], color[1], color[2], alpha)
        rect = pygame.Surface((width, height / 2), pygame.SRCALPHA)
        rect.fill(color_a)
        surface.blit(
            rect, (0, height - max_height + block_height * index + block_height)
        )
