from moviepy.editor import VideoFileClip, concatenate_videoclips, vfx
import os

def proses_video_otomatis(input_path, output_path, data_json):
    print(f"✂️  Mulai memproses video (Mode Viral): {input_path}")
    
    try:
        video_asli = VideoFileClip(input_path)
    except Exception as e:
        print(f"❌ Kritis: Tidak bisa membuka video asli. {e}")
        return None

    clips = []
    segmen_list = data_json.get('segments', [])
    
    if not segmen_list:
        print("⚠️ AI tidak memberikan instruksi. Return asli.")
        video_asli.close()
        return input_path

    # --- LOGIKA AUTO-CROP 9:16 (TIKTOK STYLE) ---
    def make_vertical(clip):
        # Cek apakah video sudah vertical?
        w, h = clip.size
        if h > w:
            return clip # Sudah vertical, biarkan
        
        # Jika landscape, kita potong tengahnya
        new_width = h * (9/16) # Hitung lebar ideal untuk rasio 9:16
        
        # Pastikan tidak error kalau videonya terlalu 'gepeng'
        if new_width > w:
            new_width = w 

        # Lakukan Crop Center
        return clip.crop(x1=(w/2 - new_width/2), y1=0, width=new_width, height=h)

    for segmen in segmen_list:
        try:
            start = float(segmen.get('start', 0))
            end = float(segmen.get('end', 0))
            
            if start >= end: continue
            if end > video_asli.duration: end = video_asli.duration
            
            # 1. Potong Sesuai Waktu
            potongan = video_asli.subclip(start, end)
            
            # 2. Ubah Jadi Vertical (Potrait)
            potongan_vertical = make_vertical(potongan)
            
            # 3. Resize ke HD (1080x1920) biar tajam di HP (Opsional, tapi bagus)
            # potongan_final = potongan_vertical.resize(height=1920) 
            # (Kita skip resize dulu biar render cepat)
            
            clips.append(potongan_vertical)
            
        except Exception as e:
            print(f"   ⚠️ Gagal segmen: {e}")

    # GABUNGKAN
    if len(clips) > 0:
        print(f"🔨 Menyambungkan {len(clips)} klip viral...")
        try:
            video_final = concatenate_videoclips(clips)
            
            # Render dengan preset 'ultrafast' biar nunggunya gak lama
            video_final.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                preset='ultrafast',
                threads=4
            )
            video_asli.close()
            return output_path
        except Exception as e:
            print(f"❌ Gagal Render: {e}")
            video_asli.close()
            return input_path
    else:
        video_asli.close()
        return input_path