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


class Bird(pygame.sprite.Sprite):
    """
    Represents the bird character in the game.
    
    Inherits from pygame.sprite.Sprite for collision detection.
    """

    def __init__(self: Bird, x: int, y: int, surface: pygame.Surface) -> None:
        """
        Initialize a bird instance.

        Args:
            x (int): Initial x coordinate in pixels.
            y (int): Initial y coordinate in pixels.
            surface (pygame.Surface): Surface used to render the bird.
        """
        super().__init__()
        self.__x = x
        self.__y = y
        self.__velocity = 0.0
        self.__gravity = 0.5
        self.__jump_force = -7.0
        self.__surface = surface
        
        # Set up the sprite's rect for collision detection
        self.rect = self.__surface.get_rect()
        self.rect.x = x
        self.rect.y = y

    def movement(self: Bird) -> None:
        """
        Update per-frame movement:
        - Apply gravity to velocity.
        - Update position by current velocity.
        - Clamp the bird within the top and bottom screen bounds.
        - Update the sprite's rect position.
        """
        self.__velocity += self.__gravity
        self.__y += self.__velocity

        # Prevent bird from falling below the screen
        if self.__y + self.__surface.get_height() >= SCREEN_HEIGHT:
            self.__y = SCREEN_HEIGHT - self.__surface.get_height()
            self.__velocity = 0.0

        # Prevent bird from going above the screen
        if self.__y <= 0:
            self.__y = 0
            
        # Update the sprite's rect position
        self.rect.x = self.__x
        self.rect.y = self.__y

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


class Pipe(pygame.sprite.Sprite):
    """
    Represents a single pipe (top or bottom) for collision detection.
    
    Inherits from pygame.sprite.Sprite for collision detection.
    """

    def __init__(
        self: Pipe,
        x: int,
        y: int,
        width: float,
        height: float,
        speed: float,
        color: tuple[int] = GREEN,
    ) -> None:
        """
        Initialize a pipe.

        Args:
            x (int): Initial x coordinate of the pipe in pixels.
            y (int): Initial y coordinate of the pipe in pixels.
            width (float): Width of the pipe in pixels.
            height (float): Height of the pipe in pixels.
            speed (float): Leftward movement speed in pixels per frame.
            color (tuple[int]): RGB color of the pipe.
        """
        super().__init__()
        self.__x = x
        self.__y = y
        self.__width = width
        self.__height = height
        self.__speed = speed
        self.__color = color

        # Set up the sprite's rect for collision detection
        self.rect = pygame.Rect(x, y, width, height)

    def update(self: Pipe) -> None:
        """
        Advance the pipe leftward by its current speed and update rect.
        """
        # Move pipe to the left
        self.__x -= self.__speed
        
        # Update Rect position
        self.rect.x = self.__x

    def draw(self: Pipe, screen: pygame.Surface) -> None:
        """
        Draw the pipe to the screen.

        Args:
            screen (pygame.Surface): The main display surface.
        """
        pygame.draw.rect(screen, self.__color, self.rect)

    @property
    def speed(self: float) -> float:
        """Return the current leftward speed in pixels per frame."""
        return self.__speed


class PipePair:
    """
    Manages a pair of pipes (top and bottom) separated by a vertical gap.
    
    This class creates and manages two Pipe sprites for collision detection.
    """

    def __init__(
        self: PipePair,
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

        # Create Pipe sprites for collision detection
        self.top_pipe = Pipe(
            self.__x, 0, self.__width, self.__top_pipe_height, self.__speed, self.__color
        )
        self.bottom_pipe = Pipe(
            self.__x,
            self.__top_pipe_height + self.__gap,
            self.__width,
            self.__bottom_pipe_height,
            self.__speed,
            self.__color,
        )

    def update(self: PipePair) -> None:
        """
        Update both pipes in the pair.
        """
        self.top_pipe.update()
        self.bottom_pipe.update()

    def draw(self: PipePair, screen: pygame.Surface) -> None:
        """
        Draw both pipes in the pair to the screen.

        Args:
            screen (pygame.Surface): The main display surface.
        """
        self.top_pipe.draw(screen)
        self.bottom_pipe.draw(screen)

    def get_pipes(self: PipePair) -> tuple[Pipe, Pipe]:
        """
        Return the top and bottom pipe sprites.
        
        Returns:
            tuple[Pipe, Pipe]: Top and bottom pipe sprites.
        """
        return self.top_pipe, self.bottom_pipe


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
        self.__pipes: list[PipePair] = []
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
                PipePair(
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
            last_x: int = self.__pipes[-1].top_pipe.rect.x
            new_x: int = max(last_x + self.__spawn_distance, SCREEN_WIDTH + 100)
            self.__pipes.append(
                PipePair(new_x, self.__pipe_width, self.__gap, self.__speed)
            )
            self.__frames_since_last_spawn = 0

        # Remove any pipes that are fully out of the screen (left side)
        while self.__pipes and self.__pipes[0].top_pipe.rect.right < 0:
            self.__pipes.pop(0)

    def draw(self: PipeManager, screen: pygame.Surface) -> None:
        """
        Draw all managed pipes to the screen in their current order.

        Args:
            screen (pygame.Surface): The main display surface.
        """
        for pipe in self.__pipes:
            pipe.draw(screen)
            
    def get_all_pipe_sprites(self: PipeManager) -> list[Pipe]:
        """
        Get all individual pipe sprites for collision detection.
        
        Returns:
            list[Pipe]: List of all pipe sprites.
        """
        all_sprites = []
        for pipe_pair in self.__pipes:
            top_pipe, bottom_pipe = pipe_pair.get_pipes()
            all_sprites.append(top_pipe)
            all_sprites.append(bottom_pipe)
        return all_sprites


def check_collisions(bird: Bird, pipe_manager: PipeManager) -> bool:
    """
    Check for collisions between the bird and any pipes.
    
    Args:
        bird (Bird): The bird sprite to check collisions for.
        pipe_manager (PipeManager): Manager containing all pipe sprites.
        
    Returns:
        bool: True if collision detected, False otherwise.
    """
    # Get all pipe sprites
    pipe_sprites = pipe_manager.get_all_pipe_sprites()
    
    # Check for collision using pygame's sprite collision detection
    if pygame.sprite.spritecollideany(bird, pipe_sprites):
        return True
    
    return False


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
        
        # Check for collisions
        if check_collisions(bird, pipe_manager):
            print("Game Over! Collision detected!")
            running = False

        # Draw window
        draw_window(screen, pipe_manager)

    # Look at the name
    pygame.display.quit()


if __name__ == "__main__":
    main()
