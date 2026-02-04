from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

def proses_video_otomatis(input_path, output_path, data_json):
    """
    Versi Anti-Gagal: Jika gagal edit, kembalikan video asli.
    """
    print(f"✂️  Mulai memproses video: {input_path}")
    
    video_asli = None
    try:
        video_asli = VideoFileClip(input_path)
    except Exception as e:
        print(f"❌ Kritis: Tidak bisa membuka video asli. {e}")
        return None

    clips = []
    
    # Ambil segmen dari JSON
    segmen_list = data_json.get('segments', [])
    
    # Jika AI tidak memberi segmen, atau list kosong
    if not segmen_list:
        print("⚠️ AI tidak memberikan instruksi potong. Mengembalikan video asli.")
        video_asli.close()
        return input_path # <--- FAIL SAFE 1

    for segmen in segmen_list:
        try:
            start = float(segmen.get('start', 0))
            end = float(segmen.get('end', 0))
            
            # Validasi durasi
            if start >= end: continue
            if end > video_asli.duration: end = video_asli.duration
            
            # Potong tanpa filter durasi minimal (biar pasti ada hasil)
            potongan = video_asli.subclip(start, end)
            clips.append(potongan)
            print(f"   -> Oke: {start:.2f} - {end:.2f}")
            
        except Exception as e:
            print(f"   ⚠️ Gagal potong segmen ini: {e}")

    # GABUNGKAN
    if len(clips) > 0:
        print(f"🔨 Menyambungkan {len(clips)} potongan...")
        try:
            video_final = concatenate_videoclips(clips)
            video_final.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                temp_audiofile='temp-audio.m4a',
                remove_temp=True,
                verbose=False,
                logger=None # Supaya terminal tidak penuh spam
            )
            video_asli.close()
            print(f"✅ Sukses! Video baru di: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Gagal Render: {e}")
            video_asli.close()
            return input_path # <--- FAIL SAFE 2 (Kembalikan asli jika render gagal)
    else:
        print("⚠️ Tidak ada potongan valid. Mengembalikan video asli.")
        video_asli.close()
        return input_path # <--- FAIL SAFE 3