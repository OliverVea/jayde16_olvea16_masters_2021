

class CSV(object):
    def _split(self, text):
        openers = {'[': 0, '{': 0, '(': 0, '"': False, "'": False}

        is_inside = lambda openers: (openers['['] > 0) or (openers['{']) > 0 or (openers['(']) > 0 or openers['"'] or openers["'"]

        result = []
        current_string = ''

        for ch in text:
            if ch == self.delimiter and not is_inside(openers):
                result.append(current_string)
                current_string = ''

            else:
                if ch == '[':
                    openers['['] += 1
                elif ch == ']':
                    openers['['] -= 1

                elif ch == '{':
                    openers['{'] += 1
                elif ch == '}':
                    openers['{'] -= 1

                elif ch == '(':
                    openers['('] += 1
                elif ch == ')':
                    openers['('] -= 1

                elif ch == '"':
                    openers['"'] = not openers['"']

                elif ch == "'":
                    openers["'"] = not openers["'"]

                if ch.isascii() and not ch in ['\n']:
                    current_string += ch
        
        result.append(current_string)

        return result

    def __init__(self, filename: str, delimiter: str = ';', ):
        self.delimiter = delimiter

        self.filename = filename
        if not filename.endswith('.csv'):
            self.filename = filename + '.csv'

        pass

    def read(self) -> list:
        pass

    def write(self, content: list):
        pass

    def get_header(self) -> list:
        pass

    def set_column_name(self, current_name: str, new_name: str):
        pass

    def __len__(self):
        pass

    def __add__(self, other_file):
        pass