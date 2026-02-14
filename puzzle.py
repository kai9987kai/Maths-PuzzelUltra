import pygame
import os

class Puzzle:
    def __init__(self, width, height, rows=1, cols=5):
        self.width = width
        self.height = height
        self.rows = rows
        self.cols = cols
        self.total_pieces = rows * cols
        self.revealed_pieces = 0
        self.image = self._load_placeholder()
        self.pieces = self._slice_image()

    def _load_placeholder(self):
        # Create a colorful placeholder if no image found
        surf = pygame.Surface((self.width, self.height))
        surf.fill((200, 200, 200))
        # Draw some pattern
        for i in range(0, self.width, 50):
            pygame.draw.line(surf, (150, 150, 150), (i, 0), (i, self.height), 1)
        for j in range(0, self.height, 50):
            pygame.draw.line(surf, (150, 150, 150), (0, j), (self.width, j), 1)
        return surf

    def load_image(self, path):
        if os.path.exists(path):
            img = pygame.image.load(path).convert()
            self.image = pygame.transform.scale(img, (self.width, self.height))
            self.pieces = self._slice_image()

    def _slice_image(self):
        pieces = []
        piece_w = self.width // self.cols
        piece_h = self.height // self.rows
        for r in range(self.rows):
            for c in range(self.cols):
                rect = pygame.Rect(c * piece_w, r * piece_h, piece_w, piece_h)
                piece_surf = self.image.subsurface(rect).copy()
                pieces.append({'surf': piece_surf, 'rect': rect})
        return pieces

    def add_piece(self):
        if self.revealed_pieces < self.total_pieces:
            self.revealed_pieces += 1
            return True
        return False

    def is_complete(self):
        return self.revealed_pieces >= self.total_pieces

    def reset(self):
        self.revealed_pieces = 0

    def draw(self, screen, x, y):
        # Draw background/frame
        pygame.draw.rect(screen, (50, 50, 50), (x-2, y-2, self.width+4, self.height+4), 2)
        
        # Draw revealed pieces
        for i in range(self.revealed_pieces):
            piece = self.pieces[i]
            screen.blit(piece['surf'], (x + piece['rect'].x, y + piece['rect'].y))
            
        # Draw grid for hidden pieces
        piece_w = self.width // self.cols
        piece_h = self.height // self.rows
        for i in range(self.revealed_pieces, self.total_pieces):
            r = i // self.cols
            c = i % self.cols
            rect = pygame.Rect(x + c * piece_w, y + r * piece_h, piece_w, piece_h)
            pygame.draw.rect(screen, (100, 100, 100), rect)
            pygame.draw.rect(screen, (120, 120, 120), rect, 1)
            # Question mark in center
            font = pygame.font.Font(None, 48)
            q_text = font.render("?", True, (80, 80, 80))
            screen.blit(q_text, q_text.get_rect(center=rect.center))
