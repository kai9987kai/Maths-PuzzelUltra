import pygame
import sys
import os
import random
import datetime
from math_gen import generate_problem
from ui import Button, TextInput
from puzzle import Puzzle
from effects import EffectManager
from sound_manager import sounds

# Constants
WIDTH, HEIGHT = 900, 700
WHITE = (255, 255, 255)
BG_COLOR = (30, 30, 40) # Darker, more premium feel
FPS = 60

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Math Puzzle Pro Ultra")
        self.clock = pygame.time.Clock()
        self.font_title = pygame.font.Font(None, 100)
        self.font_large = pygame.font.Font(None, 74)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
        self.state = "MENU" # MENU, PLAYING, LEVEL_UP, GAME_OVER
        self.mode = "classic" # classic, blitz, zen
        self.level = 1
        self.score = 0
        self.difficulty = "easy"
        
        self.combo = 0
        self.combo_timer = 0
        self.multiplier = 1.0
        self.wrong_count = 0
        self.hint_text = ""
        self.power_gauge = 0
        self.power_active = False
        self.power_timer = 0
        self.sound_on = True
        sounds.setup_default_sounds()
        
        self.puzzle = Puzzle(500, 350, rows=2, cols=4) # More pieces for ultra
        self.effects = EffectManager()
        
        self._setup_ui()
        self._new_problem()
        
        self.time_limit = 60
        self.time_remaining = self.time_limit
        self.last_tick = pygame.time.get_ticks()

    def _setup_ui(self):
        # Menu Buttons
        btn_w, btn_h = 250, 60
        self.classic_btn = Button(WIDTH//2 - 125, 230, btn_w, btn_h, "CLASSIC MODE", color=(0, 120, 215))
        self.blitz_btn = Button(WIDTH//2 - 125, 305, btn_w, btn_h, "BLITZ MODE", color=(215, 60, 0))
        self.zen_btn = Button(WIDTH//2 - 125, 380, btn_w, btn_h, "ZEN MODE", color=(0, 150, 80))
        self.daily_btn = Button(WIDTH//2 - 125, 455, btn_w, btn_h, "DAILY CHALLENGE", color=(180, 0, 180))
        self.sound_btn = Button(20, HEIGHT - 60, 150, 40, "SOUND: ON", font_size=24)
        
        # Game UI
        self.input_field = TextInput(WIDTH//2 - 100, 550, 200, 50)
        self.submit_btn = Button(WIDTH//2 + 110, 550, 100, 50, "SUBMIT", color=(40, 40, 60))

    def _new_problem(self):
        if self.mode == "zen":
            self.difficulty = random.choice(["easy", "medium"])
        else:
            if self.level == 1: self.difficulty = "easy"
            elif self.level == 2: self.difficulty = "medium"
            else: self.difficulty = "hard"
            
        self.current_problem, self.correct_answer = generate_problem(self.difficulty)
        self.input_field.text = ""
        self.wrong_count = 0
        self.hint_text = ""

    def handle_events(self):
        pos = pygame.mouse.get_pos()
        for btn in [self.classic_btn, self.blitz_btn, self.zen_btn, self.daily_btn, self.sound_btn, self.submit_btn]:
            btn.check_hover(pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if self.state == "MENU":
                if self.sound_btn.is_clicked(pos, event):
                    self.sound_on = not self.sound_on
                    self.sound_btn.text = f"SOUND: {'ON' if self.sound_on else 'OFF'}"
                    if self.sound_on: sounds.play("click")
                
                elif self.classic_btn.is_clicked(pos, event):
                    self._start_game("classic")
                elif self.blitz_btn.is_clicked(pos, event):
                    self._start_game("blitz")
                elif self.zen_btn.is_clicked(pos, event):
                    self._start_game("zen")
                elif self.daily_btn.is_clicked(pos, event):
                    self._start_game("daily")
            
            elif self.state == "PLAYING":
                if event.type == pygame.KEYDOWN and event.key == pygame.K_LSHIFT:
                    self._activate_powerup()
                res = self.input_field.handle_event(event)
                if res == "submit" or self.submit_btn.is_clicked(pos, event):
                    self._check_answer()
            
            elif self.state in ["LEVEL_UP", "GAME_OVER"]:
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    if self.state == "GAME_OVER":
                        self.state = "MENU"
                    else:
                        self.state = "PLAYING"
                        self.last_tick = pygame.time.get_ticks()
                        if self.mode != "blitz": self.time_remaining = self.time_limit
                        self.puzzle.reset()
                        self._new_problem()

    def _start_game(self, mode):
        if self.sound_on: sounds.play("click")
        self.mode = mode
        self.state = "PLAYING"
        self.level = 1
        self.score = 0
        self.combo = 0
        self.multiplier = 1.0
        self.power_gauge = 0
        self.power_active = False
        self.puzzle.reset()
        self.last_tick = pygame.time.get_ticks()
        
        if mode == "daily":
            seed = int(datetime.date.today().strftime("%Y%m%d"))
            random.seed(seed)
            self.time_limit = 45
            self.time_remaining = 45
        elif mode == "blitz":
            random.seed(pygame.time.get_ticks()) # Reset to normal random
            self.time_limit = 30
            self.time_remaining = 30
        elif mode == "classic":
            random.seed(pygame.time.get_ticks())
            self.time_limit = 60
            self.time_remaining = 60
        else: # Zen
            random.seed(pygame.time.get_ticks())
            self.time_limit = 9999
            self.time_remaining = 9999
            
        self._new_problem()

    def _check_answer(self):
        try:
            user_ans = int(self.input_field.text)
            if user_ans == self.correct_answer:
                if self.sound_on: sounds.play("correct")
                # Success Feedback
                self.effects.create_burst(WIDTH//2, 500)
                
                # Combo & Scoring
                base_points = 10 * self.level
                self.combo += 1
                self.combo_timer = 200 # frames
                self.multiplier = min(3.0, 1.0 + (self.combo // 3) * 0.5)
                
                added_score = int(base_points * self.multiplier)
                self.score += added_score
                
                # Gauge fill
                self.power_gauge = min(100, self.power_gauge + 10)
                
                if self.mode == "blitz":
                    self.time_remaining += 2 # Bonus time in blitz
                
                self.puzzle.add_piece()
                
                if self.puzzle.is_complete() and self.mode != "zen":
                    self.level += 1
                    if self.level > 5: # More levels in Ultra
                        self.state = "GAME_OVER"
                    else:
                        self.state = "LEVEL_UP"
                else:
                    self._new_problem()
            else:
                if self.sound_on: sounds.play("wrong")
                # Wrong Answer Feedback
                self.effects.trigger_shake(10, 0.3)
                self.combo = 0
                self.multiplier = 1.0
                self.input_field.text = ""
                self.wrong_count += 1
                if self.wrong_count >= 2:
                    self.hint_text = f"HINT: Look for the {self.difficulty} logic!"
                    if "+" in self.current_problem: self.hint_text = "HINT: Combination of values!"
                    elif "-" in self.current_problem: self.hint_text = "HINT: Find the difference!"
                    elif "*" in self.current_problem: self.hint_text = "HINT: Repeated addition!"
                # Shake penalty
                self.power_gauge = max(0, self.power_gauge - 15)
        except ValueError:
            self.input_field.text = ""

    def _activate_powerup(self):
        if self.power_gauge >= 100 and not self.power_active:
            if self.sound_on: sounds.play("powerup")
            self.power_active = True
            self.power_gauge = 0
            self.power_timer = 300 # 5 seconds at 60fps
            self.effects.create_burst(WIDTH//2, HEIGHT//2, (0, 255, 255), 50)

    def update(self):
        # Update effects
        dt = self.clock.get_time() / 1000.0
        self.effects.update(dt)
        
        # Powerup effect
        if self.power_active:
            self.power_timer -= 1
            if self.power_timer <= 0:
                self.power_active = False
        
        # Update timer
        if self.state == "PLAYING":
            now = pygame.time.get_ticks()
            if now - self.last_tick >= 1000:
                if self.mode != "zen":
                    # Slow time if powerup active
                    if not self.power_active or now % 2 == 0:
                        self.time_remaining -= 1
                self.last_tick = now
                if self.time_remaining <= 0:
                    self.state = "GAME_OVER"
            
            # Update combo timer
            if self.combo_timer > 0:
                self.combo_timer -= 1
            else:
                self.combo = 0
                self.multiplier = 1.0

    def draw(self):
        # Apply shake offset
        shake_x, shake_y = self.effects.get_shake_offset()
        temp_surface = pygame.Surface((WIDTH, HEIGHT))
        temp_surface.fill(BG_COLOR)
        
        if self.state == "MENU":
            title = self.font_title.render("PUZZLE ULTRA", True, (255, 255, 255))
            temp_surface.blit(title, title.get_rect(center=(WIDTH//2, 100)))
            self.classic_btn.draw(temp_surface)
            self.blitz_btn.draw(temp_surface)
            self.zen_btn.draw(temp_surface)
            self.daily_btn.draw(temp_surface)
            self.sound_btn.draw(temp_surface)
        
        elif self.state == "PLAYING":
            # HUD
            if self.power_active:
                pygame.draw.rect(temp_surface, (0, 50, 50), (0, 0, WIDTH, HEIGHT)) # Blue tint
            
            mode_text = self.font_small.render(f"MODE: {self.mode.upper()}", True, (200, 200, 200))
            temp_surface.blit(mode_text, (20, 20))
            
            score_text = self.font_medium.render(f"SCORE: {self.score}", True, (255, 215, 0))
            temp_surface.blit(score_text, (20, 50))
            
            # Powerup Gauge
            pygame.draw.rect(temp_surface, (50, 50, 50), (20, 100, 150, 15))
            bar_w = int(150 * (self.power_gauge / 100))
            bar_color = (0, 255, 255) if self.power_gauge >= 100 else (0, 180, 180)
            pygame.draw.rect(temp_surface, bar_color, (20, 100, bar_w, 15))
            power_msg = "PRESS SHIFT!" if self.power_gauge >= 100 else "POWER GAUGUE"
            p_text = self.font_small.render(power_msg, True, bar_color)
            temp_surface.blit(p_text, (20, 120))
            
            if self.mode != "zen":
                timer_color = (255, 255, 255) if self.time_remaining > 5 else (255, 50, 50)
                timer_text = self.font_large.render(f"{self.time_remaining}s", True, timer_color)
                temp_surface.blit(timer_text, (WIDTH - 150, 20))
            
            # Combo display
            if self.combo > 1:
                combo_text = self.font_medium.render(f"COMBO x{self.multiplier}", True, (0, 255, 100))
                temp_surface.blit(combo_text, combo_text.get_rect(center=(WIDTH//2, 200)))

            # Problem
            prob_text = self.font_large.render(self.current_problem, True, (255, 255, 255))
            temp_surface.blit(prob_text, prob_text.get_rect(center=(WIDTH//2, 100)))
            
            # Hint
            if self.hint_text:
                hint_surf = self.font_small.render(self.hint_text, True, (255, 200, 0))
                temp_surface.blit(hint_surf, hint_surf.get_rect(center=(WIDTH//2, 140)))
            
            # Puzzle
            self.puzzle.draw(temp_surface, WIDTH//2 - 250, 160)
            
            # Input
            self.input_field.draw(temp_surface)
            self.submit_btn.draw(temp_surface)

        elif self.state == "LEVEL_UP":
            msg = self.font_large.render(f"LEVEL {self.level-1} CLEAR!", True, (0, 255, 120))
            temp_surface.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2)))
            sub = self.font_small.render("Press any key for next challenge", True, (150, 150, 150))
            temp_surface.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 60)))

        elif self.state == "GAME_OVER":
            title = "VICTORY!" if self.level > 5 else "GAME OVER"
            color = (0, 200, 255) if self.level > 5 else (255, 50, 50)
            msg = self.font_title.render(title, True, color)
            temp_surface.blit(msg, msg.get_rect(center=(WIDTH//2, HEIGHT//2 - 40)))
            score_text = self.font_medium.render(f"FINAL SCORE: {self.score}", True, (255, 215, 0))
            temp_surface.blit(score_text, score_text.get_rect(center=(WIDTH//2, HEIGHT//2 + 40)))
            sub = self.font_small.render("Press any key to return to menu", True, (150, 150, 150))
            temp_surface.blit(sub, sub.get_rect(center=(WIDTH//2, HEIGHT//2 + 100)))

        self.effects.draw(temp_surface)
        self.screen.blit(temp_surface, (shake_x, shake_y))
        pygame.display.flip()

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
