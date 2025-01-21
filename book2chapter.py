import argparse
from pathlib import Path
from loguru import logger
import chardet
from ftfy import fix_text
import zhconv
import cn2an
import re
import sys
from shutil import move
from tools import (
    find_project_root,
    convert_arabic_to_chinese,
    convert_punctuation_to_chinese,
)


class BookProcessor:
    def __init__(self, book_path: str):
        self.book_path = Path(book_path)
        self.book_name = self.book_path.stem
        self.book_dir = None
        self._init_dir()

    def _init_dir(self):
        """
        初始化小说目录
        """
        current_file_path = Path(__file__).resolve()
        project_root = find_project_root(current_file_path)
        logger.debug(f"项目根目录: {project_root}")
        self.book_dir = project_root / "auto_target" / self.book_name / "data"
        self.book_dir.mkdir(parents=True, exist_ok=True)

    def read_book_content(self) -> str:
        """
        读取小说文件内容
        """
        book_path = self.book_dir / f"{self.book_name}.txt"
        if not book_path.exists():
            logger.error(f"文件 {book_path} 不存在")
            sys.exit(1)

        try:
            with open(book_path, "r", encoding="utf-8") as f:
                content = f.read()
            logger.debug(f"成功读取文件: {book_path}")
            return content
        except Exception as e:
            logger.error(f"读取文件 {book_path} 失败: {e}")
            sys.exit(1)

    def split_chapter(self, content: str) -> list[tuple[int, str]]:
        """
        拆分章节
        输入: 小说文本内容
        输出: 章节列表 [(idx, str)]
        """
        content = convert_arabic_to_chinese(content)
        content = zhconv.convert(content, "zh-cn")
        content = convert_punctuation_to_chinese(content)

        # 修改后的正则表达式，能够匹配两种格式
        chapter_pattern = re.compile(r"第([零一二三四五六七八九十百千]+)(章|节)\s*(.*)")

        chapters = []
        chapter_content = []
        chapter_idx = 0  # 从 0 开始编号

        for line in content.splitlines():
            line = line.strip()
            match = chapter_pattern.match(line)
            if match:
                # 如果当前章节内容不为空，保存当前章节
                if chapter_content:
                    chapters.append((chapter_idx, "\n".join(chapter_content)))
                    chapter_idx += 1

                # 增加章节号处理：将中文数字转换为阿拉伯数字
                chinese_number = match.group(1)
                arabic_number = cn2an.cn2an(chinese_number, mode="smart")
                chapter_title = match.group(3).strip()

                # 如果章节标题为空，表示只有“第xx章”，则继续处理
                if not chapter_title:
                    chapter_title = f"第{arabic_number}章"
                else:
                    chapter_title = f"第{arabic_number}章 {chapter_title}"

                chapter_content = [chapter_title]
            else:
                if line:  # 忽略空行
                    chapter_content.append(line)

        # 保存最后一章
        if chapter_content:
            chapters.append((chapter_idx, "\n".join(chapter_content)))

        return chapters

    def save_chapters(self, chapters: list[tuple[int, str]]):
        """
        保存章节到文件
        """
        for idx, chapter_content in chapters:
            chapter_path = self.book_dir / "data" / f"chapter_{idx}.txt"
            chapter_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(chapter_path, "w", encoding="utf-8") as chapter_file:
                    chapter_file.write(chapter_content)
                logger.debug(f"保存章节 {idx}: {chapter_path}")
            except Exception as e:
                logger.error(f"保存章节 {idx} 失败: {e}")
                sys.exit(1)

    def convert_file_to_utf8(self):
        """
        将文件转换为 UTF-8 编码
        """
        encoding = self.detect_file_encoding(self.book_path)
        if not encoding:
            logger.error(f"无法检测文件编码: {self.book_path}")
            sys.exit(1)

        try:
            with open(self.book_path, "r", encoding=encoding, errors="ignore") as f:
                content = f.read()
        except UnicodeDecodeError:
            logger.error(f"文件解码失败: {self.book_path} (检测到的编码: {encoding})")
            sys.exit(1)

        content = fix_text(content)

        try:
            with open(self.book_path, "w", encoding="utf-8") as f:
                f.write(content)
            logger.debug(f"文件已转换为 UTF-8: {self.book_path}")
        except Exception as e:
            logger.error(f"文件写入失败: {self.book_path}, 错误信息: {e}")
            sys.exit(1)

    def detect_file_encoding(self, file_path: Path) -> str:
        """
        检测文件编码
        """
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read()
                result = chardet.detect(raw_data)
            encoding = result["encoding"]
            if encoding is None:
                logger.error(f"无法检测文件编码: {file_path}")
                sys.exit(1)
            return encoding
        except Exception as e:
            logger.error(f"检测文件编码失败: {e}")
            sys.exit(1)

    def move_file_to_target_dir(self):
        """
        将文件移动到目标目录
        """
        target_dir = self.book_dir
        target_file_path = target_dir / self.book_path.name
        target_file_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            move(self.book_path, target_file_path)
            logger.debug(f"文件已移动到目标目录: {target_file_path}")
        except Exception as e:
            logger.error(f"移动文件失败: {e}")
            sys.exit(1)


def main(book_path: str):
    processor = BookProcessor(book_path)
    processor.convert_file_to_utf8()
    processor.move_file_to_target_dir()

    # 读取小说内容
    content = processor.read_book_content()

    # 拆分章节
    chapters = processor.split_chapter(content)

    # 保存章节
    processor.save_chapters(chapters)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="小说 txt 拆分")
    parser.add_argument(
        "book_path",
        type=str,
        help="小说绝对路径",
        default="/root/code/audio_book/auto_target/埃隆·马斯克传/data/埃隆·马斯克传.txt",
        nargs="?",  # 参数可选
    )
    args = parser.parse_args()
    book_path = args.book_path

    if book_path:
        main(book_path)
    else:
        logger.error("小说路径错误")
        sys.exit(1)
