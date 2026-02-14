import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=1)
        self.sounds = {}

    def generate_beep(self, frequency, duration, name):
        """Generates a simple sine wave beep."""
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        # Create samples
        t = np.linspace(0, duration, n_samples, False)
        # Sine wave
        wave = np.sin(2 * np.pi * frequency * t) * 32767
        # Envelope to prevent clicks
        fade = int(sample_rate * 0.01)
        envelope = np.ones(n_samples)
        envelope[:fade] = np.linspace(0, 1, fade)
        envelope[-fade:] = np.linspace(1, 0, fade)
        
        sound_array = (wave * envelope).astype(np.int16)
        sound = pygame.sndarray.make_sound(sound_array)
        self.sounds[name] = sound

    def setup_default_sounds(self):
        try:
            self.generate_beep(440, 0.1, "correct")
            self.generate_beep(220, 0.2, "wrong")
            self.generate_beep(660, 0.05, "click")
            self.generate_beep(880, 0.3, "powerup")
        except Exception as e:
            print(f"Sound generation failed: {e}. Audio will be disabled.")

    def play(self, name):
        if name in self.sounds:
            self.sounds[name].play()

# Singleton instance
sounds = SoundManager()
