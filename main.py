from kivy.config import Config
Config.set('graphics', 'resizable', True)

from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivymd.app import MDApp
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.dialog import MDDialog
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.toolbar import MDTopAppBar
from kivymd.uix.snackbar import Snackbar
from kivy.metrics import dp
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.checkbox import CheckBox
from kivy.logger import Logger
from kivy.uix.label import Label

import shutil
import os

class ImageSelector(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.spacing = dp(10)
        self.padding = dp(10)
        self.selected_images = []

        # File manager to select images
        self.file_manager = MDFileManager(
            exit_manager=self.exit_manager,
            select_path=self.select_path
        )
        self.file_manager.start_path = os.path.expanduser('~/Downloads')
        self.update_images()

    def open_file_manager(self, instance):
        self.file_manager.show(self.file_manager.start_path)

    def exit_manager(self, *args):
        self.file_manager.close()

    def select_path(self, path):
        self.preview_image(path)

    def preview_image(self, path):
        preview_content = BoxLayout(orientation='vertical', spacing=dp(10))
        img = Image(source=path, size_hint=(1, 0.8))
        button_box = BoxLayout(size_hint=(1, 0.2), spacing=dp(10))

        save_button = MDRaisedButton(text="Save", on_release=lambda x: self.save_image(path))
        delete_button = MDRaisedButton(text="Delete", on_release=lambda x: self.delete_image(path))
        close_button = MDRaisedButton(text="Close", on_release=lambda x: self.popup.dismiss())

        button_box.add_widget(save_button)
        button_box.add_widget(delete_button)
        button_box.add_widget(close_button)

        preview_content.add_widget(img)
        preview_content.add_widget(button_box)

        self.popup = Popup(title="Preview Image", content=preview_content, size_hint=(0.8, 0.8))
        self.popup.open()

    def save_image(self, path):
        if path not in self.selected_images:
            self.selected_images.append(path)
        self.popup.dismiss()
        Snackbar(text="Image saved successfully").show()
        self.update_images()

    def delete_image(self, path):
        if path in self.selected_images:
            self.selected_images.remove(path)
        self.popup.dismiss()
        Snackbar(text="Image deleted successfully").show()
        self.update_images()

    def update_images(self):
        self.clear_widgets()
        self.add_widget(MDTopAppBar(title="Image Selector", elevation=10))
        self.add_widget(MDRaisedButton(text="Select Images", size_hint=(None, None), size=(dp(200), dp(50)),
                                       pos_hint={"center_x": 0.5, "center_y": 0.5}, on_release=self.open_image_selector))
        self.add_widget(MDRaisedButton(text="Upload Images", size_hint=(None, None), size=(dp(200), dp(50)),
                                       pos_hint={"center_x": 0.5, "center_y": 0.5}, on_release=self.open_file_manager))

    def open_image_selector(self, instance):
        Logger.info("ImageSelector: Opening image selector")
        content = BoxLayout(orientation='vertical', spacing=10)

        # Load images from assets folder and selected images
        images = [("assets/images/img1.jpeg", "img1"), ("assets/images/img2.jpeg", "img2"), ("assets/images/img3.jpeg", "img3"), ("assets/images/img4.jpeg", "img4")]
        images.extend([(img, os.path.basename(img)) for img in self.selected_images])
        self.checkboxes = {}

        for i in range(0, len(images), 2):
            row = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(200))
            for img_path, img_name in images[i:i+2]:
                box = BoxLayout(orientation='vertical', size_hint=(0.5, 1))
                img = Image(source=img_path, size_hint=(1, 1))
                checkbox = CheckBox(size_hint=(1, None), height=dp(40))
                self.checkboxes[img_name] = checkbox
                box.add_widget(img)
                box.add_widget(checkbox)
                row.add_widget(box)
            content.add_widget(row)

        buttons = BoxLayout(orientation='horizontal', size_hint=(1, None), height=dp(50), spacing=dp(10))
        copy_button = MDRaisedButton(text="Copy Selected", on_release=self.copy_selected)
        delete_button = MDRaisedButton(text="Delete Selected", on_release=self.confirm_delete_selected)
        close_button = MDRaisedButton(text="Close", on_release=lambda x: self.popup.dismiss())
        buttons.add_widget(copy_button)
        buttons.add_widget(delete_button)
        buttons.add_widget(close_button)

        root = BoxLayout(orientation='vertical')
        root.add_widget(content)
        root.add_widget(buttons)

        self.popup = Popup(title="Select Images", content=root, size_hint=(0.8, 0.8))
        self.popup.open()

    def confirm_delete_selected(self, instance):
        confirm_dialog = MDDialog(
            text="Are you sure you want to delete the selected images?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: confirm_dialog.dismiss()),
                MDRaisedButton(text="Delete", on_release=lambda x: self.delete_selected(confirm_dialog))
            ]
        )
        confirm_dialog.open()

    def delete_selected(self, dialog):
        Logger.info("ImageSelector: Deleting selected images")
        for img_name, checkbox in self.checkboxes.items():
            if checkbox.active:
                try:
                    os.remove(f"assets/images/{img_name}.jpeg")
                except FileNotFoundError:
                    if os.path.isabs(img_name):
                        os.remove(img_name)
        self.popup.dismiss()
        Snackbar(text="Images deleted successfully").show()
        dialog.dismiss()

    def copy_selected(self, instance):
        confirm_dialog = MDDialog(
            text="Are you sure you want to copy the selected images?",
            buttons=[
                MDRaisedButton(text="Cancel", on_release=lambda x: confirm_dialog.dismiss()),
                MDRaisedButton(text="Copy", on_release=lambda x: self.confirm_copy_selected(confirm_dialog))
            ]
        )
        confirm_dialog.open()

    def confirm_copy_selected(self, dialog):
        Logger.info("ImageSelector: Copying selected images")
        for img_name, checkbox in self.checkboxes.items():
            if checkbox.active:
                src = img_name if os.path.isabs(img_name) else f"assets/images/{img_name}.jpeg"
                dst = f"assets/images/copied_{os.path.basename(img_name)}.jpeg"
                shutil.copyfile(src, dst)
        self.popup.dismiss()
        Snackbar(text="Images copied successfully").show()
        dialog.dismiss()

class MainApp(MDApp):
    def build(self):
        Logger.info("MainApp: Building the app")
        self.title = "Image Selector"
        Builder.load_file('kv/main.kv')
        return ImageSelector()

    def show_image_selector(self, instance):
        Logger.info("MainApp: Showing image selector")
        self.root.open_image_selector(instance)

if __name__ == '__main__':
    MainApp().run()
