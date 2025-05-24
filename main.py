from kivy.lang import Builder
from kivy.uix.screenmanager import Screen, ScreenManager
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton
from kivy.uix.image import Image
from kivy.uix.behaviors import ButtonBehavior
from kivy.metrics import dp
from plyer import camera
import os
from datetime import datetime

KV = '''
ScreenManager:
    HomeScreen:
    CameraScreen:
    DriveScreen:
    AboutScreen:

<HomeScreen>:
    name: "home"
    BoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Asset Tracker"
            elevation: 5

        ScrollView:
            MDGridLayout:
                cols: 1
                padding: "10dp"
                spacing: "10dp"
                adaptive_height: True
                MDList:

                    OneLineAvatarIconListItem:
                        text: "Director's Car 1"
                        on_release: app.change_screen("camera")
                        IconLeftWidget:
                            icon: "car-hatchback"

                    OneLineAvatarIconListItem:
                        text: "Director's Car 2"
                        on_release: app.change_screen("camera")
                        IconLeftWidget:
                            icon: "car-sports"

                    OneLineAvatarIconListItem:
                        text: "Bus"
                        on_release: app.change_screen("camera")
                        IconLeftWidget:
                            icon: "bus-side"

                    OneLineAvatarIconListItem:
                        text: "Main Building Generator"
                        on_release: app.change_screen("camera")
                        IconLeftWidget:
                            icon: "office-building"

                    OneLineAvatarIconListItem:
                        text: "Hostel Generator"
                        on_release: app.change_screen("camera")
                        IconLeftWidget:
                            icon: "home-city"

                    OneLineAvatarIconListItem:
                        text: "Open Drive"
                        on_release: app.change_screen("drive")
                        IconLeftWidget:
                            icon: "file"

                    OneLineAvatarIconListItem:
                        text: "About"
                        on_release: app.change_screen("about")
                        IconLeftWidget:
                            icon: "account-circle"

<CameraScreen>:
    name: "camera"
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Camera"
            left_action_items: [["arrow-left", lambda x: app.change_screen("home")]]

        MDLabel:
            text: "Camera Screen"
            halign: "center"
            font_style: "H5"

        MDRaisedButton:
            text: "Capture Photo"
            pos_hint: {"center_x": 0.5}
            on_release: app.take_photo()

<DriveScreen>:
    name: "drive"
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "Drive"
            left_action_items: [["arrow-left", lambda x: app.change_screen("home")]]

        ScrollView:
            MDGridLayout:
                id: grid
                cols: 3
                padding: dp(5)
                spacing: dp(5)
                adaptive_height: True
                size_hint_y: None
                height: self.minimum_height

<AboutScreen>:
    name: "about"
    MDBoxLayout:
        orientation: "vertical"

        MDTopAppBar:
            title: "About Me"
            left_action_items: [["arrow-left", lambda x: app.change_screen("home")]]

        MDLabel:
            text: "this has to filled later"
            halign: "center"
            font_style: "H5"
'''

class ImgButton(ButtonBehavior, Image):
    pass

class HomeScreen(Screen):
    pass

class CameraScreen(Screen):
    pass

class DriveScreen(Screen):
    pass

class AboutScreen(Screen):
    pass

class CameraApp(MDApp):
    def build(self):
        self.photo_folder = os.path.join(self.user_data_dir, "MyCameraAppPhotos")
        os.makedirs(self.photo_folder, exist_ok=True)
        self.dialog = None
        return Builder.load_string(KV)

    def change_screen(self, name):
        self.root.current = name
        if name == "drive":
            self.load_drive()

    def take_photo(self):
        filename = datetime.now().strftime("IMG_%Y%m%d_%H%M%S.jpg")
        filepath = os.path.join(self.photo_folder, filename)
        try:
            camera.take_picture(filename=filepath, on_complete=lambda x: self.on_photo_taken(x))
        except NotImplementedError:
            self.show_error_dialog("Camera not available on this platform.")

    def on_photo_taken(self, filepath):
        if filepath and os.path.exists(filepath):
            print(f"Photo saved to {filepath}")
            if self.root.current == "drive":
                self.load_drive()
            else:
                self.change_screen("drive")
        else:
            self.show_error_dialog("Photo was not saved. Try again.")

    def load_drive(self):
        drive_screen = self.root.get_screen("drive")
        grid = drive_screen.ids.grid
        grid.clear_widgets()

        images = [f for f in os.listdir(self.photo_folder) if f.lower().endswith((".png", ".jpg", ".jpeg"))]
        images.sort(reverse=True)

        for img_name in images:
            img_path = os.path.join(self.photo_folder, img_name)
            img_btn = ImgButton(source=img_path, size_hint_y=None, height=dp(120), allow_stretch=True)
            img_btn.bind(on_release=lambda btn, p=img_path: self.show_image_popup(p))
            grid.add_widget(img_btn)

    def show_image_popup(self, img_path):
        if self.dialog:
            self.dialog.dismiss()
        content = Image(source=img_path, allow_stretch=True)
        self.dialog = MDDialog(
            title=os.path.basename(img_path),
            type="custom",
            content_cls=content,
            size_hint=(0.9, 0.9),
            buttons=[
                MDFlatButton(text="CLOSE", on_release=lambda x: self.dialog.dismiss())
            ],
        )
        self.dialog.open()

    def show_error_dialog(self, message):
        if self.dialog:
            self.dialog.dismiss()
        self.dialog = MDDialog(
            title="Error",
            text=message,
            buttons=[MDFlatButton(text="OK", on_release=lambda x: self.dialog.dismiss())],
        )
        self.dialog.open()

if __name__ == "__main__":
    CameraApp().run()
