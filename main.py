from __future__ import annotations


import sys
import pygame


# Screen size and FPS Limits
FPS: float = 60.0
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600

# Colors
RED: tuple[int] = (255, 0, 0)
GREEN: tuple[int] = (0, 255, 0)
BLUE: tuple[int] = (0, 0, 255)
BLACK: tuple[int] = (0, 0, 0)
WHITE: tuple[int] = (255, 255, 255)


class Bird(object):
    def __init__(self: Bird, x: int, y: int, surface: pygame.Surface) -> None:
        self.__x = x
        self.__y = y
        self.__velocity = 0.0
        self.__gravity = 0.5
        self.__jump_force = -10.0
        self.__surface = surface

    def movement(self: Bird) -> None:
        self.__velocity += self.__gravity
        self.__y += self.__velocity

        # Clamp: Prevent bird from falling below the screen
        if self.__y + self.__surface.get_height() >= SCREEN_HEIGHT:
            self.__y = SCREEN_HEIGHT - self.__surface.get_height()
            self.__velocity = 0.0

        if self.__y <= 0:
            self.__y = 0

    def jump(self: Bird) -> None:
        self.__velocity = self.__jump_force

    def draw(self: Bird, screen: pygame.Surface) -> None:
        screen.blit(self.__surface, [self.__x, self.__y])

    @property
    def x(self: Bird) -> float:
        return self.__x

    @property
    def y(self: Bird) -> float:
        return self.__y

    @property
    def velocity(self: Bird) -> float:
        return self.__velocity


def draw_window(screen: pygame.Surface) -> None:
    """
    Draws and updates the game window with the current frame content.

    This function fills the entire screen with a solid blue color and updates
    the display to reflect the changes. It serves as the main rendering function
    in the game loop and can be extended to draw additional game elements.

    Args:
        screen (pygame.Surface): The main Pygame surface representing the window
            where all rendering operations are drawn.
    """
    # Fill the screen with blue
    screen.fill(BLUE)

    # Draw bird to the screen
    bird.draw(screen)

    # Update the screen
    pygame.display.flip()


def handle_events(events: list[pygame.event.Event]) -> bool:
    """
    Processes a list of Pygame events, including quitting and general input handling.

    This function iterates through the provided list of Pygame events to handle
    general game-related events such as quitting the application, key presses,
    mouse clicks, or other custom-defined event types.

    Args:
        events (list[pygame.event.Event]): A list of Pygame events to process.

    Returns:
        bool: False if a QUIT event is detected (to signal game termination),
              True otherwise (to continue the game loop).
    """
    for event in events:
        if event.type == pygame.QUIT:
            return False

    return True


def handle_keys_pressed_event(keys_pressed: pygame.key.ScancodeWrapper) -> None:
    """
    Handles keyboard input for specific keys during the game loop.

    Args:
        keys_pressed (pygame.key.ScancodeWrapper): An object representing the current state
        of all keyboard keys, where each key is either True (pressed) or False (not pressed).
    """
    if keys_pressed[pygame.K_ESCAPE]:
        sys.exit(1)

    if keys_pressed[pygame.K_SPACE]:
        bird.jump()


def main() -> None:
    """
    Initializes and runs the main game loop for the Flappy Bird game.

    This function sets up the game window, initializes Pygame's display module,
    and enters the main loop that:
    - Limits the frame rate to a fixed FPS.
    - Handles system and user-generated events (e.g., quit).
    - Processes keypress events (e.g., ESC to exit).
    - Renders the game window.

    The loop continues until a quit event is detected or ESC is pressed,
    at which point the Pygame display is properly shut down.
    """
    pygame.display.init()

    running: bool = True

    screen: pygame.Surface = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption("Flappy Bird")

    clock: pygame.time.Clock = pygame.time.Clock()

    SIZE: int = 100

    bird_surface: pygame.Surface = pygame.Surface([SIZE, SIZE])
    bird_surface.fill(BLACK)
    pygame.draw.circle(bird_surface, GREEN, [SIZE // 2, SIZE // 2], 30)

    # Initialize Bird object
    global bird
    bird = Bird(70, 90, bird_surface)

    # Game loop
    while running:
        # Set the FPS to 60
        clock.tick(FPS)

        # Get events
        events: list[pygame.event.Event] = pygame.event.get()

        # Handle events
        running = handle_events(events)

        # Get keys pressed
        keys_pressed: pygame.key.ScancodeWrapper = pygame.key.get_pressed()

        # Movement
        bird.movement()

        # Handle keys pressed
        handle_keys_pressed_event(keys_pressed)

        # Draw window
        draw_window(screen)

    # Look at the name
    pygame.display.quit()


if __name__ == "__main__":
    main()
