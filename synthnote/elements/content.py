from collections import OrderedDict

import numpy as np
from synthtiger import components, layers

from elements.textbox import TextBox
from layouts import GridStack

class TextReader:
    def __init__(self, path, cache_size=2 ** 28, block_size=2 ** 20):
        self.fp = open(path, "r", encoding="utf-8")
        self.length = 0
        self.offsets = [0]
        self.cache = OrderedDict()
        self.cache_size = cache_size
        self.block_size = block_size
        self.bucket_size = cache_size // block_size
        self.idx = 0

        while True:
            text = self.fp.read(self.block_size)
            if not text:
                break
            self.length += len(text)
            self.offsets.append(self.fp.tell())

    def __len__(self):
        return self.length

    def __iter__(self):
        return self

    def __next__(self):
        char = self.get()
        self.next()
        return char

    def move(self, idx):
        self.idx = idx

    def next(self):
        self.idx = (self.idx + 1) % self.length

    def prev(self):
        self.idx = (self.idx - 1) % self.length

    def get(self):
        key = self.idx // self.block_size

        if key in self.cache:
            text = self.cache[key]
        else:
            if len(self.cache) >= self.bucket_size:
                self.cache.popitem(last=False)

            offset = self.offsets[key]
            self.fp.seek(offset, 0)
            text = self.fp.read(self.block_size)
            self.cache[key] = text

        self.cache.move_to_end(key)
        char = text[self.idx % self.block_size]
        return char


class Content:
    def __init__(self, config):
        self.margin = config.get("margin", [0, 0.1])
        self.reader = TextReader(**config.get("text", {}))
        self.font = components.BaseFont(**config.get("font", {}))
        self.layout = GridStack(config.get("layout", {}))
        self.textbox = TextBox(config.get("textbox", {}))
        
        # "주기" 헤더 추가
        self.header_text = "주기"

    def generate(self, size):
        width, height = size

        layout_left = width * np.random.uniform(self.margin[0], self.margin[1])
        layout_top = height * np.random.uniform(self.margin[0], self.margin[1])
        layout_width = max(width - layout_left * 2, 0)
        layout_height = max(height - layout_top * 2, 0)
        layout_bbox = [layout_left, layout_top, layout_width, layout_height]

        text_layers, texts = [], []
        layouts = self.layout.generate(layout_bbox)
        self.reader.move(np.random.randint(len(self.reader)))
        
        # 주기 Layer
        note_font = self.font.sample()
        note_font = {**note_font, "size": int(layouts[0][0][0][-1]*0.66)} # text_scale 반영

        note_layer = layers.TextLayer("주기", **note_font)
        note_layer.left = layout_left * np.random.uniform(0.4, 0.5)
        note_layer.top = layout_top * np.random.uniform(0.4, 0.5)
        text_layers.append(note_layer)
        texts.append("주기")

        for layout in layouts:
            font = self.font.sample()

            for bbox, align in layout:
                x, y, w, h = bbox
                text_layer, text = self.textbox.generate((w, h), self.reader, font)
                self.reader.prev()

                if text_layer is None:
                    continue

                text_layer.center = (x + w / 2, y + h / 2)
                if align == "left":
                    text_layer.left = x
                if align == "right":
                    text_layer.right = x + w
                text_layers.append(text_layer)
                texts.append(text)
                
        # 전체 Layout에 대한 Bounding Box
        def extract_x_coordinate(item):
            coordinate, _ = item
            x, _, _, _ = coordinate
            return x
        x_left = min([extract_x_coordinate(sublist[0]) for sublist in layouts])
        x_right = max([extract_x_coordinate(sublist[0]) for sublist in layouts])
        _, y_top, w, h = layouts[0][0][0]
        _, y_bottom, _, _ = layouts[-1][-1][0]
        bbox = list(map(int, [x_left*0.9, y_top*0.9, (x_right+w)*1.05, (y_bottom+h)*1.05]))

        return text_layers, texts, bbox
