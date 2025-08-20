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
BUTTON_WIDTH: int = 220
BUTTON_HEIGHT: int = 60
BUTTON_SPACING: int = 20

# Colors
RED: tuple[int] = (255, 0, 0)
GREEN: tuple[int] = (0, 255, 0)
BLUE: tuple[int] = (0, 0, 255)
BLACK: tuple[int] = (0, 0, 0)
WHITE: tuple[int] = (255, 255, 255)


# Game states
class GameState:
    MENU = "menu"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    CONFIRM_EXIT_MENU = "confirm_exit_menu"
    CONFIRM_EXIT_GAME_OVER = "confirm_exit_game_over"


# Score system
class ScoreManager:
    def __init__(self):
        self.score = 0
        self.high_score = 0

    def increment_score(self):
        self.score += 1

    def reset_score(self):
        self.score = 0

    def update_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score


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
            self.__x,
            0,
            self.__width,
            self.__top_pipe_height,
            self.__speed,
            self.__color,
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

    def reset(self: PipeManager) -> None:
        """
        Reset the pipe manager to initial state.
        """
        self.__pipes.clear()
        self.__frames_since_last_spawn = 0

        # Spawn initial pipes
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


def draw_score(screen: pygame.Surface, score_manager: ScoreManager) -> None:
    """
    Draw the current score in the top left corner.

    Args:
        screen (pygame.Surface): The main display surface.
        score_manager (ScoreManager): The score manager containing current score.
    """
    # Initialize font module if not already done
    if not pygame.font.get_init():
        pygame.font.init()

    try:
        font = pygame.font.SysFont("arial", 36)
    except:
        try:
            font = pygame.font.Font(None, 36)
        except:
            font = None

    if font:
        score_text = font.render(f"Score: {score_manager.score}", True, BLACK)
        screen.blit(score_text, (20, 20))
    else:
        # Draw simple score indicator if font fails
        pygame.draw.rect(screen, BLACK, (20, 20, 100, 30))


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


def draw_game_over_menu(screen: pygame.Surface, score_manager: ScoreManager) -> None:
    """
    Draw the game over menu with restart and exit options.

    Args:
        screen (pygame.Surface): The main display surface.
        score_manager (ScoreManager): The score manager containing final score.
    """
    # Semi-transparent overlay to dim the background but keep consistency in button style
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))

    # Initialize font module if not already done
    if not pygame.font.get_init():
        pygame.font.init()

    # Game over text
    try:
        font = pygame.font.SysFont("arial", 55)
    except:
        try:
            font = pygame.font.Font(None, 55)
        except:
            # Fallback: create a simple text surface without custom font
            font = None

    if font:
        game_over_text = font.render("GAME OVER", True, RED)
        text_rect = game_over_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 150)
        )
        screen.blit(game_over_text, text_rect)

        # Final score text
        score_text = font.render(f"Final Score: {score_manager.score}", True, WHITE)
        score_rect = score_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80)
        )
        screen.blit(score_text, score_rect)

        # High score text
        high_score_text = font.render(
            f"High Score: {score_manager.high_score}", True, WHITE
        )
        high_score_rect = high_score_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20)
        )
        screen.blit(high_score_text, high_score_rect)
    else:
        # Draw simple text using basic shapes if font fails
        pygame.draw.rect(
            screen, RED, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 200, 300, 50)
        )
        pygame.draw.rect(
            screen, WHITE, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 130, 300, 50)
        )
        pygame.draw.rect(
            screen, WHITE, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 - 70, 300, 50)
        )

    # Buttons (consistent with main menu style)
    buttons = _get_game_over_button_rects()
    mouse_pos = pygame.mouse.get_pos()

    for name, rect in buttons.items():
        is_hovered = rect.collidepoint(mouse_pos)
        base_color = (70, 130, 180)  # steel blue
        hover_color = (100, 149, 237)  # cornflower blue
        color = hover_color if is_hovered else base_color
        pygame.draw.rect(screen, color, rect, border_radius=8)

        # Button text
        try:
            btn_font = pygame.font.SysFont("arial", 36)
        except:
            try:
                btn_font = pygame.font.Font(None, 36)
            except:
                btn_font = None

        if btn_font:
            label = "Restart" if name == "restart" else "Exit"
            text_surf = btn_font.render(label, True, WHITE)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)


