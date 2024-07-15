from kivy.config import Config
Config.set('graphics', 'resizable', True)

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.logger import Logger

import shutil
import os

class ImageSelector(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)

    def open_image_selector(self):
        Logger.info("ImageSelector: Opening image selector")
        content = BoxLayout(orientation='horizontal', spacing=10)
        
        # Load images from assets folder
        images = [("assets/images/img1.jpeg", "img1"), ("assets/images/img2.jpeg", "img2"), ("assets/images/img3.jpeg", "img3")]
        self.checkboxes = {}

        for img_path, img_name in images:
            Logger.info(f"ImageSelector: Loading image {img_path}")
            box = BoxLayout(orientation='vertical', size_hint=(1, 1))
            img = Image(source=img_path, size_hint=(1, 1))
            checkbox = CheckBox(size_hint=(1, None), height=dp(40))
            self.checkboxes[img_name] = checkbox
            box.add_widget(img)
            box.add_widget(checkbox)
            content.add_widget(box)
        
        buttons = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), spacing=dp(10))
        copy_button = MDRaisedButton(text="Copy Selected", on_release=self.copy_selected)
        delete_button = MDRaisedButton(text="Delete Selected", on_release=self.delete_selected)
        buttons.add_widget(copy_button)
        buttons.add_widget(delete_button)
        
        root = BoxLayout(orientation='vertical')
        root.add_widget(content)
        root.add_widget(buttons)
        
        self.popup = Popup(title="Select Images", content=root, size_hint=(0.8, 0.8))
        self.popup.open()

    def copy_selected(self, instance):
        Logger.info("ImageSelector: Copying selected images")
        for img_name, checkbox in self.checkboxes.items():
            if checkbox.active:
                src = f"assets/images/{img_name}.jpeg"
                dst = f"assets/images/copied_{img_name}.jpeg"
                shutil.copyfile(src, dst)
        self.popup.dismiss()

    def delete_selected(self, instance):
        Logger.info("ImageSelector: Deleting selected images")
        for img_name, checkbox in self.checkboxes.items():
            if checkbox.active:
                os.remove(f"assets/images/{img_name}.jpeg")
        self.popup.dismiss()

class MainApp(MDApp):
    def build(self):
        Logger.info("MainApp: Building the app")
        self.title = "Image Selector"
        Builder.load_file('kv/main.kv')
        return ImageSelector()

    def show_image_selector(self):
        Logger.info("MainApp: Showing image selector")
        self.root.open_image_selector()

if __name__ == '__main__':
    MainApp().run()
