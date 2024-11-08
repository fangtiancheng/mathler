from typing import List, Tuple, Optional, Union
from PIL import Image, ImageDraw, ImageFont
import os
import ast
from enum import IntEnum
from utils.basicConfigs import ROOT_PATH, SAVE_TMP_PATH, FONTS_PATH
import random
import itertools

class GuessResult(IntEnum):
    WIN = 0  # 猜出正确单词
    LOSS = 1  # 达到最大可猜次数，未猜出正确单词
    DUPLICATE = 2  # 单词重复
    ILLEGAL = 3  # 单词不合法
    LEGAL = 4 # 合法的猜测

def generate_expression(length, limit: int=10_000) -> Tuple[str, int]:
    if length < 3 :
        raise ValueError("长度太短，至少需要3个字符")
    
    # 第一个模块：确定运算符
    num_operators = random.randint(1, length // 2 - 1) #TODO: num_operators服从一定的分布
    valid_operators = ['+', '-', '*', '/']
    probabilities = [0.3, 0.3, 0.3, 0.1]
    operators = random.choices(valid_operators, probabilities, k=num_operators)
    
    # 第二个模块，确定各数字长度
    num_numbers = num_operators + 1
    num_lens = [1] * num_numbers
    extra_num_len = length - num_operators - num_numbers
    for i in random.choices(list(range(num_numbers)), k=extra_num_len):
        num_lens[i] += 1

    
    # 第三个模块，根据长度生成数字
    def gen_num_by_len(len: int)->int:
        if len <= 0:
            raise ValueError('len <= 0')
        if len == 1:
            return random.randint(0, 9)
        return random.randint(10**(len-1), (10**len)-1)
    
    # 第四个模块：验证准确性
    for _ in range(30):
        nums = [str(gen_num_by_len(len)) for len in num_lens]
        result = ''.join([x for pair in itertools.zip_longest(nums, operators) for x in pair if x is not None])
        try:
            value = eval(result)
            if value == int(value) and abs(int(value)) <= limit:
                return result, int(value)
        except:
            continue
    return generate_expression(length, limit)

def calc_mathler_expr(word: str)->Tuple[bool, Union[int, str]]:
    legal_ops = [ast.Add, ast.Sub, ast.Mult, ast.Div] # no binary
    for c in word:
        if not c.isdigit() and c not in '+-*/':
            return False, '不合法字符“{}”，仅允许数字和+-*/'.format(c)
    def check_expr(expr: ast.expr) -> Tuple[bool, str]:
        if isinstance(expr, ast.BinOp):
            if type(expr.op) not in legal_ops:
                return False, '不合法运算符"{}"'.format(type(expr.op).__name__)
            result, reason = check_expr(expr.left)
            if not result:
                return False, reason
            result, reason = check_expr(expr.right)
            if not result:
                return False, reason
            return True, ""
        elif isinstance(expr, ast.Constant):
            if not isinstance(expr.value, int):
                return False, "不合法常数“{}”".format(expr.value)
            return True, ""
        else: # no unary op
            return False, "不合法运算符“{}”".format(type(expr).__name__)
    try:
        tree = ast.parse(word)
        check_result, reason = check_expr(tree.body[0].value)
        if not check_result:
            return False, reason
        value = eval(word)
        if isinstance(value, float):
            if int(value) != value:
                return False, "计算结果“{}”非整数".format(value)
        return True, int(value)
    except Exception as e:
        return False, "解析时出错：{}".format(e)

class MathlerGame:
    def __init__(self, word: str):
        legal, value = calc_mathler_expr(word)
        if not legal:
            raise ValueError('mathler word illegal: {}'.format(value))
        self.word: str = word  # 算式
        self.value: int = value # 算式的值
        self.result = f"【算式】：{self.word}\n【值】：{self.value}"
        self.word_lower: str = self.word.lower()
        self.length: int = len(word)  # 单词长度
        self.rows: int = self.length + 1  # 可猜次数
        self.guessed_words: List[str] = []  # 记录已猜单词

        self.block_size = (40, 40)  # 文字块尺寸
        self.block_padding = (10, 10)  # 文字块之间间距
        self.padding = (20, 20)  # 边界间距
        self.border_width = 2  # 边框宽度
        self.font_size = 20  # 字体大小
        self.font = ImageFont.truetype(os.path.join(ROOT_PATH, FONTS_PATH, "KarnakPro-Bold.ttf"), self.font_size, encoding="utf-8")

        self.correct_color = (134, 163, 115)  # 存在且位置正确时的颜色
        self.exist_color = (198, 182, 109)  # 存在但位置不正确时的颜色
        self.wrong_color = (123, 123, 124)  # 不存在时颜色
        self.border_color = (123, 123, 124)  # 边框颜色
        self.bg_color = (255, 255, 255)  # 背景颜色
        self.font_color = (255, 255, 255)  # 文字颜色
        
    def legal_word(self, word:str) -> Tuple[bool, str]:
        legal_ops = [ast.Add, ast.Sub, ast.Mult, ast.Div] # no binary
        if len(word) != self.length:
            return False, '算式长度不对，期望长度{}，实际长度{}'.format(self.length, len(word))
        legal, value = calc_mathler_expr(word)
        if not legal:
            return False, value
        if value == self.value:
            return True, '合法的猜测'
        else:
            return False, '结果不对，期望结果{}，实际结果{}'.format(self.value, value)
        
    
    def guess(self, word: str) -> Tuple[GuessResult, str]:
        word = word.lower()
        if word == self.word_lower:
            self.guessed_words.append(word)
            return GuessResult.WIN, '恭喜获胜'
        if word in self.guessed_words:
            return GuessResult.DUPLICATE, '重复的猜测'
        legal, reason = self.legal_word(word)
        if not legal:
            return GuessResult.ILLEGAL, reason
        self.guessed_words.append(word)
        if len(self.guessed_words) == self.rows:
            return GuessResult.LOSS, '用掉了所有的机会'
        return GuessResult.LEGAL, '可嘉的猜测'

    def draw_block(self, color: Tuple[int, int, int], letter: str) -> Image.Image:
        block = Image.new("RGB", self.block_size, self.border_color)
        inner_w = self.block_size[0] - self.border_width * 2
        inner_h = self.block_size[1] - self.border_width * 2
        inner = Image.new("RGB", (inner_w, inner_h), color)
        block.paste(inner, (self.border_width, self.border_width))
        if letter:
            letter = letter.upper()
            draw = ImageDraw.Draw(block)
            bbox = self.font.getbbox(letter)
            x = (self.block_size[0] - bbox[2]) / 2
            y = (self.block_size[1] - bbox[3]) / 2
            draw.text((x, y), letter, font=self.font, fill=self.font_color)
        return block

    def draw(self, savePath:str):
        board_w = self.length * self.block_size[0]
        board_w += (self.length - 1) * self.block_padding[0] + 2 * self.padding[0]
        board_h = self.rows * self.block_size[1]
        board_h += (self.rows - 1) * self.block_padding[1] + 2 * self.padding[1]
        board_size = (board_w, board_h)
        board = Image.new("RGB", board_size, self.bg_color)

        for row in range(self.rows):
            if row < len(self.guessed_words):
                guessed_word = self.guessed_words[row]

                word_incorrect = ""  # 猜错的字母
                for i in range(self.length):
                    if guessed_word[i] != self.word_lower[i]:
                        word_incorrect += self.word_lower[i]
                    else:
                        word_incorrect += "_"  # 猜对的字母用下划线代替

                blocks: List[Image.Image] = []
                for i in range(self.length):
                    letter = guessed_word[i]
                    if letter == self.word_lower[i]:
                        color = self.correct_color
                    elif letter in word_incorrect:
                        """
                        一个字母的黄色和绿色数量与答案中的数量保持一致
                        以输入apple，答案adapt为例
                        结果为apple的第一个p是黄色，第二个p是灰色
                        代表答案中只有一个p，且不在第二个位置
                        """
                        word_incorrect = word_incorrect.replace(letter, "_", 1)
                        color = self.exist_color
                    else:
                        color = self.wrong_color
                    blocks.append(self.draw_block(color, letter))

            else:
                blocks = [
                    self.draw_block(self.bg_color, "") for _ in range(self.length)
                ]

            for col, block in enumerate(blocks):
                x = self.padding[0] + (self.block_size[0] + self.block_padding[0]) * col
                y = self.padding[1] + (self.block_size[1] + self.block_padding[1]) * row
                board.paste(block, (x, y))
        board.save(savePath)

    def get_hint(self) -> str:
        letters = set()
        for word in self.guessed_words:
            for letter in word:
                if letter in self.word_lower:
                    letters.add(letter)
        return "".join([i if i in letters else "@" for i in self.word_lower])

    def draw_hint(self, hint: str, savePath:str):
        board_w = self.length * self.block_size[0]
        board_w += (self.length - 1) * self.block_padding[0] + 2 * self.padding[0]
        board_h = self.block_size[1] + 2 * self.padding[1]
        board = Image.new("RGB", (board_w, board_h), self.bg_color)

        for i in range(len(hint)):
            letter = hint[i].replace("@", "")
            color = self.correct_color if letter else self.bg_color
            x = self.padding[0] + (self.block_size[0] + self.block_padding[0]) * i
            y = self.padding[1]
            board.paste(self.draw_block(color, letter), (x, y))
        board.save(savePath)

if __name__ == "__main__":
    if True:
        mathler = MathlerGame('1+2+3+4')
        print(mathler.guess('6//3+21'))
        mathler.draw(os.path.join(ROOT_PATH, SAVE_TMP_PATH, '1.png'))
        print(mathler.guess('1+3+3+3'))
        mathler.draw(os.path.join(ROOT_PATH, SAVE_TMP_PATH, '2.png'))
        print(mathler.guess('1+2+3+4'))
        mathler.draw(os.path.join(ROOT_PATH, SAVE_TMP_PATH, '3.png'))
    else:
        for _ in range(50):
            expr, val = generate_expression(10)
            print(expr, val)