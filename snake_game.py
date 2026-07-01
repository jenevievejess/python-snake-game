import tkinter as tk
import random
import time


class SnakeGame(tk.Tk):
    """
    Main class: manages the window, game logic, and all the drawing 
    """

    def __init__(self):
        super().__init__()

        self.title("Snake Game")
        self.resizable(False, False)

        # Game board settings
        self.cell_size = 25
        self.cols = 28
        self.rows = 28

        self.width = self.cell_size * self.cols
        self.height = self.cell_size * self.rows

        bar_h = 55
        self.geometry(f"{self.width}x{self.height + bar_h}")

        # Colors
        self.bg_color   = "#f2f0ee"
        self.grid_color = "#e4e1dc"

        self.bar_bg   = "#ede8e0"
        self.bar_fg   = "#4a4543"
        self.btn_bg   = "#d6cfc5"
        self.btn_hover = "#c5bdb3"

        self.snake_head_color = "#6baed6"
        self.snake_body_color = "#9ecae1"
        self.snake_outline    = "#2171b5"
        self.eye_color        = "#1a1a2e"

        self.win_color  = "#52b788"
        self.lose_color = "#e07a5f"
        self.overlay_bg = "#faf7f2"

        self.FONT = "Georgia"

        # Game state
        self.snake_direction = 'Right'
        cs = self.cell_size
        self.snake = [(cs * 5, cs * 5), (cs * 4, cs * 5), (cs * 3, cs * 5)]

        self.food = None
        self.food_type = None        # 1 = blueberry (grow 1), 2 = strawberry (grow 2)
        
        self.game_running = False
        self.paused = False

        self.start_time = None
        self.pause_start = None
        self.paused_elapsed = 0

        self.max_length = 20         # win condition: snake reach this length

        self._build_ui()
        self.start_game()

    # --- UI ---
    def _build_ui(self):
        # Top bar
        self.bar = tk.Frame(self, bg=self.bar_bg, height=55)
        self.bar.pack(fill="x")
        self.bar.pack_propagate(False)

        self.length_label = tk.Label(
            self.bar, text="Length: 3",
            bg=self.bar_bg, fg=self.bar_fg,
            font=(self.FONT, 13)
        )
        self.length_label.pack(side="left", padx=18, pady=14)

        center_frame = tk.Frame(self.bar, bg=self.bar_bg)
        center_frame.pack(side="left", expand=True)
        self.time_label = tk.Label(
            center_frame, text="Time: 0s",
            bg=self.bar_bg, fg=self.bar_fg,
            font=(self.FONT, 13)
        )
        self.time_label.pack()

        # Restart
        self.restart_btn = tk.Button(
            self.bar, text="Restart",
            bg=self.btn_bg, fg=self.bar_fg,
            font=(self.FONT, 11), relief="flat", bd=0,
            padx=10, pady=4,
            command=self.restart_game
        )
        self.restart_btn.pack(side="right", padx=8, pady=10)
        self.restart_btn.bind("<Enter>", lambda e: self.restart_btn.config(bg=self.btn_hover))
        self.restart_btn.bind("<Leave>", lambda e: self.restart_btn.config(bg=self.btn_bg))

        # Pause
        self.pause_btn = tk.Button(
            self.bar, text="Pause",
            bg=self.btn_bg, fg=self.bar_fg,
            font=(self.FONT, 11), relief="flat", bd=0,
            padx=10, pady=4,
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="right", padx=4, pady=10)
        self.pause_btn.bind("<Enter>", lambda e: self.pause_btn.config(bg=self.btn_hover))
        self.pause_btn.bind("<Leave>", lambda e: self.pause_btn.config(bg=self.btn_bg))

        # Game canvas
        self.canvas = tk.Canvas(
            self,
            bg=self.bg_color,
            width=self.width,
            height=self.height,
            highlightthickness=0
        )
        self.canvas.pack()

    # --- Game controls ---
    # Reset all variables and start a new game
    def start_game(self):
        cs = self.cell_size
        self.snake = [(cs * 5, cs * 5), (cs * 4, cs * 5), (cs * 3, cs * 5)]
        self.snake_direction = 'Right'

        self.game_running = True
        self.paused = False
        self.paused_elapsed = 0
        self.pause_start = None

        self.start_time = time.time()

        self.pause_btn.config(text="Pause")

        self.spawn_food()
        self.bind("<KeyPress>", self.on_key_press)

        # Avoid stacking loops when restarting (which causes snake to get faster each time)
        if hasattr(self, '_loop_id') and self._loop_id:
            self.after_cancel(self._loop_id)
            self._loop_id = None
        
        self.run_game()

    # Clear canvas and start a new game
    def restart_game(self):
        self.canvas.delete('all')
        self.start_game()

    # Pause and resume the game
    def toggle_pause(self):
        if not self.game_running:
            return

        if self.paused:
            self.paused_elapsed += time.time() - self.pause_start
            self.pause_start = None
            self.paused = False
            self.pause_btn.config(text="Pause")
            self.run_game()
        else:
            self.pause_start = time.time()
            self.paused = True
            self.pause_btn.config(text="Resume")
            self._draw_pause_overlay()

    # Pause message
    def _draw_pause_overlay(self):
        mx, my = self.width // 2, self.height // 2
        self.canvas.create_rectangle(mx - 150, my - 60, mx + 150, my + 60,
                                      fill=self.overlay_bg, outline="#c5bdb3", width=2)
        self.canvas.create_text(mx, my - 15, text="Paused",
                                  fill="#4a4543", font=(self.FONT, 22, "bold"))
        self.canvas.create_text(mx, my + 22, text="Press P or click Resume",
                                  fill="#888", font=(self.FONT, 11))

    # Main game loop
    def run_game(self):
        if self.game_running and not self.paused:
            self.move_snake()
            self._loop_id = self.after(140, self.run_game)

    # --- Keyboard Controls ---
    def on_key_press(self, event):
        opposite = {'Left': 'Right', 'Right': 'Left', 'Up': 'Down', 'Down': 'Up'}

        if event.keysym in ['Left', 'Right', 'Up', 'Down']:
            if event.keysym != opposite.get(self.snake_direction):
                self.snake_direction = event.keysym

        elif event.keysym.lower() == 'p':
            self.toggle_pause()

        elif event.keysym.lower() == 'r':
            self.restart_game()

    # --- Food ---
    def spawn_food(self):
        cs = self.cell_size
        
        free = [
            (x, y)
            for x in range(cs, self.width - cs, cs)
            for y in range(cs, self.height - cs, cs)
            if (x, y) not in self.snake
        ]
        if free:
            self.food = random.choice(free)
            self.food_type = random.choice([1, 2])

    # Blueberry 
    def _draw_blueberry(self, x, y):
        cs = self.cell_size
        cx = x + cs // 2
        cy = y + cs // 2
        r = 9

        self.canvas.create_oval(cx - r, cy - r + 1, cx + r, cy + r + 1,
                                 fill="#7b6fa0", outline="#5c5380", width=1)
        self.canvas.create_oval(cx - 3, cy - 5, cx + 1, cy - 2,
                                 fill="#b0a8cc", outline="")
        for dx in [-2, -1, 0, 1, 2]:
            self.canvas.create_line(cx + dx, cy - r, cx + dx, cy - r - 3,
                                     fill="#4a3f6b", width=1)

    # Strawberry 
    def _draw_strawberry(self, x, y):
        cs = self.cell_size
        cx = x + cs // 2
        cy = y + cs // 2

        self.canvas.create_polygon(
            cx,      cy + 11,
            cx - 10, cy - 2,
            cx - 8,  cy - 7,
            cx,      cy - 5,
            cx + 8,  cy - 7,
            cx + 10, cy - 2,
            fill="#e85d75", outline="#c0384f", width=1, smooth=True
        )
        for sx, sy in [(-3, -2), (3, -2), (0, 3), (-4, 4), (4, 4), (0, 8)]:
            self.canvas.create_oval(cx + sx - 1, cy + sy - 1,
                                     cx + sx + 1, cy + sy + 1,
                                     fill="#ffd166", outline="")
        self.canvas.create_polygon(
            cx - 6, cy - 5, cx - 3, cy - 11, cx, cy - 6,
            fill="#52b788", outline="#2d6a4f", width=1, smooth=True
        )
        self.canvas.create_polygon(
            cx + 6, cy - 5, cx + 3, cy - 11, cx, cy - 6,
            fill="#52b788", outline="#2d6a4f", width=1, smooth=True
        )
        self.canvas.create_polygon(
            cx - 1, cy - 6, cx + 1, cy - 6, cx, cy - 12,
            fill="#74c69d", outline="#2d6a4f", width=1
        )

    # --- Drawing ---
    # Clear and redraw each frame
    def draw(self):
        self.canvas.delete('all')

        # Grid
        for x in range(0, self.width + 1, self.cell_size):
            self.canvas.create_line(x, 0, x, self.height, fill=self.grid_color, width=1)
        for y in range(0, self.height + 1, self.cell_size):
            self.canvas.create_line(0, y, self.width, y, fill=self.grid_color, width=1)

        # Snake
        cs = self.cell_size
        for i, (x, y) in enumerate(self.snake):
            color = self.snake_head_color if i == 0 else self.snake_body_color
            self.canvas.create_rectangle(
                x + 2, y + 2, x + cs - 2, y + cs - 2,
                fill=color, outline=self.snake_outline, width=1
            )
        self._draw_eyes()

        # Food
        if self.food:
            fx, fy = self.food
            if self.food_type == 1:
                self._draw_blueberry(fx, fy)
            else:
                self._draw_strawberry(fx, fy)

        # Top bar stats
        elapsed = int(time.time() - self.start_time - self.paused_elapsed) if self.start_time else 0
        self.length_label.config(text=f"Length: {len(self.snake)}")
        self.time_label.config(text=f"Time: {elapsed}s")

    # Draw snake eyes
    def _draw_eyes(self):
        if not self.snake:
            return

        hx, hy = self.snake[0]
        cs = self.cell_size
        mid = cs // 2  

        eye_offsets = {
            'Right': [(cs - 6, mid - 4), (cs - 6, mid + 4)],
            'Left':  [(6,      mid - 4), (6,      mid + 4)],
            'Up':    [(mid - 4, 6),      (mid + 4, 6)],
            'Down':  [(mid - 4, cs - 6), (mid + 4, cs - 6)],
        }
        offsets = eye_offsets.get(self.snake_direction, [(cs - 6, mid - 4), (cs - 6, mid + 4)])

        r = 2
        for (ex, ey) in offsets:
            self.canvas.create_oval(
                hx + ex - r, hy + ey - r,
                hx + ex + r, hy + ey + r,
                fill=self.eye_color, outline=""
            )

    # --- Game logic --- 
    # Move snake and check collision
    def move_snake(self):
        hx, hy = self.snake[0]
        cs = self.cell_size

        if self.snake_direction == 'Left':
            hx -= cs
        elif self.snake_direction == 'Right':
            hx += cs
        elif self.snake_direction == 'Up':
            hy -= cs
        elif self.snake_direction == 'Down':
            hy += cs

        new_head = (hx, hy)

        # Wall collision
        if hx < 0 or hx >= self.width or hy < 0 or hy >= self.height:
            self.end_game("You hit the wall", win=False)
            return

        # Self collision
        if new_head in self.snake:
            self.end_game("You ran into yourself", win=False)
            return

        self.snake = [new_head] + self.snake

        # Food eaten
        if new_head == self.food:
            # Strawberry: +2
            if self.food_type == 2:
                self.snake.append(self.snake[-1])

            self.food = None
            self.draw()

            if len(self.snake) >= self.max_length:
                self.after(200, lambda: self.end_game("You reached max length!", win=True))
                return

            self.spawn_food()
        else:
            self.snake.pop()

        self.draw()

    # --- Ending screen ---
    def end_game(self, message, win=False):
        self.game_running = False
        elapsed = int(time.time() - self.start_time - self.paused_elapsed)

        accent = self.win_color if win else self.lose_color
        title_text = "You Win!" if win else "Game Over"

        mx, my = self.width // 2, self.height // 2

        # End stats
        self.canvas.create_rectangle(mx - 210, my - 140, mx + 210, my + 145,
                                      fill=self.overlay_bg, outline=accent, width=3)
        self.canvas.create_text(mx, my - 95, text=title_text,
                                  fill=accent, font=(self.FONT, 28, "bold"))
        self.canvas.create_text(mx, my - 52, text=message,
                                  fill="#333", font=(self.FONT, 13, "italic"))
        self.canvas.create_line(mx - 160, my - 28, mx + 160, my - 28,
                                  fill=self.grid_color, width=1)
        self.canvas.create_text(mx, my + 2,
                                  text=f"Final length:   {len(self.snake)} units",
                                  fill="#333", font=(self.FONT, 13))
        self.canvas.create_text(mx, my + 32,
                                  text=f"Time played:   {elapsed} seconds",
                                  fill="#333", font=(self.FONT, 13))

        # Play again
        btn_rect = self.canvas.create_rectangle(mx - 90, my + 60, mx + 90, my + 100,
                                                  fill=accent, outline="")
        btn_text = self.canvas.create_text(mx, my + 80, text="Play Again",
                                             fill="white", font=(self.FONT, 13, "bold"))
        for item in [btn_rect, btn_text]:
            self.canvas.tag_bind(item, "<Button-1>", lambda e: self.restart_game())
        self.canvas.create_text(mx, my + 122, text="or press R to restart",
                                  fill="#888", font=(self.FONT, 10, "italic"))


# --- Entry point ---
if __name__ == "__main__":
    game = SnakeGame()
    game.mainloop()