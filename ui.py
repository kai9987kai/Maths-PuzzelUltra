import pygame

class Button:
    def __init__(self, x, y, width, height, text, color=(100, 100, 100), hover_color=(150, 150, 150), font_size=32):
        self.base_rect = pygame.Rect(x, y, width, height)
        self.rect = self.base_rect.copy()
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.font = pygame.font.Font(None, font_size)
        self.is_hovered = False
        self.scale = 1.0
        self.target_scale = 1.0

    def draw(self, screen):
        # Smooth scale animation
        self.scale += (self.target_scale - self.scale) * 0.2
        new_w = int(self.base_rect.width * self.scale)
        new_h = int(self.base_rect.height * self.scale)
        self.rect = pygame.Rect(0, 0, new_w, new_h)
        self.rect.center = self.base_rect.center
        
        color = self.hover_color if self.is_hovered else self.color
        pygame.draw.rect(screen, color, self.rect, border_radius=8)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=8)
        
        text_surf = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)

    def check_hover(self, pos):
        self.is_hovered = self.base_rect.collidepoint(pos)
        self.target_scale = 1.1 if self.is_hovered else 1.0
        return self.is_hovered

    def is_clicked(self, pos, event):
        return event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(pos)

class TextInput:
    def __init__(self, x, y, width, height, font_size=40):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = ""
        self.font = pygame.font.Font(None, font_size)
        self.active = True
        self.cursor_timer = 0

    def draw(self, screen):
        color = (40, 40, 50)
        pygame.draw.rect(screen, color, self.rect, border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=5)
        
        display_text = self.text
        if len(display_text) == 0:
            text_surf = self.font.render("Type here...", True, (100, 100, 110))
        else:
            text_surf = self.font.render(display_text, True, (255, 255, 255))
            
        text_rect = text_surf.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        screen.blit(text_surf, text_rect)
        
        # Blinking cursor
        self.cursor_timer = (self.cursor_timer + 1) % 60
        if self.cursor_timer < 30:
            cursor_x = text_rect.right + 2
            pygame.draw.line(screen, (255, 255, 255), (cursor_x, self.rect.y + 10), (cursor_x, self.rect.bottom - 10), 2)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "submit"
            elif event.unicode.isdigit() or (event.unicode == '-' and len(self.text) == 0):
                self.text += event.unicode
        return None