def handle_game_over_input(keys_pressed: pygame.key.ScancodeWrapper) -> str:
    """
    Handle input during game over menu.

    Args:
        keys_pressed (pygame.key.ScancodeWrapper): Pressed state of all keys.

    Returns:
        str: Action to take - "restart", "exit", or "none"
    """
    if keys_pressed[pygame.K_r]:
        return "restart"
    elif keys_pressed[pygame.K_RETURN] or keys_pressed[pygame.K_SPACE]:
        return "restart"
    elif keys_pressed[pygame.K_ESCAPE]:
        return "exit"
    return "none"


def _get_menu_button_rects() -> dict[str, pygame.Rect]:
    """
    Compute rectangles for main menu buttons.

    Returns:
        dict[str, pygame.Rect]: Mapping of button name to its rectangle.
    """
    center_x: int = SCREEN_WIDTH // 2
    start_y: int = SCREEN_HEIGHT // 2 - BUTTON_HEIGHT // 2
    total_height: int = BUTTON_HEIGHT * 2 + BUTTON_SPACING
    origin_y: int = SCREEN_HEIGHT // 2 - total_height // 2
    start_button_rect = pygame.Rect(
        center_x - BUTTON_WIDTH // 2,
        origin_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    exit_button_rect = pygame.Rect(
        center_x - BUTTON_WIDTH // 2,
        origin_y + BUTTON_HEIGHT + BUTTON_SPACING,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    return {"start": start_button_rect, "exit": exit_button_rect}


def draw_main_menu(screen: pygame.Surface) -> None:
    """
    Draw the main menu UI with 'Start' and 'Exit' buttons.
    """
    # Title
    if not pygame.font.get_init():
        pygame.font.init()

    try:
        title_font = pygame.font.SysFont("arial", 64)
    except:
        try:
            title_font = pygame.font.Font(None, 64)
        except:
            title_font = None

    if title_font:
        title_text = title_font.render("Flappy Bird", True, BLACK)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 140)
        )
        screen.blit(title_text, title_rect)

    # Buttons
    buttons = _get_menu_button_rects()
    mouse_pos = pygame.mouse.get_pos()

    for name, rect in buttons.items():
        is_hovered = rect.collidepoint(mouse_pos)
        base_color = (70, 130, 180)  # steel blue
        hover_color = (100, 149, 237)  # cornflower blue
        color = hover_color if is_hovered else base_color
        pygame.draw.rect(screen, color, rect, border_radius=8)

        # Button text
        try:
            btn_font = pygame.font.SysFont("arial", 36)
        except:
            try:
                btn_font = pygame.font.Font(None, 36)
            except:
                btn_font = None

        if btn_font:
            label = "Start" if name == "start" else "Exit"
            text_surf = btn_font.render(label, True, WHITE)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)


