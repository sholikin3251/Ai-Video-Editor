from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

# --- FUNGSI BANTUAN CROP (Safe Mode) ---
def make_vertical_safe(clip):
    try:
        w, h = clip.size
        # Jika sudah potrait (Tinggi > Lebar), jangan diapa-apain
        if h > w:
            return clip
            
        # Hitung target lebar untuk rasio 9:16
        new_width = h * (9/16)
        
        # Pengaman: Kalau hasil hitungan aneh, pakai lebar asli
        if new_width > w:
            new_width = w
            
        # Titik potong X (tengah)
        center_x = w / 2
        x1 = center_x - (new_width / 2)
        
        # Lakukan Crop
        return clip.crop(x1=x1, y1=0, width=new_width, height=h)
    except Exception as e:
        print(f"   ⚠️ Gagal Crop Potrait: {e}. Menggunakan klip asli.")
        return clip

def proses_video_otomatis(input_path, output_path, data_json):
    print(f"✂️  Mulai memproses video: {input_path}")
    
    video_asli = None
    try:
        video_asli = VideoFileClip(input_path)
    except Exception as e:
        print(f"❌ Error Fatal: Tidak bisa baca video. {e}")
        return None

    clips = []
    segmen_list = data_json.get('segments', [])

    # Jika AI diam saja, kita paksa ambil 5 detik pertama (Hook manual)
    if not segmen_list:
        print("⚠️ AI tidak response. Membuat 'Auto-Hook' 5 detik pertama.")
        segmen_list = [{"start": 0, "end": 5, "description": "Auto-Hook"}]

    for segmen in segmen_list:
        try:
            start = float(segmen.get('start', 0))
            end = float(segmen.get('end', 0))
            
            # Validasi Waktu
            if start >= end: continue
            if end > video_asli.duration: end = video_asli.duration
            
            # 1. Potong
            potongan = video_asli.subclip(start, end)
            
            # 2. Coba ubah jadi Potrait (9:16)
            potongan_final = make_vertical_safe(potongan)
            
            clips.append(potongan_final)
            print(f"   -> Oke: {start:.1f}s - {end:.1f}s")
            
        except Exception as e:
            print(f"   ⚠️ Skip segmen error: {e}")

    # GABUNGKAN
    if len(clips) > 0:
        print(f"🔨 Menyambungkan {len(clips)} klip...")
        try:
            # Method="compose" lebih aman untuk ukuran beda-beda
            video_final = concatenate_videoclips(clips, method="compose")
            
            video_final.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='ultrafast' # Biar render cepat
            )
            video_asli.close()
            print(f"✅ SUKSES! Video ada di: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Gagal Render Akhir: {e}")
            video_asli.close()
            return input_path # Balikin file asli kalau render gagal
    else:
        print("⚠️ Tidak ada klip. Balikin file asli.")
        video_asli.close()
        return input_path