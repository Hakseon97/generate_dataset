import os
import random
import json
import yaml
from PIL import Image

def load_config(config_path):
    with open(config_path, 'r') as config_file:
        return yaml.safe_load(config_file)
    
def convert_to_yolo_format(bbox, image_width, image_height):
    x, y, w, h = bbox
    
    x_center = (x + w/2) / image_width
    y_center = (y + h/2) / image_height
    width = w / image_width
    height = h / image_height
    
    return [x_center, y_center, width, height]

def process_images(config_data):
    input_dir = config_data.get('background').get('input_dir')
    output_dir = config_data.get('background').get('output_dir')
    background_dir = config_data.get('background').get('background_dir')
    background_size = config_data.get('background').get('size')
    metadata_path = os.path.join(input_dir, "metadata.jsonl")
    output_metadata_path = os.path.join(output_dir, "metadata.jsonl")

    background_images = [f for f in os.listdir(background_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    # 메타데이터 로드
    with open(metadata_path, 'r', encoding='utf-8') as f:
        metadata_list = [json.loads(line) for line in f]

    updated_metadata_list = []
    for metadata in metadata_list:
        filename = metadata['file_name']
        input_image_path = os.path.join(input_dir, filename)
        
        if not os.path.exists(input_image_path):
            print(f"Image not found for {filename}, skipping...")
            continue
        
        # 이미지 로드
        foreground = Image.open(input_image_path).convert("RGBA")
        
        # 랜덤 배경 선택 및 로드
        background_path = os.path.join(background_dir, random.choice(background_images))
        background = Image.open(background_path).convert("RGBA")
        background = background.resize(background_size, Image.NEAREST)
        
        # 랜덤 위치 계산
        x_offset = random.randint(0, max(0, background.size[0] - foreground.size[0]))
        y_offset = random.randint(0, max(0, background.size[1] - foreground.size[1]))
        
        # 이미지 합성
        new_image = Image.new("RGBA", background.size)
        new_image.paste(background, (0, 0))
        new_image.paste(foreground, (x_offset, y_offset), foreground)
        
        # 메타데이터 업데이트
        gt_parse = json.loads(metadata['ground_truth'])['gt_parse']
        roi = gt_parse['roi']
        roi_yolo = dict()
        for key in roi:
            x, y, w, h = roi[key]
            roi[key] = [x + x_offset, y + y_offset, w, h]
            roi_yolo[key] = convert_to_yolo_format(roi[key], new_image.width, new_image.height)
        
        gt_parse['roi_yolo'] = roi_yolo  
        metadata['ground_truth'] = json.dumps({"gt_parse": gt_parse}, ensure_ascii=False)
        
        # 결과 저장
        output_image_path = os.path.join(output_dir, filename)
        new_image.convert("RGB").save(output_image_path)
        
        updated_metadata_list.append(metadata)
        print(f"Processed {filename}")
    
    # 업데이트된 메타데이터를 JSONL 파일로 저장
    with open(output_metadata_path, 'w', encoding='utf-8') as f:
        for metadata in updated_metadata_list:
            f.write(json.dumps(metadata, ensure_ascii=False) + '\n')

    print("Processing complete.")

if __name__ == "__main__":
    config_path = "config.yaml"
    config_data = load_config(config_path)
    process_images(config_data)