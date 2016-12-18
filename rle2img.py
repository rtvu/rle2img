from PIL import Image, ImageDraw
import argparse
import logging
import os
import re
import sys


def setup_parser():
    class Parser(argparse.ArgumentParser):
        def error(self, message):
            # Superclass only report error message.
            # Override to also show print help.
            self._print_message(('%s: error: %s\n\n') % (self.prog, message))
            self.print_help(sys.stderr)
            self.exit(2)

    parser = Parser(description = "convert a Conway's Game of Life rle file" \
                                  + " to an image file",
                    formatter_class = argparse.RawTextHelpFormatter,
                    )
    parser.add_argument('source',
                        help = 'path to rle file',
                        )
    parser.add_argument('target',
                        action = 'store',
                        nargs = '?',
                        default = '',
                        help = "optional: path to image file, extension" \
                               + " determines image format",
                        )
    return parser


class Configuration:
    @staticmethod
    def read_configuration(config, comment_flag='#'):
        config_file = open(config)
        config_string = config_file.read()
        config_file.close()
        config_raw_lines = config_string.split('\n')
        config_lines = Configuration.clean_lines(config_raw_lines)
        return config_lines

    @staticmethod
    def clean_lines(lines, comment_flag='#'):
        def decomment(raw_line):
            return raw_line.partition(comment_flag)[0]
        def trim(raw_line):
            return raw_line.strip()
        def notempty(line):
            return line != ''

        decomment_lines = map(decomment, lines)
        trimmed_lines = map(trim, decomment_lines)
        nonempty_lines = filter(notempty, trimmed_lines)
        return nonempty_lines


class RLE(Configuration):
    def __init__(self, rle):
        dimensions_regex = \
            'x\s*=\s(\d+)\s*,\s*y\s*=\s(\d+)' # regex matches "x = #, y = #"

        def exit_unless(success):
            if not success: exit('Read RLE error.')

        lines = self.read_configuration(rle)

        match = re.search(dimensions_regex, lines[0])
        if match != None:
            x = int(match.group(1))
            y = int(match.group(2))
            self.dimensions = (x, y)
        else:
            exit_unless(False)

        self.specifications = ''.join(lines[1:])

    def next_sequence(self):
        specifications_regex = \
            '(\$)|(!)|(\d*b)|(\d*o)' # regex matches $, !, #b, #o

        match = re.search(specifications_regex, self.specifications)
        specification = match.group()
        self.specifications = self.specifications[len(specification):]
        if specification == '$':
            return ('$', 0)
        elif specification == '!':
            self.specifications = '!'
            return ('!', 0)
        else:
            if len(specification) == 1:
                specification = '1' + specification
            return (specification[-1], int(specification[0:-1]))


def get_paths(source, target):
    def exit_unless(success):
        if not success: exit('File error.')

    if os.path.isfile(source):
        (source_path, source_file) = os.path.split(source)
        (target_path, target_file) = os.path.split(target)

        if target_path == '':
            target_path = source_path

        if target_file == '':
            (source_root, source_ext) = os.path.splitext(source_file)
            target_file = source_root + '.png'

        target = os.path.join(target_path, target_file)
        return (source, target)
    else:
        exit_unless(False)


def make_image(source, target):
    rle = RLE(source)

    im = Image.new('RGBA', rle.dimensions, 'white')
    draw = ImageDraw.Draw(im)

    xp = 0
    yp = 0
    (symbol, length) = rle.next_sequence()
    while symbol != '!':
        if symbol == '$':
            xp = 0
            yp += 1
        elif symbol == 'b':
            xp += length
        else:
            draw.line([(xp, yp), (xp + length - 1, yp)], 'black')
            xp += length
        (symbol, length) = rle.next_sequence()

    im.save(target)


def main(argv):
    parser = setup_parser()
    parsed_args = parser.parse_args(argv)
    source = parsed_args.source
    target = parsed_args.target
    (source, target) =  get_paths(source, target)
    make_image(source, target)


if __name__ == '__main__':
    main(sys.argv[1:])
