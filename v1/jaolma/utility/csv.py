print(__name__)

class CSV(object):
    def _split(self, text):
        is_inside = False

        result = []
        current_string = ''

        for ch in text:
            if ch == self.delimiter and not is_inside:
                result.append(current_string)
                current_string = ''

            else:
                if ch == '"':
                    is_inside = not is_inside

                if ch.isascii() and not ch == '\n':
                    current_string += ch
        
        result.append(current_string)

        return result

    def __init__(self, filename: str, delimiter: str = ';'):
        self.delimiter = delimiter

        self.filename = filename
        if not filename.endswith('.csv'):
            self.filename = filename + '.csv'

        self.typedict = {'int': int, 'float': float, 'str': str, 'bool': bool}
        self.type_row = all([typename in self.typedict for typename in self.get_types()])

    def read(self, cols: list = None, filter: callable = None) -> list:
        with open(self.filename, 'r') as f:
            rows = [self._split(row) for row in f]

        header = rows[0]
        types = rows[1]
        rows = rows[1:]

        def convert(val, t):
            if not self.type_row:
                return val
                
            if val == 'None':
                return None

            return self.typedict[t](val)
        
        if self.type_row:
            rows = rows[1:]

        data = []
        for row in rows:
            if all(cell == '' for cell in row):
                continue
            
            if self.type_row:
                _row = {key: convert(value, t) for key, value, t in zip(header, row, types) if cols == None or key in cols}
            else:
                _row = {key: value for key, value, t in zip(header, row, types) if cols == None or key in cols}

            if filter == None or filter(_row):
                data.append(_row)

        return data

    def write(self, content: list):
        header = self.get_header()
        types = self.get_types()

        with open(self.filename, 'w') as f:
            f.write(self.delimiter.join(header) + '\n')

            if self.type_row:
                f.write(self.delimiter.join(types) + '\n')

            for row in content:
                f.write(self.delimiter.join([str(el) for el in row.values()]) + '\n')

    def get_header(self) -> list:
        with open(self.filename, 'r') as f:
            rows = [self._split(row) for row in f]

        return rows[0]

    def get_types(self) -> list:
        with open(self.filename, 'r') as f:
            rows = [self._split(row) for row in f]

        return rows[1]

    def set_column_name(self, current_name: str, new_name: str):
        pass

    def __len__(self):
        pass

    def __add__(self, other_file):
        pass