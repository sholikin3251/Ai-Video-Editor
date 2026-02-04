from moviepy.editor import VideoFileClip, concatenate_videoclips
import os
import uuid

def make_vertical_safe(clip):
    try:
        w, h = clip.size
        if h > w: return clip
        
        new_width = h * (9/16)
        if new_width > w: new_width = w
        center_x = w / 2
        x1 = center_x - (new_width / 2)
        return clip.crop(x1=x1, y1=0, width=new_width, height=h)
    except:
        return clip

def proses_video_otomatis(input_path, output_path, data_json):
    print(f"✂️  Memproses: {os.path.basename(input_path)}")
    
    video_asli = None
    try:
        video_asli = VideoFileClip(input_path)
    except:
        return None

    clips = []
    segmen_list = data_json.get('segments', [])

    # Auto-Hook jika AI diam
    if not segmen_list:
        segmen_list = [{"start": 0, "end": min(5, video_asli.duration), "description": "Hook"}]

    for segmen in segmen_list:
        try:
            start = float(segmen.get('start', 0))
            end = float(segmen.get('end', 0))
            if start >= end: continue
            if end > video_asli.duration: end = video_asli.duration
            
            # Potong & Crop
            potongan = video_asli.subclip(start, end)
            potongan = make_vertical_safe(potongan)
            clips.append(potongan)
        except:
            pass

    # GABUNGKAN
    if len(clips) > 0:
        try:
            # Gunakan method='compose' agar aman
            final = concatenate_videoclips(clips, method="compose")
            
            # Nama file audio temp unik
            temp_audio = f"temp_{uuid.uuid4()}.m4a"
            
            # --- PENGATURAN RENDER ANTI-CORRUPT ---
            final.write_videofile(
                output_path, 
                fps=24, 
                codec='libx264', 
                audio_codec='aac',
                threads=1,          # Tetap 1 biar stabil di Windows
                preset='medium',    
                # BARIS INI KUNCINYA AGAR BROWSER BISA BACA:
                ffmpeg_params=['-pix_fmt', 'yuv420p'], 
                temp_audiofile=temp_audio,
                remove_temp=True,
                verbose=False,
                logger=None
            )
            # ---------------------------------------
            
            video_asli.close()
            final.close()
            
            # Cek apakah file benar-benar ada isinya?
            if os.path.exists(output_path) and os.path.getsize(output_path) > 1000:
                print(f"✅ SUKSES! File aman: {output_path}")
                return output_path
            else:
                print("❌ File terbuat tapi 0 bytes (Kosong).")
                return input_path

        except Exception as e:
            print(f"❌ Gagal Render: {e}")
            if video_asli: video_asli.close()
            return input_path 
    else:
        if video_asli: video_asli.close()
        return input_path