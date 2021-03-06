"""
Convert an html file back into an xml document (for evaluation purposes)
"""
from bs4 import BeautifulSoup
import re
import os
import glob
import codecs
from ..postprocess.postprocess import not_ocr
from pascal_voc_writer import Writer
from argparse import ArgumentParser


def iterate_and_update_writer(soup, writer):
    for seg_type in soup.find_all('div', not_ocr):
        seg_class = ' '.join(seg_type['class'])
        hocr = seg_type.find_next('div', 'hocr')
        coordinates = hocr['data-coordinates']
        coordinates = coordinates.split(' ')
        coordinates = [int(x) for x in coordinates]
        coordinates = tuple(coordinates)
        writer.addObject(seg_class, *coordinates)
    return writer


def html2xml(html_path, output_path):
    for f in glob.glob(os.path.join(html_path, "*.html")):
        with codecs.open(f, "r", "utf-8") as fin:
            soup = BeautifulSoup(fin, 'html.parser')
            writer = Writer(f'{os.path.basename(f)[:-5]}.png', 1920, 1920)
            writer = iterate_and_update_writer(soup, writer)
            writer.save(f'{os.path.join(output_path, os.path.basename(f)[:-5])}.xml')


if __name__ == '__main__':
    parser = ArgumentParser(description='Convert html output to xml output')
    parser.add_argument('htmldir', type=str, help='Path to html directory')
    parser.add_argument('outputdir', type=str, help='Path to output directory')
    args = parse_args()
    html2xml(args.htmldir, args.outputdir)

