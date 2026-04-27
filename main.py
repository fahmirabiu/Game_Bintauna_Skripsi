import json
import os
import random

# --- KIVY IMPORTS ---
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.image import Image
from kivy.uix.popup import Popup
from kivy.uix.slider import Slider
from kivy.core.window import Window
from kivy.core.audio import SoundLoader
from kivy.clock import Clock
from kivy.graphics import Color, RoundedRectangle, Ellipse
from kivy.properties import NumericProperty
from kivy.animation import Animation
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView

# --- FUNGSI WARNA ---
def hex_to_rgb(hex_code):
    hex_code = hex_code.lstrip('#')
    return tuple(int(hex_code[i:i+2], 16) / 255.0 for i in (0, 2, 4)) + (1,)

# --- KONFIGURASI TEMA ---
THEMES = {
    'light': {
        'BG_MAIN': hex_to_rgb('F8F9FA'),
        'TEXT_MAIN': hex_to_rgb('212529'),
        'TEXT_SOFT': hex_to_rgb('6C757D'),
        'SLOT_BG': hex_to_rgb('E9ECEF'),
        'ACCENT_BLUE': hex_to_rgb('4A90E2'),
        'ACCENT_SAGE': hex_to_rgb('82AA82'),
        'CORRECT': hex_to_rgb('2ECC71'),
        'WRONG': hex_to_rgb('E74C3C'),
        'LOCKED': hex_to_rgb('95A5A6'),
        'WARNING': hex_to_rgb('F39C12')
    },
    'dark': {
        'BG_MAIN': hex_to_rgb('121212'),
        'TEXT_MAIN': hex_to_rgb('E0E0E0'),
        'TEXT_SOFT': hex_to_rgb('A0A0A0'),
        'SLOT_BG': hex_to_rgb('2C2C2C'),
        'ACCENT_BLUE': hex_to_rgb('3A7CA5'),
        'ACCENT_SAGE': hex_to_rgb('6B8E23'),
        'CORRECT': hex_to_rgb('27AE60'),
        'WRONG': hex_to_rgb('C0392B'),
        'LOCKED': hex_to_rgb('4F4F4F'),
        'WARNING': hex_to_rgb('D35400')
    }
}

CURRENT_THEME = 'light'
T = THEMES[CURRENT_THEME]
Window.clearcolor = T['BG_MAIN']

# --- KONFIGURASI FILE ---
FILE_KAMUS = 'kamus.json'
FILE_GAME = 'game.json'
FILE_PROGRESS = 'progress.json'
FILE_MUSIK = 'bgm.mp3'
FILE_KLIK = 'click.wav' 
FILE_BENAR = 'benar.mp3'
FILE_SALAH = 'salah.mp3'
FILE_NAIK_LEVEL = 'naik_level.wav'

def muat_data(nama_file):
    if os.path.exists(nama_file):
        try:
            with open(nama_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error baca {nama_file}: {e}")
    return {}

# --- WIDGET KUSTOM ---
class ThemeSwitch(ButtonBehavior, Widget):
    knob_x = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (80, 40)
        self.is_dark = (CURRENT_THEME == 'dark')

        with self.canvas:
            self.bg_col = Color(0.12, 0.12, 0.12, 1) 
            self.bg_rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[20])
            self.moon_col = Color(1, 1, 1, 1) 
            self.moon = Ellipse(size=(18, 18))
            self.moon_mask_col = Color(0.12, 0.12, 0.12, 1) 
            self.moon_mask = Ellipse(size=(18, 18))
            self.knob_col = Color(0.95, 0.95, 0.95, 1)
            self.knob = Ellipse(size=(34, 34))

        self.bind(pos=self.update_canvas, size=self.update_canvas, knob_x=self.update_knob)
        Clock.schedule_once(self.set_initial_state, 0)

    def set_initial_state(self, dt):
        knob_size = self.height - 6
        if self.is_dark:
            self.knob_x = self.right - knob_size - 3
        else:
            self.knob_x = self.x + 3
        self.update_canvas()

    def update_canvas(self, *args):
        self.bg_rect.pos = self.pos
        self.bg_rect.size = self.size
        self.bg_rect.radius = [self.height / 2.0]
        moon_x = self.right - 28
        moon_y = self.y + (self.height / 2.0) - 9
        self.moon.pos = (moon_x, moon_y)
        self.moon_mask.pos = (moon_x + 5, moon_y + 3) 
        knob_size = self.height - 6
        self.knob.size = (knob_size, knob_size)
        self.knob.pos = (self.knob_x, self.y + 3)

    def update_knob(self, instance, value):
        self.knob.pos = (value, self.y + 3)

    def on_press(self):
        self.is_dark = not self.is_dark
        knob_size = self.height - 6
        target_x = self.right - knob_size - 3 if self.is_dark else self.x + 3
        anim = Animation(knob_x=target_x, duration=0.25, t='out_quad')
        anim.start(self)

        app = App.get_running_app()
        if app and app.suara_klik:
            app.suara_klik.play()

        if app and app.root:
            menu_screen = app.root.get_screen('menu')
            if menu_screen:
                menu_screen.do_toggle_theme(self.is_dark)

