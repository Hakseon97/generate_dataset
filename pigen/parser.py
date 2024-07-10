import os, sys
from pathlib import Path
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
project_dir = Path(os.path.split(os.path.realpath(__file__))[0]) / ".."

def argument_parser():
    """
        CLI arguments.
    """

    parser = argparse.ArgumentParser(
        description="Generate synthetic paragraph images for text recognition."
    )

    """
        Options you really want to change
    """
    core_config = parser.add_argument_group("core", "Core Configurations")

    """
        Output configuration (count, directory, extension, ...)
    """
    output_config = parser.add_argument_group("output", "Output Configurations")
    
    core_config.add_argument(
        "-c",
        "--count",
        type=int,
        nargs="?",
        help="The number of images to be created.",
        required=True,
    )
    core_config.add_argument(
        "-out",
        "--output_dir",
        type=str,
        nargs="?",
        help="The output directory",
        default="out/"
    )
    output_config.add_argument(
        "-maxl",
        "--max_length",
        type=int,
        nargs="?",
        help="Set the maximum number of words for each generated sample.",
        default=7,
    )
    output_config.add_argument(
        "-minl",
        "--min_length",
        type=int,
        nargs="?",
        help="Define how many words should be included in each generated sample.",
        default=1,
    )
    output_config.add_argument(
        "-ns",
        "--n_sentence",
        type=int,
        nargs="?",
        help="Define the number of sentences per paragraph.",
        default=5,
    )
    output_config.add_argument(
        "-np",
        "--n_paragraph",
        type=int,
        nargs="?",
        help="Define the number of paragraphs to be created in a image.",
        default=4,
    )
    output_config.add_argument(
        "-e",
        "--extension",
        type=str,
        nargs="?",
        help="Define the extension to save the image with",
        default="jpg",
    )
    # output_config.add_argument(
    #     "-na",
    #     "--name_format",
    #     type=int,
    #     help="Define how the produced files will be named.\
    #         0: [TEXT]_[ID].[EXT],\
    #         1: [ID]_[TEXT].[EXT],\
    #         2: [ID].[EXT] + one file labels.txt containing id-to-label mappings,\
    #         3: [ID].[EXT]",
    #     default=3,
    # )

    """
        Text Sources (dict/random/string/wiki/file)
    """
    source_ex = parser.add_mutually_exclusive_group()
    source_ex.add_argument(
        "-wk",
        "--wikipedia",
        action="store_true",
        help="Use Wikipedia as the source text for the generation.",
        default=False,
    )
    source_ex.add_argument(
        "-dt",
        "--dict",
        "--dictionary",
        type=str,
        help="Specify the name of the dictionary to be used.\
            Each lines are separated by .splitlines(), and the orders of the lines are scrambled.",
        default="ksx1001.txt"
    )
  
    """
        Text configuration (font, color, orientation, spacing, ...)
    """
    text_config = parser.add_argument_group("text", "Text configurations")
    
    text_config.add_argument(
        "-sw",
        "--space_width",
        type=float,
        nargs="?",
        help="Define the width of the spaces between words. 2.0 means twice the normal space width",
        default=1.0,
    )
    text_config.add_argument(
        "-cs",
        "--character_spacing",
        type=int,
        nargs="?",
        help="Define the width of the spaces between characters. 2 means two pixels",
        default=0,
    )
    text_config.add_argument(
        "-ft",
        "--font",
        type=str,
        nargs="?",
        help="Define font to be used",
        default="NanumGothic.ttf",
    )
    text_config.add_argument(
        "-fs",
        "--fontsize",
        type=int,
        nargs="?",
        help="Define fontsize to be used",
        default=20,
    )

    """
        # Image constructions (size, background, ...)
    """
    image_config = parser.add_argument_group("image", "Image construction details")
    core_config.add_argument(
        "-f",
        "--format",
        "--height",
        type=int,
        nargs="?",
        help="Define the height of the produced images if horizontal, else the width",
        default=32,
    )
    image_config.add_argument(
        "-wd",
        "--width",
        type=int,
        nargs="?",
        help="Define the width of the resulting image. If not set it will be the width of the text + 10. If the width of the generated text is bigger that number will be used",
        default=400,
    )

    image_config.add_argument(
        "-b",
        "--background",
        type=int,
        nargs="?",
        help="Define what kind of background to use. 0: Gaussian Noise, 1: Plain white, 2: Quasicrystal, 3: Image",
        default=0,
    )
    image_config.add_argument(
        "-om",
        "--output_mask",
        type=int,
        help="Define if the generator will return masks for the text",
        default=0,
    )
    image_config.add_argument(
        "-al",
        "--alignment",
        type=int,
        nargs="?",
        help="Define the alignment of the text in the image. Only used if the width parameter is set. 0: left, 1: center, 2: right",
        default=1,
    )
    image_config.add_argument(
        "-fi",
        "--fit",
        action="store_true",
        help="Apply a tight crop around the rendered text",
        default=False,
    )
    image_config.add_argument(
        "-id",
        "--image_dir",
        type=str,
        nargs="?",
        help="Define an image directory to use when background is set to image",
        default=os.path.join(project_dir, "resources", "images"),
    )

    """
        Others
    """
    others_config = parser.add_argument_group("others", "Other configurations")
    core_config.add_argument(
        "-t",
        "--thread_count",
        type=int,
        nargs="?",
        help="Define the number of thread to use for image generation",
        default=1,
    )
    return parser