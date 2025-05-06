import os
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from moviepy.editor import VideoFileClip
from PIL import Image
import csv

# === 設定參數 ===
video_path = "small_video.mp4"
audio_path = "audio.wav"  # 建議使用 ffmpeg 提前轉好音訊
output_frame_dir = "matched_frames"
target_freq_range = (1000, 5000)  # 目標頻率範圍 (Hz)
power_threshold = 3  # 頻率強度閾值
frame_interval_sec = 0.5  # 擷取時間間隔（秒）
os.makedirs(output_frame_dir, exist_ok=True)

# === 步驟 1：讀取影片 & 音訊 ===
clip = VideoFileClip(video_path)
y, sr = librosa.load(audio_path, sr=None)

# === 步驟 2：STFT + FFT 分析 ===
S = np.abs(librosa.stft(y))
DB = librosa.amplitude_to_db(S, ref=np.max)
frequencies = librosa.fft_frequencies(sr=sr)
times = librosa.frames_to_time(np.arange(S.shape[1]), sr=sr)

# FFT 頻譜
fft = np.fft.fft(y)
fft_mag = np.abs(fft)
fft_freq = np.fft.fftfreq(len(fft), d=1/sr)
pos_idx = fft_freq > 0
fft_freq = fft_freq[pos_idx]
fft_mag = fft_mag[pos_idx]

# === 繪製 STFT + FFT 並儲存 ===
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))

# STFT
img = librosa.display.specshow(DB, sr=sr, x_axis='time', y_axis='linear', ax=ax1)
ax1.set_title("STFT Spectrogram")
fig.colorbar(img, ax=ax1, format="%+2.0f dB")

# FFT
ax2.plot(fft_freq, fft_mag)
ax2.set_xlim(0, 10000)
ax2.set_xlabel("Frequency (Hz)")
ax2.set_ylabel("Magnitude")
ax2.set_title("FFT Spectrum")
ax2.grid(True)

plt.tight_layout()
plt.savefig("spectrogram_and_fft.png")
plt.show()

# === 步驟 3：找出特定頻率強度時間點 ===
freq_idx = np.where((frequencies >= target_freq_range[0]) &
                    (frequencies <= target_freq_range[1]))[0]

active_times = []
for i, t in enumerate(times):
    spectrum = S[:, i]
    avg_power = np.mean(spectrum[freq_idx])
    if avg_power > power_threshold:
        active_times.append(t)

# 避免重複擷取（根據時間間隔）
filtered_times = []
last_time = -frame_interval_sec
for t in active_times:
    if t - last_time >= frame_interval_sec:
        filtered_times.append(t)
        last_time = t

# === 步驟 4：擷取畫面幀 ===
for idx, t in enumerate(filtered_times):
    frame = clip.get_frame(t)
    img = Image.fromarray(frame)
    img.save(f"{output_frame_dir}/frame_{idx:03d}_at_{int(t*1000)}ms.jpg")

# === 步驟 5：輸出文字與 CSV 結果 ===
with open("matched_times.txt", "w") as f:
    for i, t in enumerate(filtered_times):
        f.write(f"{i+1}. {t:.3f} 秒\n")

with open("matched_times.csv", "w", newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Frame Index", "Time (s)", "Time (ms)"])
    for idx, t in enumerate(filtered_times):
        writer.writerow([idx+1, round(t, 3), int(t * 1000)])

# === 印出時間點 ===
print("\n偵測到振翅頻率強度超過閾值的時間點（秒）：")
for i, t in enumerate(filtered_times):
    print(f"{i+1:>2}. {t:.2f} 秒")