def _get_confirm_exit_button_rects() -> dict[str, pygame.Rect]:
    center_x: int = SCREEN_WIDTH // 2
    origin_y: int = SCREEN_HEIGHT // 2 + 30
    yes_rect = pygame.Rect(
        center_x - BUTTON_WIDTH - BUTTON_SPACING // 2,
        origin_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    no_rect = pygame.Rect(
        center_x + BUTTON_SPACING // 2, origin_y, BUTTON_WIDTH, BUTTON_HEIGHT
    )
    return {"yes": yes_rect, "no": no_rect}


def draw_confirm_exit(screen: pygame.Surface) -> None:
    # modal overlay
    modal = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    modal.set_alpha(180)
    modal.fill((0, 0, 0))
    screen.blit(modal, (0, 0))

    if not pygame.font.get_init():
        pygame.font.init()

    try:
        title_font = pygame.font.SysFont("arial", 48)
    except:
        try:
            title_font = pygame.font.Font(None, 48)
        except:
            title_font = None

    if title_font:
        msg = "Are you sure you want to exit?"
        title_text = title_font.render(msg, True, WHITE)
        title_rect = title_text.get_rect(
            center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40)
        )
        screen.blit(title_text, title_rect)

    buttons = _get_confirm_exit_button_rects()
    mouse_pos = pygame.mouse.get_pos()
    for name, rect in buttons.items():
        is_hovered = rect.collidepoint(mouse_pos)
        base_color = (178, 34, 34) if name == "yes" else (70, 130, 180)
        hover_color = (220, 20, 60) if name == "yes" else (100, 149, 237)
        color = hover_color if is_hovered else base_color
        pygame.draw.rect(screen, color, rect, border_radius=8)

        try:
            btn_font = pygame.font.SysFont("arial", 36)
        except:
            try:
                btn_font = pygame.font.Font(None, 36)
            except:
                btn_font = None
        if btn_font:
            label = "Yes" if name == "yes" else "No"
            text_surf = btn_font.render(label, True, WHITE)
            text_rect = text_surf.get_rect(center=rect.center)
            screen.blit(text_surf, text_rect)


def handle_main_menu_input(events: list[pygame.event.Event]) -> str:
    """
    Handle input for the main menu.

    Returns:
        str: "start", "exit", or "none"
    """
    buttons = _get_menu_button_rects()
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if buttons["start"].collidepoint(event.pos):
                return "start"
            if buttons["exit"].collidepoint(event.pos):
                return "exit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return "start"
            if event.key == pygame.K_ESCAPE:
                return "exit"
    return "none"


def _get_game_over_button_rects() -> dict[str, pygame.Rect]:
    """
    Compute rectangles for Game Over buttons (Restart, Exit) with same style as main menu.
    """
    center_x: int = SCREEN_WIDTH // 2
    # Place buttons below the score block
    origin_y: int = SCREEN_HEIGHT // 2 + 30
    restart_rect = pygame.Rect(
        center_x - BUTTON_WIDTH // 2,
        origin_y,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    exit_rect = pygame.Rect(
        center_x - BUTTON_WIDTH // 2,
        origin_y + BUTTON_HEIGHT + BUTTON_SPACING,
        BUTTON_WIDTH,
        BUTTON_HEIGHT,
    )
    return {"restart": restart_rect, "exit": exit_rect}


def handle_game_over_input_events(events: list[pygame.event.Event]) -> str:
    """
    Handle mouse/keyboard events for Game Over menu (clickable buttons).
    """
    buttons = _get_game_over_button_rects()
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if buttons["restart"].collidepoint(event.pos):
                return "restart"
            if buttons["exit"].collidepoint(event.pos):
                return "exit"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_r):
                return "restart"
            if event.key == pygame.K_ESCAPE:
                return "exit"
    return "none"


def handle_confirm_exit_input(events: list[pygame.event.Event]) -> str:
    """
    Handle input for the confirm-exit modal.
    Returns: "yes", "no", or "none"
    """
    buttons = _get_confirm_exit_button_rects()
    for event in events:
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if buttons["yes"].collidepoint(event.pos):
                return "yes"
            if buttons["no"].collidepoint(event.pos):
                return "no"
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_y, pygame.K_RETURN):
                return "yes"
            if event.key in (pygame.K_n, pygame.K_ESCAPE):
                return "no"
    return "none"


def reset_game(
    bird: Bird, pipe_manager: PipeManager, score_manager: ScoreManager
) -> None:
    """
    Reset the game to initial state.

    Args:
        bird (Bird): The bird object to reset.
        pipe_manager (PipeManager): The pipe manager to reset.
        score_manager (ScoreManager): The score manager to reset.
    """
    # Reset bird position and velocity
    bird.__x = 70
    bird.__y = 90
    bird.__velocity = 0.0
    bird.rect.x = 70
    bird.rect.y = 90

    # Reset pipe manager using its reset method
    pipe_manager.reset()

    # Reset score
    score_manager.reset_score()


