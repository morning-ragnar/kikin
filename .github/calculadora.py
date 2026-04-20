from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.uix.textinput import TextInput
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.graphics import Color, RoundedRectangle

class CustomButton(Button):
    def __init__(self, is_operator=False, **kwargs):
        super().__init__(**kwargs)
        self.background_color = (0, 0, 0, 0)
        self.background_normal = ''
        self.font_size = '22sp'
        self.is_operator = is_operator
        self.normal_color = (0.3, 0.7, 1, 1) if is_operator else (0.92, 0.92, 0.92, 1)
        self.hover_color = (0.4, 0.8, 1, 1) if is_operator else (1, 1, 1, 1)
        self.text_color = (1, 1, 1, 1) if is_operator else (0.2, 0.2, 0.2, 1)
        self.color = self.text_color

        with self.canvas.before:
            Color(0, 0, 0, 0.2)
            self.shadow = RoundedRectangle(pos=(self.x + 2, self.y - 2),
                                           size=self.size, radius=[12])
            Color(*self.normal_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

        self.bind(pos=self.update_rect, size=self.update_rect)

    def update_rect(self, *args):
        self.shadow.pos = (self.x + 2, self.y - 2)
        self.shadow.size = self.size
        self.rect.pos = self.pos
        self.rect.size = self.size

    def on_press(self):
        with self.canvas.before:
            Color(*[x * 0.9 for x in self.normal_color[:3]] + [self.normal_color[3]])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])

    def on_release(self):
        with self.canvas.before:
            Color(*self.normal_color)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[12])


class CalculatorApp(App):
    def build(self):
        self.operators = ['+', '-', '*', '/']
        self.last_was_operator = None
        self.last_was_equal = False
        Window.size = (400, 600)
        Window.clearcolor = (0.12, 0.12, 0.12, 1)
        self.title = 'Calculadora'
        main_layout = BoxLayout(orientation='vertical', padding=15, spacing=15)
        display_layout = BoxLayout(size_hint_y=0.25, padding=3)

        self.input_box = TextInput(
            font_size=48,
            readonly=True,
            halign='right',
            multiline=False,
            background_color=(0.15, 0.15, 0.15, 1),
            foreground_color=(1, 1, 1, 1),
            cursor_color=(0, 0, 0, 0),
            padding=(25, 25),
            font_name='Roboto'
        )

        display_layout.add_widget(self.input_box)
        main_layout.add_widget(display_layout)

        buttons_layout = GridLayout(cols=4, spacing=12, padding=[2, 10, 2, 2])

        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            'C', '0', '=', '+'
        ]

        for button in buttons:
            is_operator = button in self.operators or button in ['C', '=']
            btn = CustomButton(
                text=button,
                is_operator=is_operator,
                on_press = self.on_button_press
            )
            buttons_layout.add_widget(btn)

        main_layout.add_widget(buttons_layout)

        return main_layout

    def on_button_press(self, instance):
        current = self.input_box.text
        button_text = instance.text

        if button_text == 'C':
            self.input_box.text = ''
        elif button_text == '=':
            try:
                result = eval(current)
                if isinstance(result, float):
                    self.input_box.text = f"{result:.2f}".rstrip('0').rstrip('.')
                else:
                    self.input_box.text = str(result)
                self.last_was_equal = True
            except Exception:
                self.input_box.text = 'Error'
        else:
            if self.last_was_equal and button_text in self.operators:
                self.last_was_equal = False
                self.input_box.text = current + button_text
            else:
                self.input_box.text += button_text

if __name__ == '__main__':
    CalculatorApp().run()





