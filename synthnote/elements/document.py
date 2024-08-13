"""
Donut
Copyright (c) 2022-present NAVER Corp.
MIT License
"""
import numpy as np
from synthtiger import layers

from elements.content import Content


class Document:
    def __init__(self, config):
        self.fullscreen = config.get("fullscreen", 0.5)
        self.landscape = config.get("landscape", 0.5)
        self.short_size = config.get("short_size", [480, 1024])
        self.aspect_ratio = config.get("aspect_ratio", [1, 2])
        self.content = Content(config.get("content", {}))
  
    def generate(self, size):
        width, height = size
        fullscreen = np.random.rand() < self.fullscreen

        if not fullscreen:
            landscape = np.random.rand() < self.landscape
            max_size = width if landscape else height
            short_size = np.random.randint(
                min(width, height, self.short_size[0]),
                min(width, height, self.short_size[1]) + 1,
            )
            aspect_ratio = np.random.uniform(
                min(max_size / short_size, self.aspect_ratio[0]),
                min(max_size / short_size, self.aspect_ratio[1]),
            )
            long_size = int(short_size * aspect_ratio)
            size = (long_size, short_size) if landscape else (short_size, long_size)

        text_layers, texts, bbox = self.content.generate(size)
        paper_layer = layers.RectLayer(size, (255, 255, 255, 255))

        return paper_layer, text_layers, texts, bbox
