import os
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


def draw_window(
    screen: pygame.Surface,
    circle_surface: pygame.Surface,
    circle_x: float,
    circle_y: float,
) -> None:
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

    screen.blit(circle_surface, (circle_x, circle_y))

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
        os._exit(1)

    global circle_velocity
    if keys_pressed[pygame.K_SPACE]:
        circle_velocity = jump_force


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

    # Circle surface
    circle_surface: pygame.Surface = pygame.Surface([100, 100])
    circle_surface.fill(BLACK)

    # Rectangle surface
    rectangle_surface: pygame.Surface = pygame.Surface([100, 100])
    rectangle_surface.fill(BLACK)

    # Initial position of the circle (bird)
    circle_y: int = 250

    # X position stays constant (like Flappy Bird)
    circle_x: int = SCREEN_WIDTH // 2 - 50

    # Falling speed (velocity)
    global circle_velocity
    circle_velocity = 0.0

    # Gravity that pulls the circle down
    gravity: float = 0.5

    # Force applied when jumping
    global jump_force
    jump_force = -10.0

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

        # Handle keys pressed
        handle_keys_pressed_event(keys_pressed)

        # Draw window
        draw_window(screen, circle_surface, circle_x, circle_y)

        # Apply gravity to velocity
        circle_velocity += gravity

        # Update circle's Y position based on velocity
        circle_y += circle_velocity

    # Look at the name
    pygame.display.quit()


if __name__ == "__main__":
    main()
