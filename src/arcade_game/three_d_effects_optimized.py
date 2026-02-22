
import math
import arcade

class ThreeDEffectsOptimized:
    def __init__(self):
        self._time = 0.0
        self._float_amplitude = 2.5
        self._float_speed = 1.5
        self._shadow_offset = (0, -10)
        self._shadow_scale = 0.85
        self._shadow_alpha = 100
        self._highlight_alpha = 60
        self._edge_highlight_alpha = 60
        self._ellipse_batch = []
        self._circle_filled_batch = []
    
    def update(self, dt):
        self._time += dt
    
    def get_float_offset(self, entity_id, base_y):
        phase = (entity_id * 0.1234) % (2 * math.pi)
        return math.sin(self._time * self._float_speed + phase) * self._float_amplitude
    
    def get_perspective_scale(self, y, screen_height=600):
        normalized_y = y / screen_height
        return 0.95 + normalized_y * 0.1
    
    def _clear_batches(self):
        self._ellipse_batch.clear()
        self._circle_filled_batch.clear()
    
    def _execute_batches(self):
        for x, y, w, h, color in self._ellipse_batch:
            arcade.draw_ellipse_filled(x, y, w, h, color)
        for x, y, r, color in self._circle_filled_batch:
            arcade.draw_circle_filled(x, y, r, color)
    
    def draw_shadow(self, x, y, width, height, alpha=None):
        shadow_alpha = alpha if alpha is not None else self._shadow_alpha
        shadow_x = x + self._shadow_offset[0]
        shadow_y = y + self._shadow_offset[1]
        shadow_width = width * self._shadow_scale
        shadow_height = height * 0.4
        r, g, b = 0, 0, 0
        for i in range(2):
            scale = 1.0 + i * 0.2
            a_val = max(0, shadow_alpha - i * 40)
            if a_val > 0:
                self._ellipse_batch.append((shadow_x, shadow_y, shadow_width * scale, shadow_height * scale, (r, g, b, a_val)))
    
    def draw_highlight(self, x, y, width, height, alpha=None):
        highlight_alpha = alpha if alpha is not None else self._highlight_alpha
        highlight_y = y + height * 0.25
        highlight_width = width * 0.6
        highlight_height = height * 0.3
        self._ellipse_batch.append((x, highlight_y, highlight_width, highlight_height, (255, 255, 255, highlight_alpha)))
    
    def draw_3d_effects(self, entity_id, x, y, width, height, screen_height=600, enable_shadow=True, enable_highlight=True, enable_edge=False, enable_float=True):
        float_offset = self.get_float_offset(entity_id, y) if enable_float else 0.0
        scale = self.get_perspective_scale(y, screen_height)
        adjusted_y = y + float_offset
        adjusted_width = width * scale
        adjusted_height = height * scale
        if enable_shadow:
            self.draw_shadow(x, adjusted_y, adjusted_width, adjusted_height)
        return (x, adjusted_y, scale)
    
    def apply_post_effects(self, entity_id, x, y, width, height, enable_highlight=True, enable_edge=False):
        if enable_highlight:
            self.draw_highlight(x, y, width, height)
    
    def begin_batch(self):
        self._clear_batches()
    
    def end_batch(self):
        self._execute_batches()

