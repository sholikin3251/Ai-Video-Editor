from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

from moviepy.editor import VideoFileClip, concatenate_videoclips
import os

def proses_video_otomatis(input_path, output_path, data_json):
    """
    Fungsi ini memotong video dengan pengaman (Safety Nets).
    """
    print(f"✂️  Mulai memproses video: {input_path}")
    
    try:
        video_asli = VideoFileClip(input_path)
    except OSError:
        print("❌ Error: File video tidak bisa dibaca.")
        return None

    clips = []
    
    # 2. Loop setiap segmen dari JSON
    for segmen in data_json.get('segments', []): # Pakai .get biar gak error kalau JSON kosong
        start = segmen['start']
        end = segmen['end']
        deskripsi = segmen.get('description', '-')
        
        # Validasi dasar
        if start >= end:
            continue
            
        durasi = end - start
        
        # --- FILTER YANG LEBIH LEMBUT ---
        # Kita turunkan jadi 0.5 detik biar gak terlalu galak
        if durasi < 0.5: 
            print(f"   ⚠️ SKIP: Terlalu pendek ({durasi:.2f}s) - {deskripsi}")
            continue
        # --------------------------------

        print(f"   -> Ambil: {start} s.d {end} ({deskripsi})")
        
        try:
            # Safety: Jangan sampai minta detik yang melebihi durasi video asli
            if end > video_asli.duration:
                end = video_asli.duration
            
            potongan = video_asli.subclip(start, end)
            clips.append(potongan)
        except Exception as e:
            print(f"   ⚠️ Gagal memotong bagian ini: {e}")

    # 3. Gabungkan Semua Potongan
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
                remove_temp=True
            )
            video_asli.close()
            print(f"✅ Video Selesai! Disimpan di: {output_path}")
            return output_path
        except Exception as e:
            print(f"❌ Gagal Render: {e}")
            video_asli.close()
            return None
    else:
        # --- PENGAMAN TERAKHIR ---
        # Jika AI tidak menemukan momen bagus (list kosong),
        # Jangan error, tapi kembalikan video asli saja (atau return None dengan pesan jelas)
        print("⚠️ AI tidak menemukan momen menarik, atau semua terfilter.")
        video_asli.close()
        return None