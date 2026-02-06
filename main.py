from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout

class HelloApp(App):
    def build(self):
        box = BoxLayout(orientation='vertical')
        btn = Button(text='Hello from Kivy → APK',
                     font_size='24sp',
                     size_hint=(1, .3))
        btn.bind(on_release=lambda _: setattr(btn, 'text', 'Clicked!'))
        box.add_widget(btn)
        return box

if __name__ == '__main__':
    HelloApp().run()
