from __future__ import annotations


import random
import sys
import pygame


# Screen size and FPS Limits
FPS: float = 60.0
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
MAX_PIPE_HEIGHT: int = 100
PIPE_WIDTH: int = 80

# Colors
RED: tuple[int] = (255, 0, 0)
GREEN: tuple[int] = (0, 255, 0)
BLUE: tuple[int] = (0, 0, 255)
BLACK: tuple[int] = (0, 0, 0)
WHITE: tuple[int] = (255, 255, 255)


class Bird(object):
    """
    Represents the bird character in the game.

    Holds position, velocity, gravity, jump force and the drawing surface. Provides
    core behaviors: per-frame movement with gravity, jumping on input, and rendering.
    """

    def __init__(self: Bird, x: int, y: int, surface: pygame.Surface) -> None:
        """
        Initialize a bird instance.

        Args:
            x (int): Initial x coordinate in pixels.
            y (int): Initial y coordinate in pixels.
            surface (pygame.Surface): Surface used to render the bird.
        """
        self.__x = x
        self.__y = y
        self.__velocity = 0.0
        self.__gravity = 0.5
        self.__jump_force = -7.0
        self.__surface = surface

    def movement(self: Bird) -> None:
        """
        Update per-frame movement:
        - Apply gravity to velocity.
        - Update position by current velocity.
        - Clamp the bird within the top and bottom screen bounds.
        """
        self.__velocity += self.__gravity
        self.__y += self.__velocity

        # Prevent bird from falling below the screen
        if self.__y + self.__surface.get_height() >= SCREEN_HEIGHT:
            self.__y = SCREEN_HEIGHT - self.__surface.get_height()
            self.__velocity = 0.0

        #  Otherwise
        if self.__y <= 0:
            self.__y = 0

    def jump(self: Bird) -> None:
        """
        Trigger a jump by setting vertical velocity to a negative impulse.
        """
        self.__velocity = self.__jump_force

    def draw(self: Bird, screen: pygame.Surface) -> None:
        """
        Render the bird at its current position.

        Args:
            screen (pygame.Surface): The main display surface.
        """
        screen.blit(self.__surface, [self.__x, self.__y])

    @property
    def x(self: Bird) -> float:
        """Return the current x coordinate in pixels."""
        return self.__x

    @property
    def y(self: Bird) -> float:
        """Return the current y coordinate in pixels."""
        return self.__y

    @property
    def velocity(self: Bird) -> float:
        """Return the current vertical velocity in pixels per frame."""
        return self.__velocity


class Pipe(object):
    """
    Represents a pair of pipes (top and bottom) separated by a vertical gap.

    Each pipe pair has an x position, a width, a gap size, and a horizontal
    leftward speed. Two `pygame.Rect` objects are kept for drawing and collision.
    """

    def __init__(
        self: Pipe,
        x: int,
        width: float,
        gap: float,
        speed: float,
        color: tuple[int] = GREEN,
    ) -> None:
        """
        Initialize a pipe pair.

        Args:
            x (int): Initial x coordinate of the pipe pair in pixels.
            width (float): Width of each pipe in pixels.
            gap (float): Vertical gap between top and bottom pipes in pixels.
            speed (float): Leftward movement speed in pixels per frame.
            color (tuple[int]): RGB color of the pipes.
        """
        self.__x = x
        self.__width = width
        self.__gap = gap
        self.__speed = speed
        self.__color = color

        # Randomize the height of the top pipe
        self.__top_pipe_height = random.randint(
            MAX_PIPE_HEIGHT, SCREEN_HEIGHT - self.__gap - MAX_PIPE_HEIGHT
        )

        # Calculate the bottom pipe height
        self.__bottom_pipe_height = SCREEN_HEIGHT - self.__gap - self.__top_pipe_height

        # Create Rect objects for collision detection
        self.__top_pipe_rect = pygame.Rect(
            self.__x, 0, self.__width, self.__top_pipe_height
        )
        self.__bottom_pipe_rect = pygame.Rect(
            self.__x,
            self.__top_pipe_height + self.__gap,
            self.__width,
            self.__bottom_pipe_height,
        )

    def update(self: Pipe) -> None:
        """
        Advance the pipe pair leftward by its current speed and update rects.
        """
        # Move pipes to the left
        self.__x -= self.__speed

        # Update Rect positions
        self.__top_pipe_rect.x = self.__x
        self.__bottom_pipe_rect.x = self.__x

    def draw(self: Pipe, screen: pygame.Surface) -> None:
        """
        Draw the pipe pair to the screen.

        Args:
            screen (pygame.Surface): The main display surface.
        """
        # Draw the top pipe
        pygame.draw.rect(screen, GREEN, self.__top_pipe_rect)

        # Draw the bottom pipe
        pygame.draw.rect(screen, GREEN, self.__bottom_pipe_rect)

    @property
    def speed(self: Pipe) -> float:
        """Return the current leftward speed in pixels per frame."""
        return self.__speed

    @property
    def top_pipe_rect(self: Pipe) -> pygame.Rect:
        """Return the `pygame.Rect` for the top pipe (for draw/collision)."""
        return self.__top_pipe_rect

    @property
    def bottom_pipe_rect(self: Pipe) -> pygame.Rect:
        """Return the `pygame.Rect` for the bottom pipe (for draw/collision)."""
        return self.__bottom_pipe_rect


