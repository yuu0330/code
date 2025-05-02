import os
import io
import time
import tempfile
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from flask import Flask, Response, send_file, abort

app = Flask(__name__)

AUDIO_FILE = "秋行軍蟲振翅.mp4"
SAMPLE_RATE = 16000
FRAME_DURATION = 1  # 每張圖對應 1 秒

waveform_frames = []
spectrogram_frames = []

def extract_audio_from_mp4(mp4_path, wav_path, sample_rate):
    cmd = f'ffmpeg -y -i "{mp4_path}" -vn -ac 1 -ar {sample_rate} -f wav "{wav_path}"'
    os.system(cmd)

def generate_frames():
    global waveform_frames, spectrogram_frames

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
        wav_path = tmp_wav.name

    extract_audio_from_mp4(AUDIO_FILE, wav_path, SAMPLE_RATE)
    audio, sr = librosa.load(wav_path, sr=SAMPLE_RATE, mono=True)

    total_samples = len(audio)
    samples_per_frame = int(SAMPLE_RATE * FRAME_DURATION)
    total_frames = total_samples // samples_per_frame

    for i in range(total_frames):
        start = i * samples_per_frame
        end = start + samples_per_frame
        chunk = audio[start:end]

        # --- 波形圖 ---
        fig1, ax1 = plt.subplots(figsize=(4, 2))
        librosa.display.waveshow(chunk, sr=sr, ax=ax1)
        ax1.axis('off')
        fig1.tight_layout(pad=0)
        buf1 = io.BytesIO()
        plt.savefig(buf1, format='jpeg', bbox_inches='tight', pad_inches=0)
        plt.close(fig1)
        buf1.seek(0)
        waveform_frames.append(buf1.read())

        # --- 頻譜圖 ---
        S = librosa.feature.melspectrogram(y=chunk, sr=sr)
        S_dB = librosa.power_to_db(S, ref=np.max)
        fig2, ax2 = plt.subplots(figsize=(4, 2))
        librosa.display.specshow(S_dB, sr=sr, x_axis=None, y_axis='mel', ax=ax2)
        ax2.axis('off')
        fig2.tight_layout(pad=0)
        buf2 = io.BytesIO()
        plt.savefig(buf2, format='jpeg', bbox_inches='tight', pad_inches=0)
        plt.close(fig2)
        buf2.seek(0)
        spectrogram_frames.append(buf2.read())

    os.remove(wav_path)

@app.route('/video')
def serve_video():
    return send_file(AUDIO_FILE, mimetype='video/mp4')

@app.route('/frame/waveform/<int:index>')
def serve_waveform(index):
    if 0 <= index < len(waveform_frames):
        return Response(waveform_frames[index], mimetype='image/jpeg')
    return abort(404)

@app.route('/frame/spectrogram/<int:index>')
def serve_spectrogram(index):
    if 0 <= index < len(spectrogram_frames):
        return Response(spectrogram_frames[index], mimetype='image/jpeg')
    return abort(404)

@app.route('/')
def index():
    return '''
    <html>
    <head>
        <title>影片 + 波形 + 頻譜 同步顯示</title>
        <script>
            let interval = null;

            function syncVisuals() {
                const video = document.getElementById('video');
                const wfImg = document.getElementById('waveform');
                const spImg = document.getElementById('spectrogram');

                if (interval) clearInterval(interval);
                interval = setInterval(() => {
                    if (!video.paused && !video.ended) {
                        const sec = Math.floor(video.currentTime);
                        const timestamp = new Date().getTime();
                        wfImg.src = "/frame/waveform/" + sec + "?t=" + timestamp;
                        spImg.src = "/frame/spectrogram/" + sec + "?t=" + timestamp;
                    }
                }, 500);
            }
        </script>
    </head>
    <body onload="syncVisuals()">
        <h2>🎬 同步影片 + 波形圖 + 頻譜圖</h2>
        <div style="display: flex; gap: 20px;">
            <div>
                <video id="video" width="480" controls autoplay onplay="syncVisuals()" onpause="syncVisuals()">
                    <source src="/video" type="video/mp4">
                    不支援影片播放
                </video>
            </div>
            <div>
                <h4>📈 波形圖</h4>
                <img id="waveform" src="/frame/waveform/0" width="480"><br>
                <h4>📊 頻譜圖</h4>
                <img id="spectrogram" src="/frame/spectrogram/0" width="480">
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    print("⏳ 正在處理音訊，產生波形與頻譜圖...")
    generate_frames()
    print(f"✅ 完成！波形圖：{len(waveform_frames)} 張，頻譜圖：{len(spectrogram_frames)} 張")
    app.run(host='0.0.0.0', port=5000)