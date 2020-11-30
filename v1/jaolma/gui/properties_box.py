import PySimpleGUI as sg

class PropertiesBox:
    def __init__(self):
        self.prop_text = sg.Text('Properties', font=('Any', 11, 'bold'))
        self.init_text = sg.Text('Press a feature to show it in this window.')

        self.id = '23211512'

        cw, ch = 400, 1000

        self.attributes = [[sg.Text('', visible=False, key=f'{self.id}_att_{i}', font=('Any', 10), size=(cw, None), auto_size_text=False, enable_events=True)] for i in range(50)]

        self.properties = sg.Column([[self.prop_text]] + self.attributes + [[self.init_text]], size=(cw, ch), vertical_alignment='top')
        
        self.visible = True

        self.attributes = []


    def get_properties(self):
        return self.properties

    def set_attributes(self, window, attributes):
        self.init_text.update(visible=False)

        for i, attribute_name in enumerate(attributes):
            attribute_entry = window.find(f'{self.id}_att_{i}')
            attribute_entry.update(value=f'{attribute_name}: {attributes[attribute_name]}', visible=True)

        for i in range(50 - len(attributes)):
            i += len(attributes)
            attribute_entry = window.find(f'{self.id}_att_{i}')
            attribute_entry.update(visible=False)

        self.attributes = attributes