from abc import ABC, abstractmethod


class AudioGenerator(ABC):
    """
    音频生成父类，定义通用接口。
    """

    def __init__(self):
        self.spk = None  # 当前说话人

    @abstractmethod
    def gen_audio(self, text: str):
        """
        生成音频
        :param text: 输入的文本
        :return: 音频信息（字典格式，包含音频数据、格式等）
        """
        pass

    def set_spk(self, spk: str) -> None:
        """
        设置说话人
        :param spk: 说话人标识
        """
        self.spk = spk
        print(f"说话人已设置为: {spk}")

    @abstractmethod
    def check_audio(self, audio_info, text: str) -> bool:
        """
        检查音频是否匹配文本
        :param audio_info: 音频信息
        :param text: 原始文本
        :return: 是否匹配
        """
        pass