def draw_window(
    screen: pygame.Surface,
    pipe_manager: PipeManager,
    game_state: str = GameState.PLAYING,
    score_manager: ScoreManager = None,
) -> None:
    """
    Render and present the current frame of the game.

    Fills the background, draws pipes first so the bird appears on top, then draws
    the bird and flips the display buffer.

    Args:
        screen (pygame.Surface): The main display surface.
        pipe_manager (PipeManager): Manager responsible for drawing all pipes.
        game_state (str): Current state of the game.
        score_manager (ScoreManager): Score manager for displaying score.
    """
    # Fill the screen with background
    screen.fill(WHITE)

    # Main menu draws its own UI; skip game world drawing
    if game_state == GameState.MENU:
        draw_main_menu(screen)
    elif game_state == GameState.CONFIRM_EXIT_MENU:
        draw_main_menu(screen)
        draw_confirm_exit(screen)
    else:
        # Draw pipes first so the bird appears on top
        pipe_manager.draw(screen)

        # Draw bird to the screen
        bird.draw(screen)

        # Draw score during gameplay
        if game_state == GameState.PLAYING and score_manager:
            draw_score(screen, score_manager)

        # Draw game over menu if game is over
        if game_state == GameState.GAME_OVER and score_manager:
            draw_game_over_menu(screen, score_manager)
        elif game_state == GameState.CONFIRM_EXIT_GAME_OVER and score_manager:
            draw_game_over_menu(screen, score_manager)
            draw_confirm_exit(screen)

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
    pygame.font.init()  # Initialize font module

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

    # Initialize ScoreManager
    score_manager: ScoreManager = ScoreManager()

    # Initialize Bird object
    global bird
    bird = Bird(70, 90, bird_surface)

    # Game state
    game_state = GameState.MENU

    # Track last pipe passed for scoring
    last_pipe_passed = None

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

        if game_state == GameState.MENU:
            # Handle input in main menu
            action = handle_main_menu_input(events)
            if action == "start":
                reset_game(bird, pipe_manager, score_manager)
                game_state = GameState.PLAYING
                last_pipe_passed = None
            elif action == "exit":
                game_state = GameState.CONFIRM_EXIT_MENU

        elif game_state == GameState.CONFIRM_EXIT_MENU:
            confirm = handle_confirm_exit_input(events)
            if confirm == "yes":
                running = False
            elif confirm == "no":
                game_state = GameState.MENU

        elif game_state == GameState.PLAYING:
            # Movement
            bird.movement()

            pipe_manager.update()

            # Handle keys pressed
            handle_keys_pressed_events(keys_pressed)

            # Check for scoring (when bird passes a pipe)
            for pipe_pair in pipe_manager._PipeManager__pipes:
                if (
                    pipe_pair.top_pipe.rect.right < bird.rect.left
                    and pipe_pair != last_pipe_passed
                ):
                    score_manager.increment_score()
                    last_pipe_passed = pipe_pair

            # Check for collisions
            if check_collisions(bird, pipe_manager):
                score_manager.update_high_score()
                game_state = GameState.GAME_OVER

        elif game_state == GameState.GAME_OVER:
            # Handle input in game over menu (mouse + keyboard)
            action = handle_game_over_input_events(events)
            if action == "none":
                # fallback to continuous key state for convenience
                action = handle_game_over_input(keys_pressed)
            if action == "restart":
                reset_game(bird, pipe_manager, score_manager)
                game_state = GameState.PLAYING
                last_pipe_passed = None
            elif action == "exit":
                game_state = GameState.CONFIRM_EXIT_GAME_OVER

        elif game_state == GameState.CONFIRM_EXIT_GAME_OVER:
            confirm = handle_confirm_exit_input(events)
            if confirm == "yes":
                running = False
            elif confirm == "no":
                game_state = GameState.GAME_OVER

        # Draw window
        draw_window(screen, pipe_manager, game_state, score_manager)

    # Look at the name
    pygame.display.quit()


if __name__ == "__main__":
    main()
