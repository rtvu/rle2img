import re

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
