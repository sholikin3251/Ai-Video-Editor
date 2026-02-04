from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

def proses_video_otomatis(input_path, output_path, data_json):
    """
    Fungsi ini memotong video berdasarkan instruksi JSON dari AI.
    """
    print(f"✂️  Mulai memproses video: {input_path}")
    
    # 1. Load Video Asli
    try:
        # Kita gunakan context manager agar file otomatis tertutup setelah dipakai
        video_asli = VideoFileClip(input_path)
    except OSError:
        print("❌ Error: File video tidak ditemukan atau rusak.")
        return

    clips = []
    
   # 2. Loop setiap segmen dari JSON
    for segmen in data_json['segments']:
        start = segmen['start']
        end = segmen['end']
        deskripsi = segmen.get('description', '-')
        
        # --- TAMBAHKAN FILTER INI ---
        durasi = end - start
        if durasi < 2.0: 
            print(f"   ⚠️ SKIP: Potongan terlalu pendek ({durasi:.2f} detik) - {deskripsi}")
            continue
        # ----------------------------

        # Validasi durasi (cegah error jika start > end)
        if start >= end:
            continue
            
        print(f"   -> Memotong detik {start} s.d {end} ({deskripsi})")
        
        # Potong (Subclip)
        potongan = video_asli.subclip(start, end)
        clips.append(potongan)

    # 3. Gabungkan Semua Potongan
    if len(clips) > 0:
        print("🔨 Menyambungkan potongan...")
        video_final = concatenate_videoclips(clips)
        
        # 4. Simpan ke File Baru (Render)
        # fps=24 biar standar sinematik/tiktok, codec libx264 biar ringan
        video_final.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac',
            temp_audiofile='temp-audio.m4a',
            remove_temp=True
        )
        
        # Tutup file asli untuk melepas memori
        video_asli.close()
        print(f"✅ Video Selesai! Disimpan di: {output_path}")
        return output_path
    else:
        print("⚠️ AI tidak menemukan momen menarik untuk dipotong.")
        video_asli.close()
        return None