class TombolEstetik(Button):
    def __init__(self, color_key='ACCENT_BLUE', bentuk='pill', **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_disabled_normal = ''
        self.background_color = (0, 0, 0, 0) 
        
        self.color_key = color_key
        self.bentuk = bentuk 
        self.color = (1, 1, 1, 1)
        self.bold = True
        self.font_size = '18sp'

        with self.canvas.before:
            self.bg_color = Color(*T[self.color_key])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        if self.bentuk == 'circle':
            r = min(self.width, self.height) / 2
            self.rect.radius = [r]
        else:
            self.rect.radius = [self.height / 2]

    def set_color_key(self, color_key):
        self.color_key = color_key
        self.bg_color.rgba = T[self.color_key]

    def update_theme(self):
        self.bg_color.rgba = T[self.color_key]

    def on_press(self):
        if not self.disabled:
            current_rgba = T[self.color_key]
            self.bg_color.rgba = (current_rgba[0]*0.8, current_rgba[1]*0.8, current_rgba[2]*0.8, current_rgba[3])
            app = App.get_running_app()
            if app.suara_klik:
                app.suara_klik.play()
        super().on_press()

    def on_release(self):
        if not self.disabled:
            self.bg_color.rgba = T[self.color_key]
        super().on_release()

class SlotBulat(Label):
    def __init__(self, color_key='SLOT_BG', **kwargs):
        super().__init__(**kwargs)
        self.color_key = color_key
        self.color = T['TEXT_MAIN']
        self.bold = True
        self.font_size = '22sp'
        
        with self.canvas.before:
            self.bg_color = Color(*T[self.color_key])
            self.rect = RoundedRectangle(pos=self.pos, size=self.size)
            
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
        r = min(self.width, self.height) / 2
        self.rect.radius = [r]

    def set_color_key(self, color_key):
        self.color_key = color_key
        self.bg_color.rgba = T[self.color_key]
        
    def update_theme(self):
        self.bg_color.rgba = T[self.color_key]
        self.color = T['TEXT_MAIN'] if self.text == "" else (1,1,1,1)

class TemaLabel(Label):
    def __init__(self, color_key='TEXT_MAIN', **kwargs):
        super().__init__(**kwargs)
        self.color_key = color_key
        self.color = T[self.color_key]
        
    def set_color_key(self, color_key):
        self.color_key = color_key
        self.color = T[self.color_key]
        
    def update_theme(self):
        self.color = T[self.color_key]
# --- WIDGET KARTU BELAJAR ---
class KartuBelajar(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical' 
        self.padding = 30
        self.spacing = 15
        with self.canvas.before:
            self.bg_color = Color(1, 1, 1, 0.85) 
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[25])
        self.bind(pos=self.update_canvas, size=self.update_canvas)

    def update_canvas(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size
# --- HALAMAN 1: BELAJAR BAHASA ---
class BelajarScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements_to_update = []

    def on_enter(self):
        self.clear_widgets()
        self.elements_to_update = []
        
        self.add_widget(Image(source='bg.png', fit_mode='fill'))
        
        self.data_kamus = muat_data(FILE_KAMUS)
        self.kategori_aktif = "angka" 
        self.index_kata = 0
        self.siapkan_kata()

        layout_utama = BoxLayout(padding=40)
        kartu = KartuBelajar() 
        
        # --- 1. JUDUL KARTU ---
        lbl_judul_belajar = TemaLabel(text="BELAJAR", color_key='ACCENT_SAGE', bold=True, font_size='36sp', size_hint_y=None, height=60, halign='center', valign='middle')
        lbl_judul_belajar.bind(size=lbl_judul_belajar.setter('text_size'))
        self.elements_to_update.append(lbl_judul_belajar)
        kartu.add_widget(lbl_judul_belajar)
        
        # --- 2. AREA KONTEN TENGAH ---
        konten_kartu = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.7)
        
        # PANEL KIRI: DAFTAR KATEGORI
        panel_kiri = BoxLayout(orientation='vertical', size_hint_x=0.35, spacing=15)
        panel_kiri.add_widget(Label(size_hint_y=0.5)) # Penyeimbang agar kategori agak turun
        
        lbl_kategori = TemaLabel(text="KATEGORI", color_key='TEXT_MAIN', bold=True, font_size='26sp', size_hint_y=None, height=40, halign='center')
        lbl_kategori.bind(size=lbl_kategori.setter('text_size'))
        self.elements_to_update.append(lbl_kategori)
        panel_kiri.add_widget(lbl_kategori)
        
        # Blok tombol kategori
        box_kategori = BoxLayout(orientation='vertical', size_hint_y=None, height=210, spacing=15)
        daftar_kategori = ["angka", "organ_tubuh", "tumbuhan"]
        for kat in daftar_kategori:
            btn_kat = TombolEstetik(text=kat.replace('_', ' ').upper(), color_key='ACCENT_BLUE', size_hint_y=None, height=60)
            btn_kat.bind(on_release=lambda instance, k=kat: self.ganti_kategori(k))
            self.elements_to_update.append(btn_kat)
            box_kategori.add_widget(btn_kat)
        panel_kiri.add_widget(box_kategori)
        panel_kiri.add_widget(Label(size_hint_y=1)) 

        # PANEL KANAN: KONTEN KOSAKATA
        panel_kanan = BoxLayout(orientation='vertical', size_hint_x=0.65, spacing=10)
        panel_kanan.add_widget(Label(size_hint_y=0.3)) # Penyeimbang Atas
        
        box_navigasi = BoxLayout(orientation='horizontal', size_hint_y=None, height=150, spacing=10)
        box_navigasi.add_widget(Label(size_hint_x=0.1))
        
        btn_prev = TombolEstetik(text="<", color_key='ACCENT_BLUE', bentuk='circle', size_hint=(None, None), size=(60, 60), pos_hint={'center_y': 0.5})
        btn_prev.bind(on_release=self.prev_kata)
        self.elements_to_update.append(btn_prev)
        
        self.box_kata = BoxLayout(orientation='vertical', size_hint_x=0.8)
        self.lbl_indo = TemaLabel(text="", color_key='ACCENT_BLUE', bold=True, font_size='26sp', halign='center', valign='middle')
        self.lbl_indo.bind(size=self.lbl_indo.setter('text_size'))
        self.lbl_bintauna = TemaLabel(text="", color_key='TEXT_MAIN', bold=True, font_size='22sp', halign='center', valign='middle')
        self.lbl_bintauna.bind(size=self.lbl_bintauna.setter('text_size'))
        self.elements_to_update.extend([self.lbl_indo, self.lbl_bintauna])
        self.box_kata.add_widget(self.lbl_indo)
        self.box_kata.add_widget(self.lbl_bintauna)
        
        btn_next = TombolEstetik(text=">", color_key='ACCENT_BLUE', bentuk='circle', size_hint=(None, None), size=(60, 60), pos_hint={'center_y': 0.5})
        btn_next.bind(on_release=self.next_kata)
        self.elements_to_update.append(btn_next)
        
        box_navigasi.add_widget(btn_prev)
        box_navigasi.add_widget(self.box_kata)
        box_navigasi.add_widget(btn_next)
        box_navigasi.add_widget(Label(size_hint_x=0.1))
        
        panel_kanan.add_widget(box_navigasi)
        panel_kanan.add_widget(Label(size_hint_y=0.5)) 

        # Masukkan Kiri & Kanan ke area tengah kartu
        konten_kartu.add_widget(panel_kiri)
        konten_kartu.add_widget(panel_kanan)
        kartu.add_widget(konten_kartu)
        
        # --- 3. TOMBOL KEMBALI ---
        btn_kembali = TombolEstetik(text="Kembali", color_key='WRONG', size_hint=(None, None), size=(200, 60), pos_hint={'center_x': 0.5})
        btn_kembali.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        self.elements_to_update.append(btn_kembali)
        kartu.add_widget(btn_kembali)
        
        layout_utama.add_widget(kartu)
        self.add_widget(layout_utama)
        
        self.update_tampilan_kata()

    def siapkan_kata(self):
        if self.kategori_aktif in self.data_kamus:
            self.list_kata = list(self.data_kamus[self.kategori_aktif].items())
        else:
            self.list_kata = []
            
    def ganti_kategori(self, kategori):
        self.kategori_aktif = kategori
        self.index_kata = 0
        self.siapkan_kata()
        self.update_tampilan_kata()
        
    def prev_kata(self, instance):
        if self.list_kata and self.index_kata > 0:
            self.index_kata -= 1
            self.update_tampilan_kata()
            
    def next_kata(self, instance):
        if self.list_kata and self.index_kata < len(self.list_kata) - 1:
            self.index_kata += 1
            self.update_tampilan_kata()
            
    def update_tampilan_kata(self):
        if self.list_kata:
            bintauna, indo = self.list_kata[self.index_kata]
            self.lbl_indo.text = indo.upper()
            self.lbl_bintauna.text = bintauna.upper()
        else:
            self.lbl_indo.text = ""
            self.lbl_bintauna.text = "DATA KOSONG"

    def update_theme(self):
        if hasattr(self, 'elements_to_update'):
            for el in self.elements_to_update:
                el.update_theme()

## --- HALAMAN 2: PILIH LEVEL ---
class PilihLevelScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements_to_update = []

    def on_enter(self):
        self.clear_widgets()
        self.elements_to_update = []
        self.app = App.get_running_app()
        progress = self.app.progress

        # Latar Belakang
        self.add_widget(Image(source='bg.png', fit_mode='fill'))

        # Mengurangi spacing bawaan agar kita bisa mengatur jarak secara manual
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        
        # Pendorong Atas agar keseluruhan menu sedikit turun ke tengah
        layout.add_widget(Label(size_hint_y=0.8))
        
        lbl_judul = TemaLabel(text="Pilih Tingkat Kesulitan", color_key='ACCENT_BLUE', bold=True, font_size='36sp', size_hint_y=None, height=60, halign='center', valign='middle')
        lbl_judul.bind(size=lbl_judul.setter('text_size'))
        self.elements_to_update.append(lbl_judul)
        layout.add_widget(lbl_judul)
        
        # Pendorong Tengah 1: Memberi jarak napas antara Judul dan Tombol EASY
        layout.add_widget(Label(size_hint_y=0.4))
        
        # Tombol EASY
        btn_easy = TombolEstetik(text="EASY (10 Soal)", color_key='CORRECT', size_hint_y=None, height=60, size_hint_x=0.5, pos_hint={'center_x': 0.5})
        btn_easy.bind(on_release=lambda x: self.ke_game('easy'))
        self.elements_to_update.append(btn_easy)
        layout.add_widget(btn_easy)
        
        # Tombol HARD
        btn_hard = TombolEstetik(text="HARD (20 Soal)", size_hint_y=None, height=60, size_hint_x=0.5, pos_hint={'center_x': 0.5})
        if progress.get('hard_unlocked', False):
            btn_hard.set_color_key('WARNING')
            btn_hard.bind(on_release=lambda x: self.ke_game('hard'))
        else:
            btn_hard.set_color_key('LOCKED')
            btn_hard.text = "HARD (Terkunci)"
            btn_hard.disabled = True
        self.elements_to_update.append(btn_hard)
        layout.add_widget(btn_hard)
        
        # Tombol EXPERT
        btn_expert = TombolEstetik(text="EXPERT (30 Soal)", size_hint_y=None, height=60, size_hint_x=0.5, pos_hint={'center_x': 0.5})
        if progress.get('expert_unlocked', False):
            btn_expert.set_color_key('WRONG')
            btn_expert.bind(on_release=lambda x: self.ke_game('expert'))
        else:
            btn_expert.set_color_key('LOCKED')
            btn_expert.text = "EXPERT (Terkunci)"
            btn_expert.disabled = True
        self.elements_to_update.append(btn_expert)
        layout.add_widget(btn_expert)
        
        # Pendorong Tengah 2: Memberi jarak lebih jauh antara pilihan level dan tombol kembali
        layout.add_widget(Label(size_hint_y=0.5))
        
        # Tombol KEMBALI
        btn_kembali = TombolEstetik(text="Kembali", color_key='WRONG', size_hint_y=None, height=60, size_hint_x=0.5, pos_hint={'center_x': 0.5})
        btn_kembali.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        self.elements_to_update.append(btn_kembali)
        layout.add_widget(btn_kembali)
        
        # Pendorong Bawah
        layout.add_widget(Label(size_hint_y=0.8))
        
        self.add_widget(layout)

    def ke_game(self, level):
        game_screen = self.manager.get_screen('game_play')
        game_screen.set_level(level)
        self.manager.current = 'game_play'

    def update_theme(self):
        if hasattr(self, 'elements_to_update'):
            for el in self.elements_to_update:
                el.update_theme()

# --- HALAMAN 3: GAME PLAY ---
class GamePlayScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.level_aktif = None
        self.event_waktu = None
        self.elements_to_update = []

    def set_level(self, level):
        self.level_aktif = level

    def on_enter(self):
        self.clear_widgets()
        self.elements_to_update = []
        self.add_widget(Image(source='bg.png', fit_mode='fill'))
        
        self.data_game = muat_data(FILE_GAME) 
        self.app = App.get_running_app()
        
        if not self.data_game:
            lbl = TemaLabel(text="File game.json tidak ditemukan!", color_key='WRONG')
            self.add_widget(lbl)
            self.elements_to_update.append(lbl)
            return

        level_data = self.data_game.get(self.level_aktif, {})
        self.waktu_awal = level_data.get('waktu', 0)
        target_jumlah_soal = level_data.get('jumlah_soal', 10)
        kosakata_dict = level_data.get('kosakata', {})
        
        semua_soal = list(kosakata_dict.items())
        random.shuffle(semua_soal)
        self.daftar_soal = semua_soal[:target_jumlah_soal]
        
        self.skor = 0
        self.indeks_soal = 0
        self.total_soal = len(self.daftar_soal)
        
        self.setup_ui_game()
        self.load_soal()

    def setup_ui_game(self):
        self.layout_utama = BoxLayout(orientation='vertical', padding=20, spacing=15)
        
        box_header = BoxLayout(orientation='horizontal', size_hint_y=0.1)
        self.lbl_tingkat = TemaLabel(text=f"{self.level_aktif.upper()} ({self.indeks_soal+1}/{self.total_soal})", color_key='ACCENT_SAGE', bold=True, font_size='22sp')
        self.lbl_timer = TemaLabel(text="", color_key='WRONG', bold=True, font_size='24sp')
        box_header.add_widget(self.lbl_tingkat)
        box_header.add_widget(self.lbl_timer)
        self.elements_to_update.extend([self.lbl_tingkat, self.lbl_timer])
        self.layout_utama.add_widget(box_header)
        
        self.lbl_petunjuk = TemaLabel(text="Apa bahasa Bintauna dari:", color_key='TEXT_MAIN', font_size='18sp', size_hint_y=0.1)
        self.lbl_arti = TemaLabel(text="", color_key='ACCENT_BLUE', bold=True, font_size='28sp', size_hint_y=0.2)
        self.elements_to_update.extend([self.lbl_petunjuk, self.lbl_arti])
        self.layout_utama.add_widget(self.lbl_petunjuk)
        self.layout_utama.add_widget(self.lbl_arti)

        self.box_slot = BoxLayout(orientation='horizontal', spacing=10, size_hint_y=0.15)
        self.layout_utama.add_widget(self.box_slot)
        
        self.lbl_feedback = TemaLabel(text="", color_key='TEXT_MAIN', bold=True, font_size='20sp', size_hint_y=0.1)
        self.elements_to_update.append(self.lbl_feedback)
        self.layout_utama.add_widget(self.lbl_feedback)

        self.grid_huruf = GridLayout(cols=6, spacing=10, size_hint_y=0.25)
        self.layout_utama.add_widget(self.grid_huruf)
        
        box_aksi = BoxLayout(orientation='horizontal', spacing=20, size_hint_y=0.1, size_hint_x=0.8, pos_hint={'center_x': 0.5})
        btn_hapus = TombolEstetik(text="Hapus", color_key='WRONG')
        btn_hapus.bind(on_release=self.hapus_huruf)
        
        btn_keluar = TombolEstetik(text="Berhenti", color_key='TEXT_MAIN')
        btn_keluar.bind(on_release=self.kembali_ke_pilih_level)
        
        self.elements_to_update.extend([btn_hapus, btn_keluar])
        box_aksi.add_widget(btn_hapus)
        box_aksi.add_widget(btn_keluar)
        
        self.layout_utama.add_widget(box_aksi)
        self.add_widget(self.layout_utama)

    def load_soal(self):
        if self.event_waktu:
            self.event_waktu.cancel()
            
        if self.indeks_soal < self.total_soal:
            self.lbl_tingkat.text = f"{self.level_aktif.upper()} ({self.indeks_soal+1}/{self.total_soal})"
            self.lbl_feedback.text = ""
            self.jawaban_user = []
            
            kata_bintauna, arti_indo = self.daftar_soal[self.indeks_soal]
            self.kata_target = kata_bintauna.upper()
            self.panjang_kata = len(self.kata_target)
            self.lbl_arti.text = f"\"{arti_indo.upper()}\""
            
            self.waktu_sekarang = self.waktu_awal
            if self.waktu_awal > 0:
                self.lbl_timer.text = f"{self.waktu_sekarang}s"
                self.event_waktu = Clock.schedule_interval(self.update_timer, 1)
            else:
                self.lbl_timer.text = "Tanpa Waktu"

            self.box_slot.clear_widgets()
            self.slots = []
            for char in self.kata_target:
                if char in [" ", "'", "’", "-"]:
                    spacer = TemaLabel(text=char, color_key='TEXT_MAIN', bold=True, font_size='24sp', size_hint_x=0.2)
                    self.elements_to_update.append(spacer)
                    self.box_slot.add_widget(spacer)
                else:
                    slot_bulat = SlotBulat(color_key='SLOT_BG')
                    slot_bulat.text = ""
                    self.slots.append(slot_bulat)
                    self.elements_to_update.append(slot_bulat)
                    self.box_slot.add_widget(slot_bulat)
                    
            huruf_murni = [char for char in self.kata_target if char not in [" ", "'", "’", "-"]]
            abjad = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            jml_pengecoh = 4 if self.level_aktif == 'expert' else 3
            for _ in range(jml_pengecoh): 
                huruf_murni.append(random.choice(abjad))
            
            random.shuffle(huruf_murni)
            self.grid_huruf.clear_widgets()
            for huruf in huruf_murni:
                btn_huruf = TombolEstetik(text=huruf, color_key='ACCENT_BLUE', bentuk='circle')
                btn_huruf.bind(on_release=self.klik_huruf)
                self.elements_to_update.append(btn_huruf)
                self.grid_huruf.add_widget(btn_huruf)
        else:
            self.tampilkan_tamat()

    def update_timer(self, dt):
        self.waktu_sekarang -= 1
        self.lbl_timer.text = f"{self.waktu_sekarang}s"
        if self.waktu_sekarang <= 0:
            self.event_waktu.cancel()
            self.waktu_habis()

    def waktu_habis(self):
        self.lbl_feedback.text = "WAKTU HABIS!"
        self.lbl_feedback.set_color_key('WRONG')
        self.lbl_feedback.update_theme()
        for btn in self.grid_huruf.children:
            btn.disabled = True
        self.indeks_soal += 1
        Clock.schedule_once(lambda dt: self.load_soal(), 2.0)

    def klik_huruf(self, instance):
        slot_tersedia = [s for s in self.slots if s.text == ""]
        if len(slot_tersedia) > 0:
            huruf = instance.text
            self.jawaban_user.append((huruf, instance)) 
            instance.disabled = True
            instance.set_color_key('SLOT_BG')
            self.update_slots()
            
            if len([s for s in self.slots if s.text == ""]) == 0:
                self.cek_jawaban()

    def hapus_huruf(self, instance):
        if len(self.jawaban_user) > 0:
            huruf_dihapus, tombol_asli = self.jawaban_user.pop()
            self.update_slots()
            self.lbl_feedback.text = ""
            tombol_asli.disabled = False
            tombol_asli.set_color_key('ACCENT_BLUE')

    def update_slots(self):
        idx_jawaban = 0
        for slot in self.slots:
            if idx_jawaban < len(self.jawaban_user):
                slot.text = self.jawaban_user[idx_jawaban][0]
                slot.set_color_key('ACCENT_BLUE')
                slot.color = (1,1,1,1)
                idx_jawaban += 1
            else:
                slot.text = ""
                slot.set_color_key('SLOT_BG')
                slot.color = T['TEXT_MAIN']

    def cek_jawaban(self):
        tebakan = "".join([h[0] for h in self.jawaban_user])
        jawaban_murni = "".join([char for char in self.kata_target if char not in [" ", "'", "’", "-"]])
        
        if tebakan == jawaban_murni:
            if self.event_waktu: self.event_waktu.cancel()
            self.skor += 10
            if self.app.suara_benar:
                self.app.suara_benar.play()
            
            # Panggil Popup Benar
            self.tampilkan_popup_jawaban("BENAR!", "Jawaban Anda Benar!", 'CORRECT', True)
        else:
            if self.app.suara_salah:
                self.app.suara_salah.play()
            
            # Panggil Popup Salah
            self.tampilkan_popup_jawaban("SALAH!", "Upss! Jawaban kamu salah", 'WRONG', False)

    def tampilkan_popup_jawaban(self, judul, pesan, warna_key, is_correct):
        content = BoxLayout(orientation='vertical', padding=20)
        lbl = Label(text=pesan, font_size='28sp', bold=True, color=T[warna_key])
        content.add_widget(lbl)
        
        self.popup_jwb = Popup(title=judul, content=content, size_hint=(0.8, 0.4), auto_dismiss=False)
        self.popup_jwb.open()
        
        # Otomatis tutup popup setelah 1.5 detik dan lanjut
        Clock.schedule_once(lambda dt: self.lanjut_setelah_popup(is_correct), 1.5)

    def lanjut_setelah_popup(self, is_correct):
        self.popup_jwb.dismiss()
        if is_correct:
            self.indeks_soal += 1
            self.load_soal()
        else:
            # Reset jika salah agar user bisa mencoba lagi
            for btn in self.jawaban_user:
                btn[1].disabled = False
                btn[1].set_color_key('ACCENT_BLUE')
            self.jawaban_user.clear()
            self.update_slots()

    def tampilkan_tamat(self):
        if self.event_waktu: self.event_waktu.cancel()
        self.clear_widgets()
        self.elements_to_update = []
        self.add_widget(Image(source='bg.png', fit_mode='fill'))
        
        # --- JURUS PALING AMAN MEMANGGIL SUARA & DETEKTIF ---
        app = App.get_running_app()
        
        print("\n--- DETEKTIF AUDIO ---")
        print("Mencoba memutar suara naik level...")
        print("Status File:", app.suara_naik_level)
        
        if app.suara_naik_level:
            app.suara_naik_level.play()
            print("Laporan: Perintah PLAY berhasil dieksekusi!")
        else:
            print("Laporan GAGAL: File audio tidak terbaca oleh Kivy!")
        print("----------------------\n")
        # ----------------------------------------------------
        
        if self.level_aktif == 'easy':
            app.progress['hard_unlocked'] = True
            app.simpan_progress()
        elif self.level_aktif == 'hard':
            app.progress['expert_unlocked'] = True
            app.simpan_progress()

        layout = BoxLayout(orientation='vertical', padding=20, spacing=20)
        
        lbl_selesai = TemaLabel(text="Level Selesai!", color_key='TEXT_MAIN', bold=True, font_size='36sp', halign='center')
        lbl_info = TemaLabel(text=f"Skor Anda:\n{self.skor} / {self.total_soal * 10}", color_key='ACCENT_SAGE', bold=True, font_size='34sp', halign='center')
        
        btn_menu = TombolEstetik(text="Pilih Level Lain", color_key='ACCENT_BLUE', size_hint_y=0.2, size_hint_x=0.7, pos_hint={'center_x': 0.5})
        btn_menu.bind(on_release=self.kembali_ke_pilih_level)

        self.elements_to_update.extend([lbl_selesai, lbl_info, btn_menu])
        
        layout.add_widget(lbl_selesai)
        layout.add_widget(lbl_info)
        layout.add_widget(btn_menu)
        self.add_widget(layout)

    def kembali_ke_pilih_level(self, instance):
        if self.event_waktu: self.event_waktu.cancel()
        self.manager.current = 'pilih_level'

    def update_theme(self):
        if hasattr(self, 'elements_to_update'):
            for el in self.elements_to_update:
                el.update_theme()


# --- HALAMAN 4: PENGATURAN KESELURUHAN ---
class PengaturanScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements_to_update = []

    def on_enter(self):
        self.clear_widgets()
        self.elements_to_update = []
        self.app = App.get_running_app()
        self.add_widget(Image(source='bg.png', fit_mode='fill'))
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=15)
        
        # Pendorong Atas
        layout.add_widget(Label(size_hint_y=0.5))
        
        lbl_judul = TemaLabel(text="Pengaturan", color_key='ACCENT_BLUE', bold=True, font_size='36sp', size_hint_y=None, height=60, halign='center', valign='middle')
        lbl_judul.bind(size=lbl_judul.setter('text_size'))
        self.elements_to_update.append(lbl_judul)
        layout.add_widget(lbl_judul)

        # Spasi sedikit di bawah judul
        layout.add_widget(Label(size_hint_y=0.1))

        # Tombol Musik (Lebar 60% layar)
        self.btn_musik = TombolEstetik(text="", size_hint_y=None, height=60, size_hint_x=0.6, pos_hint={'center_x': 0.5})
        self.update_tombol_musik()
        self.btn_musik.bind(on_release=self.toggle_musik)
        self.elements_to_update.append(self.btn_musik)
        layout.add_widget(self.btn_musik)

        # Bungkus Label Volume dan Slider ke dalam satu kontainer khusus
        box_vol = BoxLayout(orientation='vertical', size_hint_y=None, height=80, size_hint_x=0.6, pos_hint={'center_x': 0.5})
        self.lbl_vol = TemaLabel(text=f"Volume BGM: {int(self.app.volume_level * 100)}%", color_key='TEXT_MAIN', font_size='20sp', size_hint_y=0.5, halign='center', valign='bottom')
        self.lbl_vol.bind(size=self.lbl_vol.setter('text_size'))
        self.elements_to_update.append(self.lbl_vol)
        box_vol.add_widget(self.lbl_vol)

        slider = Slider(min=0, max=1, value=self.app.volume_level, size_hint_y=0.5)
        slider.bind(value=self.ubah_volume)
        box_vol.add_widget(slider)
        
        layout.add_widget(box_vol)

        # Spasi sedikit sebelum tombol Tentang Kami
        layout.add_widget(Label(size_hint_y=0.1))

        btn_tentang = TombolEstetik(text="Tentang Kami", color_key='ACCENT_SAGE', size_hint_y=None, height=60, size_hint_x=0.6, pos_hint={'center_x': 0.5})
        btn_tentang.bind(on_release=self.tampilkan_tentang)
        self.elements_to_update.append(btn_tentang)
        layout.add_widget(btn_tentang)

        btn_keluar = TombolEstetik(text="Keluar Aplikasi", color_key='WRONG', size_hint_y=None, height=60, size_hint_x=0.6, pos_hint={'center_x': 0.5})
        btn_keluar.bind(on_release=lambda x: App.get_running_app().stop())
        self.elements_to_update.append(btn_keluar)
        layout.add_widget(btn_keluar)

        # Pendorong Tengah (Jarak pemisah ke tombol Kembali)
        layout.add_widget(Label(size_hint_y=0.4))

        # Tombol Kembali (Sedikit lebih pendek, lebar 50% layar)
        btn_kembali = TombolEstetik(text="Kembali", color_key='TEXT_MAIN', size_hint_y=None, height=60, size_hint_x=0.5, pos_hint={'center_x': 0.5})
        btn_kembali.bind(on_release=lambda x: setattr(self.manager, 'current', 'menu'))
        self.elements_to_update.append(btn_kembali)
        layout.add_widget(btn_kembali)
        
        # Pendorong Bawah
        layout.add_widget(Label(size_hint_y=0.5))
        
        self.add_widget(layout)

    def tampilkan_tentang(self, instance):
        content = BoxLayout(orientation='vertical', padding=10, spacing=15)
        teks_panjang = (
            "Game ini dibuat oleh Mahasiswa Fakultas Ilmu Komputer\n\n"
            "Developer:\n"
            "Fatur Rahman Djangko\n"
            "T3122115\n\n"
            "Game ini disusun untuk memenuhi salah satu syarat "
            "dalam menyelesaikan tugas akhir (Skripsi) pada "
            "program studi Teknik Informatika di Universitas Ichsan Gorontalo.\n\n"
        )
        
        # Membuat area Scroll (Bisa digulir)
        scroll = ScrollView(size_hint=(1, 1))
        
        # Membuat Label khusus yang tingginya otomatis menyesuaikan panjang teks
        lbl_info = Label(text=teks_panjang, halign='center', valign='top', font_size='20sp', size_hint_y=None)
        lbl_info.bind(width=lambda *x: lbl_info.setter('text_size')(lbl_info, (lbl_info.width, None)))
        lbl_info.bind(texture_size=lbl_info.setter('size'))
        
        # Memasukkan Label ke dalam Scroll, lalu Scroll ke dalam Pop-up
        scroll.add_widget(lbl_info)
        content.add_widget(scroll)
        
        # Mengubah tombol Tutup menjadi lebih cantik menggunakan TombolEstetik
        btn_tutup = TombolEstetik(text="Tutup", color_key='WRONG', size_hint_y=None, height=50)
        
        pop = Popup(title="Tentang Kami", content=content, size_hint=(0.85, 0.65))
        btn_tutup.bind(on_release=pop.dismiss)
        content.add_widget(btn_tutup)
        
        pop.open()

    def update_tombol_musik(self):
        if self.app.musik_menyala:
            self.btn_musik.text = "Audio: ON (Klik untuk mematikan)"
            self.btn_musik.set_color_key('ACCENT_BLUE')
        else:
            self.btn_musik.text = "Audio: OFF (Klik untuk menyalakan)"
            self.btn_musik.set_color_key('TEXT_SOFT')

    def toggle_musik(self, instance):
        self.app.musik_menyala = not self.app.musik_menyala
        if self.app.musik_menyala and self.app.bgm:
            self.app.bgm.play()
        elif self.app.bgm:
            self.app.bgm.stop()
        self.update_tombol_musik()

    def ubah_volume(self, instance, value):
        self.app.volume_level = value
        self.lbl_vol.text = f"Volume BGM: {int(value * 100)}%"
        if self.app.bgm: self.app.bgm.volume = value
        if self.app.suara_klik: self.app.suara_klik.volume = value
        
    def update_theme(self):
        if hasattr(self, 'elements_to_update'):
            for el in self.elements_to_update:
                el.update_theme()


