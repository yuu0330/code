import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import noisereduce as nr
import soundfile as sf

# ===== 1. 讀取音訊檔 =====
file_path = "振翅頻率.mp3"
y, sr = librosa.load(file_path, sr=None)

# ===== 2. 降噪處理 =====
# 可選擇是否指定純噪音樣本（例如前1秒）
# noise_sample = y[0:int(sr * 1)]
# y_denoised = nr.reduce_noise(y=y, y_noise=noise_sample, sr=sr)
y_denoised = nr.reduce_noise(y=y, sr=sr)

# ===== 3. 繪製 STFT 頻譜圖 =====
D = librosa.stft(y_denoised)
DB = librosa.amplitude_to_db(abs(D), ref=np.max)

plt.figure(figsize=(10, 4))
librosa.display.specshow(DB, sr=sr, x_axis='time', y_axis='linear')
plt.colorbar(format='%+2.0f dB')
plt.title('STFT Spectrogram (After Noise Reduction)')
plt.tight_layout()
plt.show()

# ===== 4. 繪製 FFT 頻譜（頻率 vs 強度） =====
# 取整段音訊的 FFT
fft = np.fft.fft(y_denoised)
fft_mag = np.abs(fft)
freq = np.fft.fftfreq(len(fft), d=1/sr)

# 只保留正頻率
half_range = freq > 0
freq = freq[half_range]
fft_mag = fft_mag[half_range]

plt.figure(figsize=(10, 4))
plt.plot(freq, fft_mag)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Amplitude")
plt.title("FFT Spectrum (After Noise Reduction)")
plt.grid(True)
plt.tight_layout()
plt.show()

# ===== 5. 儲存處理後音訊（可選） =====
sf.write("reduced_output.wav", y_denoised, sr)
