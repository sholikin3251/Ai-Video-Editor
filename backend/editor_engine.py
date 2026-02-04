from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

# --- FUNGSI BANTUAN CROP (Safe Mode) ---
def make_vertical_safe(clip):
    try:
        w, h = clip.size
        if h > w: return clip # Sudah potrait
        
        # Hitung lebar 9:16
        new_width = h * (9/16)
        if new_width > w: new_width = w
            
        center_x = w / 2
        x1 = center_x - (new_width / 2)
        
        return clip.crop(x1=x1, y1=0, width=new_width, height=h)
    except Exception as e:
        print(f"   ⚠️ Gagal Crop: {e}. Pakai asli.")
        return clip

def proses_video_otomatis(input_path, output_path, data_json):
    print(f"✂️  Mulai memproses: {input_path}")
    
    video_asli = None
    try:
        video_asli = VideoFileClip(input_path)
    except Exception as e:
        print(f"❌ Error Buka Video: {e}")
        return None

    clips = []
    segmen_list = data_json.get('segments', [])

    # Auto-Hook jika AI diam
    if not segmen_list:
        print("⚠️ AI diam. Auto-Hook 5 detik.")
        segmen_list = [{"start": 0, "end": 5, "description": "Auto-Hook"}]

    for segmen in segmen_list:
        try:
            start = float(segmen.get('start', 0))
            end = float(segmen.get('end', 0))
            
            if start >= end: continue
            if end > video_asli.duration: end = video_asli.duration
            
            # Potong & Crop
            potongan = video_asli.subclip(start, end)
            potongan_final = make_vertical_safe(potongan)
            
            clips.append(potongan_final)
            print(f"   -> Oke: {start:.1f} - {end:.1f}")
            
        except Exception:
            pass # Skip error kecil

    # GABUNGKAN
    if len(clips) > 0:
        print(f"🔨 Menyambungkan {len(clips)} klip...")
        try:
            final = concatenate_videoclips(clips, method="compose")
            
            # --- BAGIAN PENTING: SETTING RENDER AMAN ---
            final.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                threads=1,       # <--- WAJIB 1 AGAR TIDAK KORUP DI WINDOWS
                preset='medium', # Jangan ultrafast, biar header file rapi
                verbose=False,
                logger=None      # Biar terminal bersih
            )
            # -------------------------------------------
            
            video_asli.close()
            final.close() # Pastikan ditutup
            print(f"✅ SUKSES! File aman di: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Gagal Render: {e}")
            video_asli.close()
            return input_path 
    else:
        video_asli.close()
        return input_path