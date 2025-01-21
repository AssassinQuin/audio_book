import re


def find_project_root(current_path):
    # 定义项目根目录的标识文件
    markers = [".git", "requirements.txt", "setup.py"]
    for marker in markers:
        if (current_path / marker).exists():
            return current_path
    # 如果未找到标识文件，继续向父目录查找
    if current_path.parent == current_path:
        raise FileNotFoundError("未找到项目根目录")
    return find_project_root(current_path.parent)


def convert_arabic_to_chinese(text: str) -> str:
    """
    将文本中的阿拉伯数字转换为中文数字，并处理年月日时分秒、小数、百分数等。
    若字母前后紧跟数字，则不转换。
    """
    import cn2an

    # 定义年份转换函数
    def convert_year(year: str) -> str:
        year_map = {
            "0": "零",
            "1": "一",
            "2": "二",
            "3": "三",
            "4": "四",
            "5": "五",
            "6": "六",
            "7": "七",
            "8": "八",
            "9": "九",
        }
        return "".join(year_map.get(char, char) for char in year)

    # 处理年月日时分秒类数字
    time_pattern = r"(\d+)(年|月|日|天|小时|时|分钟|分|秒)"
    for match in re.finditer(time_pattern, text):
        number, unit = match.group(1), match.group(2)
        if unit == "年":
            chinese_number = convert_year(number)
        else:
            chinese_number = cn2an.an2cn(number, mode="low")
        time_str = f"{chinese_number}{unit}"
        text = text.replace(f"{number}{unit}", time_str)

    # 处理百分数
    percent_pattern = r"(\d+(?:\.\d+)?)%"
    for match in re.finditer(percent_pattern, text):
        percent_number = match.group(1)
        # 确保百分数部分转换为“百分之X”
        chinese_number = cn2an.an2cn(percent_number, mode="low")
        text = text.replace(f"{percent_number}%", f"百分之{chinese_number}")

    # 处理小数
    decimal_pattern = r"(\d+\.\d+)"
    for match in re.finditer(decimal_pattern, text):
        decimal_number = match.group(1)
        chinese_number = cn2an.an2cn(decimal_number, mode="low")
        text = text.replace(decimal_number, chinese_number)

    # 处理普通数字，排除字母前后紧跟的数字
    number_pattern = r"(?<![a-zA-Z])\d+(?:(?:,| )\d{3})*(?:\.\d+)?(?![a-zA-Z])"
    for match in re.finditer(number_pattern, text):
        number = match.group(0)
        clean_number = number.replace(",", "").replace(" ", "")
        chinese_number = cn2an.an2cn(clean_number, mode="low")
        text = text.replace(number, chinese_number)

    return text


def convert_punctuation_to_chinese(text: str) -> str:
    """
    将英文标点符号转换为中文标点符号，并排除类似 zip.com 的情况
    """
    # 定义英文标点到中文标点的映射
    punctuation_map = {
        ",": "，",
        "!": "！",
        "?": "？",
        ":": "：",
        ";": "；",
        "(": "（",
        ")": "）",
        "<": "《",
        ">": "》",
    }

    # 逐个替换标点符号
    for eng, chn in punctuation_map.items():
        text = text.replace(eng, chn)

    # 单独处理句点（.），排除类似 zip.com 的情况
    text = re.sub(r"(?<![a-zA-Z0-9])\.(?![a-zA-Z0-9])", "。", text)

    # 单独处理引号
    is_open_quote = True  # 标志变量，表示当前是前引号还是后引号
    result = []
    for char in text:
        if char == '"':
            if is_open_quote:
                result.append("“")  # 前引号
            else:
                result.append("”")  # 后引号
            is_open_quote = not is_open_quote  # 切换状态
        else:
            result.append(char)

    return "".join(result)