class PipeManager(object):
    """
    Manages the lifecycle of pipe pairs: initial spawn, updates, drawing,
    and respawning when pipes leave the screen.
    """

    def __init__(
        self: PipeManager, gap: int, pipe_width: int, speed: int, spawn_distance: int
    ) -> None:
        """
        Initialize the pipe manager.

        Args:
            gap (int): Vertical gap between top and bottom pipes in pixels.
            pipe_width (int): Pipe width in pixels.
            speed (int): Leftward movement speed in pixels per frame.
            spawn_distance (int): Horizontal distance between consecutive pipe pairs in pixels.
        """
        self.__pipes: list[Pipe] = []
        self.__gap: int = gap
        self.__pipe_width: int = pipe_width
        self.__speed: int = speed
        self.__spawn_distance: int = spawn_distance
        # Spawn timing based on distance and speed to keep even intervals
        self.__spawn_interval_frames: int = (
            int(self.__spawn_distance / self.__speed) if self.__speed > 0 else 60
        )
        self.__frames_since_last_spawn: int = 0

        # Spawn initial pipes off-screen to the right with even spacing
        start_x: int = SCREEN_WIDTH + 100
        initial_count: int = 3
        for i in range(initial_count):
            self.__pipes.append(
                Pipe(
                    start_x + i * self.__spawn_distance,
                    self.__pipe_width,
                    self.__gap,
                    self.__speed,
                )
            )

    def update(self: PipeManager) -> None:
        """
        Update all active pipes and manage timed spawning/removal.

        Details:
        - Move each pipe left every frame.
        - Spawn a new pipe at fixed frame intervals so spacing (and timing) is even.
        - Always remove pipes that have fully left the screen.
        """
        # Update all pipes
        for pipe in self.__pipes:
            pipe.update()

        # Timed spawning to keep intervals even
        self.__frames_since_last_spawn += 1
        if (
            self.__frames_since_last_spawn >= self.__spawn_interval_frames
            and self.__pipes
        ):
            last_x: int = self.__pipes[-1].top_pipe_rect.x
            new_x: int = max(last_x + self.__spawn_distance, SCREEN_WIDTH + 100)
            self.__pipes.append(
                Pipe(new_x, self.__pipe_width, self.__gap, self.__speed)
            )
            self.__frames_since_last_spawn = 0

        # Remove any pipes that are fully out of the screen (left side)
        while self.__pipes and self.__pipes[0].top_pipe_rect.right < 0:
            self.__pipes.pop(0)

    def draw(self: PipeManager, screen: pygame.Surface) -> None:
        """
        Draw all managed pipes to the screen in their current order.

        Args:
            screen (pygame.Surface): The main display surface.
        """
        for pipe in self.__pipes:
            pipe.draw(screen)


def draw_window(screen: pygame.Surface, pipe_manager: PipeManager) -> None:
    """
    Render and present the current frame of the game.

    Fills the background, draws pipes first so the bird appears on top, then draws
    the bird and flips the display buffer.

    Args:
        screen (pygame.Surface): The main display surface.
        pipe_manager (PipeManager): Manager responsible for drawing all pipes.
    """
    # Fill the screen with background
    screen.fill(WHITE)

    # Draw pipes first so the bird appears on top
    pipe_manager.draw(screen)

    # Draw bird to the screen
    bird.draw(screen)

    # Update the screen
    pygame.display.flip()


def handle_events(events: list[pygame.event.Event]) -> bool:
    """
    Process a batch of Pygame events (including quit events).

    Iterates through the received events; returns False to terminate the game loop
    if a QUIT event is encountered, otherwise returns True to continue.

    Args:
        events (list[pygame.event.Event]): Events to process.

    Returns:
        bool: False if quit requested; True to continue running.
    """
    for event in events:
        if event.type == pygame.QUIT:
            return False

    return True


def handle_keys_pressed_events(keys_pressed: pygame.key.ScancodeWrapper) -> None:
    """
    Handle keyboard state each frame.

    - ESC: exit the program immediately.
    - SPACE: make the bird jump.

    Args:
        keys_pressed (pygame.key.ScancodeWrapper): Pressed state of all keys.
    """
    if keys_pressed[pygame.K_ESCAPE]:
        sys.exit(1)

    if keys_pressed[pygame.K_SPACE]:
        bird.jump()


def main() -> None:
    """
    Initialize and run the main game loop for a minimal Flappy Bird.

    Sets up the display window and FPS clock, creates the bird and pipe manager,
    then runs the main loop:
    - Cap frame rate to `FPS`.
    - Fetch and handle events (terminate on quit).
    - Update bird motion and pipe positions.
    - Handle key states (ESC to exit, SPACE to jump).
    - Render the current frame.

    The loop continues until exit; then the display module is shut down.
    """
    pygame.display.init()

    running: bool = True

    screen: pygame.Surface = pygame.display.set_mode([SCREEN_WIDTH, SCREEN_HEIGHT])
    pygame.display.set_caption("Flappy Bird")

    clock: pygame.time.Clock = pygame.time.Clock()

    BIRD_SIZE: int = 50

    # Bird surface
    bird_surface: pygame.Surface = pygame.Surface([BIRD_SIZE, BIRD_SIZE])
    bird_surface.fill(BLACK)
    pygame.draw.circle(bird_surface, GREEN, [BIRD_SIZE // 2, BIRD_SIZE // 2], 20)

    pipe_manager: PipeManager = PipeManager(
        gap=200, pipe_width=80, speed=4, spawn_distance=300
    )

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

        pipe_manager.update()

        # Handle keys pressed
        handle_keys_pressed_events(keys_pressed)

        # Draw window
        draw_window(screen, pipe_manager)

    # Look at the name
    pygame.display.quit()


if __name__ == "__main__":
    main()
