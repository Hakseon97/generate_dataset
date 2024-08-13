import json
import os
import re
from typing import Any, List

import numpy as np
from elements import Document
from PIL import Image
from synthtiger import components, layers, templates


class Note(templates.Template):
    def __init__(self, config=None):
        super().__init__(config)
        if config is None:
            config = {}

        self.landscape = config.get("landscape", 0.5)
        self.short_size = config.get("short_size", [720, 1024])
        self.aspect_ratio = config.get("aspect_ratio", [1, 2])
        self.document = Document(config.get("document", {}))

    def generate(self):
        landscape = np.random.rand() < self.landscape
        short_size = np.random.randint(self.short_size[0], self.short_size[1] + 1)
        aspect_ratio = np.random.uniform(self.aspect_ratio[0], self.aspect_ratio[1])
        long_size = int(short_size * aspect_ratio)
        size = (long_size, short_size) if landscape else (short_size, long_size)

        paper_layer, text_layers, texts, layouts_bbox = self.document.generate(size)

        document_group = layers.Group([*text_layers, paper_layer])
        document_space = np.clip(size - document_group.size, 0, None)
        document_group.left = np.random.randint(document_space[0] + 1)
        document_group.top = np.random.randint(document_space[1] + 1)
        
        bg_layer = layers.RectLayer(size, (255, 255, 255, 255))
        layer = layers.Group([*document_group.layers, bg_layer]).merge()
     
        # 주기 Bounding Box
        x,y,w,h = map(int, text_layers[0].bbox)
         
        ## Image Drawing
        image = layer.output(bbox=[0, 0, *size])
        image = Image.fromarray(image[..., :3].astype(np.uint8))
        
        # combine crop coordinates
        crop_coords = [x,y] + layouts_bbox[2:]
        crop_img = image.crop(crop_coords)

        # label
        label = "".join(texts).strip()
        label = re.sub(r"\s+", " ", label)

        data = {
            "image": np.array(crop_img),
            "label": label,
            "roi": {
                "note": [0, 0, w, h],
                "layouts": [a - b for a, b in zip(layouts_bbox, [x,y,x,y])]
            },
        }
        return data

    def init_save(self, root):
        if not os.path.exists(root):
            os.makedirs(root, exist_ok=True)

    def save(self, root, data, idx):
        image = data["image"]
        label = data["label"]
        roi = data["roi"]

        output_dirpath = os.path.join(root)

        # save image
        image_filename = f"note_ko_{idx}.jpg"
        image_filepath = os.path.join(output_dirpath, image_filename)
        os.makedirs(os.path.dirname(image_filepath), exist_ok=True)
        image = Image.fromarray(image[..., :3].astype(np.uint8))
        image.save(image_filepath, quality=95)

        # save metadata (gt_json)
        metadata_filename = "metadata.jsonl"
        metadata_filepath = os.path.join(output_dirpath, metadata_filename)
        os.makedirs(os.path.dirname(metadata_filepath), exist_ok=True)

        metadata = self.format_metadata(
            image_filename=image_filename,
            keys=["text_sequence", "roi"],
            values=[label, roi]
        )
        
        with open(metadata_filepath, "a") as fp:
            json.dump(metadata, fp, ensure_ascii=False)
            fp.write("\n")

    def end_save(self, root):
        pass

    def format_metadata(self, image_filename: str, keys: List[str], values: List[Any]):
        """
        Fit gt_parse contents to huggingface dataset's format
        keys and values, whose lengths are equal, are used to constrcut 'gt_parse' field in 'ground_truth' field
        Args:
            keys: List of task_name
            values: List of actual gt data corresponding to each task_name
        """
        assert len(keys) == len(values), "Length does not match: keys({}), values({})".format(len(keys), len(values))

        gt_parse = {"gt_parse": dict(zip(keys, values))}
        gt_parse_str = json.dumps(gt_parse, ensure_ascii=False)
        metadata = {"file_name": image_filename, "ground_truth": gt_parse_str}
        return metadata