# --- WIDGET TOMBOL ICON (Tambahan) ---
class TombolIcon(ButtonBehavior, Image):
    def on_press(self):
        app = App.get_running_app()
        if app.suara_klik:
            app.suara_klik.play()
        super().on_press()


# --- MENU UTAMA ---
class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.elements_to_update = []

    def on_enter(self):
        self.clear_widgets()
        self.elements_to_update = []
        
        # Latar Belakang
        self.add_widget(Image(source='bg.png', fit_mode='fill'))
        
        layout = BoxLayout(orientation='vertical', padding=40, spacing=20)

        # BAGIAN ATAS: Icon Pengaturan di Kiri (Mode Gelap Dihapus)
        box_top = BoxLayout(orientation='horizontal', size_hint_y=0.15)
        
        # Menggunakan gambar gear.png yang Anda siapkan
        btn_atur = TombolIcon(source='gear.png', size_hint=(None, None), size=(50, 50), pos_hint={'center_y': 0.5})
        btn_atur.bind(on_release=lambda x: setattr(self.manager, 'current', 'pengaturan'))
        
        box_top.add_widget(btn_atur)
        box_top.add_widget(Label(size_hint_x=0.8)) # Memberi ruang agar ikon tetap di ujung kiri
        
        layout.add_widget(box_top)

        # JUDUL APLIKASI
        lbl_judul = TemaLabel(text="Belajar Bahasa Daerah", color_key='ACCENT_BLUE', bold=True, font_size='45sp', size_hint_y=0.3)
        lbl_sub = TemaLabel(text="Game edukasi", color_key='TEXT_MAIN', font_size='18sp', size_hint_y=0.1)
        self.elements_to_update.extend([lbl_judul, lbl_sub])
        layout.add_widget(lbl_judul)
        layout.add_widget(lbl_sub)

        # TOMBOL MENU UTAMA (Tanpa Nomor)
        btn_belajar = TombolEstetik(text="Belajar Bahasa", color_key='ACCENT_BLUE', size_hint_y=0.2, size_hint_x=0.7, pos_hint={'center_x': 0.5})
        btn_belajar.bind(on_release=lambda x: setattr(self.manager, 'current', 'belajar'))
        
        btn_main = TombolEstetik(text="Mulai Bermain", color_key='ACCENT_SAGE', size_hint_y=0.2, size_hint_x=0.7, pos_hint={'center_x': 0.5})
        btn_main.bind(on_release=lambda x: setattr(self.manager, 'current', 'pilih_level'))
        
        self.elements_to_update.extend([btn_belajar, btn_main])
        layout.add_widget(btn_belajar)
        layout.add_widget(btn_main)
        
        # Penyeimbang spasi di bawah agar tombol tidak terlalu panjang ke bawah
        layout.add_widget(Label(size_hint_y=0.2))

        self.add_widget(layout)

    def update_theme(self):
        if hasattr(self, 'elements_to_update'):
            for el in self.elements_to_update:
                el.update_theme()


