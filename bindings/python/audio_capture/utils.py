import numpy as np
import soundfile as sf
from typing import List, Union

class WavWriter:
    """WAV 文件写入器"""
    def __init__(self, filename: str, sample_rate: int, channels: int, bits_per_sample: int):
        """
        初始化 WAV 文件写入器
        
        Args:
            filename: WAV 文件名
            sample_rate: 采样率
            channels: 声道数
            bits_per_sample: 位深度
        """
        self.filename = filename
        self.sample_rate = sample_rate
        self.channels = channels
        self.bits_per_sample = bits_per_sample
        self._soundfile = sf.SoundFile(
            filename,
            mode='w',
            samplerate=sample_rate,
            channels=channels,
            subtype=self._get_subtype()
        )

    def _get_subtype(self) -> str:
        """根据位深度获取 soundfile 子类型"""
        if self.bits_per_sample == 16:
            return 'PCM_16'
        elif self.bits_per_sample == 24:
            return 'PCM_24'
        elif self.bits_per_sample == 32:
            return 'PCM_32'
        else:
            raise ValueError(f"Unsupported bits per sample: {self.bits_per_sample}")

    def write_float32(self, data: Union[List[float], np.ndarray]) -> None:
        """
        写入 float32 格式的音频数据
        
        Args:
            data: float32 格式的音频数据
        """
        if isinstance(data, list):
            data = np.array(data, dtype=np.float32)
        elif not isinstance(data, np.ndarray):
            raise TypeError("Data must be a list or numpy array")

        # 确保数据类型正确
        if data.dtype != np.float32:
            data = data.astype(np.float32)

        # 如果是多声道，重塑数组
        if self.channels > 1 and len(data.shape) == 1:
            data = data.reshape(-1, self.channels)

        self._soundfile.write(data)

    def close(self) -> None:
        """关闭文件"""
        if self._soundfile is not None:
            self._soundfile.close()
            self._soundfile = None

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()

    def __del__(self):
        """析构函数"""
        self.close() 