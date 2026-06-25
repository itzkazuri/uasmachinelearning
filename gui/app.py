import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, Gio, GLib, GdkPixbuf
import os
import subprocess
import threading
from src.predict import FruitClassifier

class FruitApp(Adw.Application):
    def __init__(self, **kwargs):
        super().__init__(application_id='com.itzkazuri.FruitClassifier',
                         flags=Gio.ApplicationFlags.FLAGS_NONE,
                         **kwargs)
        self.server_process = None
        self.classifier = FruitClassifier()

    def do_activate(self):
        # Adwaita Style Manager
        style_manager = Adw.StyleManager.get_default()
        style_manager.set_color_scheme(Adw.ColorScheme.PREFER_LIGHT)

        self.win = Adw.ApplicationWindow(application=self, title="Fruit Classifier Pro")
        self.win.set_default_size(900, 750)

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.win.set_content(main_box)

        header = Adw.HeaderBar()
        main_box.append(header)

        view_switcher_title = Adw.ViewSwitcherTitle()
        header.set_title_widget(view_switcher_title)

        self.view_stack = Adw.ViewStack()
        main_box.append(self.view_stack)
        view_switcher_title.set_stack(self.view_stack)

        # --- PAGE 1: CLASSIFIER ---
        classifier_scroll = Gtk.ScrolledWindow()
        classifier_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        # Fix GTK 4 Margins
        classifier_page.set_margin_top(20)
        classifier_page.set_margin_bottom(20)
        classifier_page.set_margin_start(20)
        classifier_page.set_margin_end(20)
        classifier_scroll.set_child(classifier_page)
        
        # Image Preview Area
        img_frame = Gtk.Frame()
        img_frame.set_valign(Gtk.Align.CENTER)
        img_frame.set_halign(Gtk.Align.CENTER)
        img_frame.set_size_request(350, 350)
        
        self.preview_image = Gtk.Image()
        self.preview_image.set_pixel_size(350)
        self.preview_image.set_from_icon_name("image-x-generic-symbolic") # Fix GTK 4 method
        img_frame.set_child(self.preview_image)
        classifier_page.append(img_frame)

        # Upload Button
        upload_btn = Gtk.Button(label="Pilih Foto Buah untuk Diklasifikasi")
        upload_btn.set_halign(Gtk.Align.CENTER)
        upload_btn.add_css_class("suggested-action")
        upload_btn.add_css_class("pill")
        upload_btn.set_margin_top(10)
        upload_btn.connect("clicked", self.on_upload_clicked)
        classifier_page.append(upload_btn)

        # Results Group
        self.results_group = Adw.PreferencesGroup(title="Analisis Buah")
        self.results_group.set_visible(False)
        
        self.pred_row = Adw.ActionRow(title="Jenis Buah (Prediksi Utama)", subtitle="-")
        self.rotten_row = Adw.ActionRow(title="Estimasi Kebusukan", subtitle="0%")
        
        self.results_group.add(self.pred_row)
        self.results_group.add(self.rotten_row)
        
        # Similarity List
        self.similarity_expander = Adw.ExpanderRow(title="Kemiripan dengan Buah Lain")
        self.results_group.add(self.similarity_expander)
        
        classifier_page.append(self.results_group)

        self.view_stack.add_titled_with_icon(classifier_scroll, "classifier", "Klasifikasi", "image-x-generic-symbolic")

        # --- PAGE 2: SERVER CONTROL ---
        server_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        server_page.set_margin_top(20)
        server_page.set_margin_bottom(20)
        server_page.set_margin_start(20)
        server_page.set_margin_end(20)

        status_group = Adw.PreferencesGroup(title="Status Server API")
        self.status_row = Adw.ActionRow(title="API Backend", subtitle="Offline")
        status_group.add(self.status_row)
        
        model_found = os.path.exists('models/fruit_model.keras')
        self.model_row = Adw.ActionRow(title="AI Model Status", 
                                      subtitle="Ready" if model_found else "Not Found (Training required)")
        status_group.add(self.model_row)
        server_page.append(status_group)

        btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=15)
        btn_box.set_halign(Gtk.Align.CENTER)
        
        self.start_btn = Gtk.Button(label="Jalankan Server API")
        self.start_btn.add_css_class("suggested-action")
        self.start_btn.connect("clicked", self.on_start_server)
        
        self.stop_btn = Gtk.Button(label="Matikan Server")
        self.stop_btn.add_css_class("destructive-action")
        self.stop_btn.set_sensitive(False)
        self.stop_btn.connect("clicked", self.on_stop_server)

        btn_box.append(self.start_btn)
        btn_box.append(self.stop_btn)
        server_page.append(btn_box)

        self.view_stack.add_titled_with_icon(server_page, "server", "Server Management", "network-server-symbolic")

        self.win.present()

    def on_upload_clicked(self, btn):
        dialog = Gtk.FileChooserNative(title="Pilih Gambar Buah",
                                     transient_for=self.win,
                                     action=Gtk.FileChooserAction.OPEN)
        
        filter_img = Gtk.FileFilter()
        filter_img.set_name("Gambar (JPG/PNG)")
        filter_img.add_mime_type("image/jpeg")
        filter_img.add_mime_type("image/png")
        dialog.add_filter(filter_img)

        dialog.connect("response", self.on_file_dialog_response)
        dialog.show()

    def on_file_dialog_response(self, dialog, response):
        if response == Gtk.ResponseType.ACCEPT:
            file_path = dialog.get_file().get_path()
            self.process_image(file_path)
        dialog.destroy()

    def process_image(self, file_path):
        try:
            pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(file_path, 350, 350, True)
            self.preview_image.set_from_pixbuf(pixbuf)
            
            self.pred_row.set_subtitle("Menganalisis...")
            self.rotten_row.set_subtitle("...")
            self.results_group.set_visible(True)
            
            thread = threading.Thread(target=self.run_prediction, args=(file_path,))
            thread.daemon = True
            thread.start()
        except Exception as e:
            print(f"Error loading image: {e}")

    def run_prediction(self, file_path):
        if self.classifier.model is None:
            self.classifier.load()
            
        result = self.classifier.predict(file_path)
        GLib.idle_add(self.update_classification_results, result)

    def update_classification_results(self, result):
        if "error" in result:
            self.pred_row.set_subtitle(result["error"])
            return

        self.pred_row.set_subtitle(f"{result['prediction']} (Pasti {result['confidence']*100:.1f}%)")
        self.rotten_row.set_subtitle(f"{result['rotten_percentage']:.1f}% Busuk")
        
        sim_text = []
        others = result.get("other_similarities", {})
        sorted_others = sorted(others.items(), key=lambda x: x[1], reverse=True)
        for name, prob in sorted_others[:4]:
            sim_text.append(f"{name}: {prob:.1f}%")
        
        self.similarity_expander.set_subtitle(", ".join(sim_text))

    def on_start_server(self, btn):
        self.start_btn.set_sensitive(False)
        self.status_row.set_subtitle("Menghidupkan Server...")
        threading.Thread(target=self.run_server_task, daemon=True).start()

    def run_server_task(self):
        try:
            cmd = ["./run_python.sh", "-m", "uvicorn", "api.server:app", "--host", "127.0.0.1", "--port", "8000"]
            self.server_process = subprocess.Popen(cmd)
            GLib.idle_add(self.status_row.set_subtitle, "Aktif di http://127.0.0.1:8000")
            GLib.idle_add(self.stop_btn.set_sensitive, True)
            self.server_process.wait()
        except Exception as e:
            print(f"Server error: {e}")
            GLib.idle_add(self.update_ui_server_stopped)

    def on_stop_server(self, btn):
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
        self.update_ui_server_stopped()

    def update_ui_server_stopped(self):
        self.status_row.set_subtitle("Offline")
        self.start_btn.set_sensitive(True)
        self.stop_btn.set_sensitive(False)

def launch_gui():
    app = FruitApp()
    app.run(None)
