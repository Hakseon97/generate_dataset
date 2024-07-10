import os, sys
from datetime import datetime
import errno
from pathlib import Path
from glob import glob

import random

from PIL import Image, ImageDraw, ImageFont
import textwrap
from tqdm import tqdm

from pigen.parser import argument_parser
from pigen.utils import create_strings_from_wikipedia

base_dir = Path(os.path.realpath(__file__)).parent
resource_dir = base_dir / "resources/"

def main():
    args = argument_parser().parse_args()
    
    # Create the directory if it does not exist.
    try:
        os.makedirs(args.output_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    
    # Create font (path) list
    font_path = Path(resource_dir) / "fonts"

    if list(font_path.glob('*.ttf')):
        fonts = list(glob(str(font_path / "*.ttf")))
        rnd_font = random.randrange(0, len(fonts))
        select_font = ImageFont.truetype(fonts[rnd_font], args.fontsize)
    else:
        sys.exit("Cannot open font")

    # 이미지 고정 config
    margin = 20
    line_height = 30
    paragraph_spacing = 20

    # 텍스트 크기 계산
    img_width = margin * 2
    img_height = margin * 2
    wrapped_paragraphs = []
    
    sentences = create_strings_from_wikipedia(args.min_length, args.max_length, args.n_sentence*args.n_paragraph, lang='ko')
    paragraphs = [' '.join(sentences[i:i+args.n_sentence]) 
                  for i in range(0, len(sentences), args.n_sentence)]    

    for paragraph in paragraphs:
        wrapped = textwrap.wrap(paragraph, width=args.width//10)  # 대략적인 폭 추정
        wrapped_paragraphs.append(wrapped)
        w = max([select_font.getbbox(line)[2] - select_font.getbbox(line)[0] for line in wrapped])
        h = len(wrapped) * line_height
        img_width = max(img_width, w + margin * 2)
        img_height += h + paragraph_spacing

    img_height -= paragraph_spacing  # 마지막 문단 후의 추가 간격 제거
    
    # 이미지 생성
    background_color = (255, 255, 255)  # 흰색
    text_color = (0, 0, 0)  # 검은색
    image = Image.new('RGB', (img_width, img_height), background_color)
    draw = ImageDraw.Draw(image)
    
    # 텍스트 그리기
    y_text = margin
    for wrapped in wrapped_paragraphs:
        for line in wrapped:
            draw.text((margin, y_text), line, font=select_font, fill=text_color)
            y_text += line_height
        y_text += paragraph_spacing
    
    # 이미지 저장
    i=0
    current_info = datetime.now().strftime(f"%y%m%d_%H%M%S_{i}")
    img_name = current_info + str(i)
    image.save(img_name + '.' + args.extension)
    
if __name__ == "__main__":
    main()