# --- APLIKASI UTAMA ---
# --- APLIKASI UTAMA ---
class BintaunaApp(App):
    def build(self):
        self.musik_menyala = True
        self.volume_level = 0.5
        
        self.muat_progress()
        
        self.bgm = SoundLoader.load(FILE_MUSIK)
        self.suara_klik = SoundLoader.load(FILE_KLIK)
        self.suara_benar = SoundLoader.load(FILE_BENAR)
        self.suara_salah = SoundLoader.load(FILE_SALAH)
        self.suara_naik_level = SoundLoader.load(FILE_NAIK_LEVEL) # <-- Tambahkan ini

        if self.bgm:
            self.bgm.volume = self.volume_level
            self.bgm.loop = True
            if self.musik_menyala:
                self.bgm.play()
                
        if self.suara_klik: self.suara_klik.volume = self.volume_level
        if self.suara_benar: self.suara_benar.volume = self.volume_level
        if self.suara_salah: self.suara_salah.volume = self.volume_level
        if self.suara_naik_level: self.suara_naik_level.volume = self.volume_level # <-- Tambahkan ini

        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(BelajarScreen(name='belajar'))
        sm.add_widget(PilihLevelScreen(name='pilih_level'))
        sm.add_widget(GamePlayScreen(name='game_play'))
        sm.add_widget(PengaturanScreen(name='pengaturan'))
        
        return sm
        
    def muat_progress(self):
        if os.path.exists(FILE_PROGRESS):
            try:
                with open(FILE_PROGRESS, 'r') as f:
                    self.progress = json.load(f)
            except:
                self.progress = {'hard_unlocked': False, 'expert_unlocked': False}
        else:
            self.progress = {'hard_unlocked': False, 'expert_unlocked': False}
            
    def simpan_progress(self):
        with open(FILE_PROGRESS, 'w') as f:
            json.dump(self.progress, f)

if __name__ == '__main__':
    BintaunaApp().run()