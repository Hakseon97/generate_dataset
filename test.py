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

i=0
current_info = datetime.now().strftime(f"%y%m%d_%H%M%S")
img_name = current_info + str(i)
args = argument_parser().parse_args()
print(img_name + '.' + args.extension)

