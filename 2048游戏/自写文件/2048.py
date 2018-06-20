# -*- coding:utf-8 -*-
import curses
import numpy as np
import random
from threading import Thread
import time
# 创建按键与功能相对应的字典，{数字：功能}
action = ['Up', 'Left', 'Down', 'Right', 'Restart', 'Exit']
action_key1 = [ord(ch) for ch in 'WASDRQwasdrq']
action_key2 = [259, 260, 258, 261]  # 这是上左下右键的ASCII码
action_dic = dict(zip(action_key1, action*2))
action_dic.update(dict(zip(action_key2, action[:4])))
# print(action_dic)


def get_use_input(screen):
    char = 'N'
    while char not in action_dic:
        char = screen.getch()
    return char

class Game2048(object):
    def __init__(self, width=4, height=4, win=64):
        self.data = np.zeros((height, width), dtype=np.int64)
        self.win = win
        self.score = 0
        self.score_hei = 0
        self.restart()      # 重置数据
    # 重置棋盘功能
    def restart(self):
        self.pawn()
        self.pawn()
    # 画图功能
    def draw(self, screens):
        help_info1 = '     W(up) A(left) S(down) D(right)'
        help_info2 = '          R(restart) Q(exit)'
        win_info = '               You are win!'
        over_info = '              You are over!'
        def draw_cast(string):
            screens.addstr(string+'\n')
        def draw_separator():
            sea = ('+------'*self.data.shape[1])+'\n'
            draw_cast(sea)
        def draw_row(rows):
            sea = ''
            for i in range(self.data.shape[1]):
                sea += ('|  {}  |'.format(self.data[rows, i]) if self.data[rows, i] != 0 else '|     |')
            draw_cast(sea)
        screens.clear()
        draw_cast('SCORE: ' + str(self.score))
        draw_cast('SCORE_HEI: '+ str(self.score_hei))
        for row in range(self.data.shape[0]):
            draw_separator()
            draw_row(row)
        draw_separator()
        if self.is_win():
            draw_cast(win_info)
        if self.is_over():
            draw_cast(over_info)
        draw_cast(help_info1)
        draw_cast(help_info2)
    # 将数组形成一行并迭代第一行的数据
    def is_win(self):
        return any([i for i in self.data.reshape(1, -1)[0] if i == self.win])
    # 统计数组中的非0个数，然后判断其数组是否全为0
    def is_over(self):
        over = np.count_nonzero(self.data)
        return over == self.data.shape[0] * self.data.shape[1]
    # 在空格中随机生成一个数
    def pawn(self):
        row = [i for i in range(self.data.shape[0])]
        col = [i for i in range(self.data.shape[1])]
        index = []
        for i in row:
            index += [(i, x) for x in col]
        rows, cols = np.nonzero(self.data)
        index = set(index) - set(zip(rows, cols))
        val = 2
        index_rand = random.choice(list(index))
        self.data[index_rand] = val
    def move(self, use_input):
        act = action_dic[use_input]
        return self.move_func(act)
    def move_func(self, direction):
        test = self.data.copy()
        transpose = False
        if direction == 'Up':
            direction = 'Left'
            self.data = self.data.T
            transpose = True
        if direction == 'Down':
            direction = 'Right'
            transpose = True
            self.data = self.data.T
        if direction == 'Right' or direction == 'Left':
            in_row = 0
            ele = []
            for row in self.data:
                row = list(row)
                for i in range(len(row)):
                    if row[i] != 0:
                        ele.append(row[i])
                if not ele:
                    in_row += 1
                    continue
                if len(ele) > 1:
                    for i in range(len(ele)-1):
                        if ele[i] == ele[i + 1]:
                            self.score += ele[i]
                            if direction == 'Right':
                                ele[i+1] *= 2
                                ele[i] = 0
                            else:
                                ele[i] *= 2
                                ele[i+1] = 0
                    clea = ele.count(0)
                    for i in range(clea):
                        ele.remove(0)
                if direction == 'Right':
                    self.data[in_row, -len(ele):] = ele
                    self.data[in_row, :-len(ele)] = 0

                else:
                    self.data[in_row, :len(ele)] = ele
                    self.data[in_row, len(ele):] = 0

                ele.clear()
                in_row += 1
        if transpose:
            self.data = self.data.T
        test = (self.data == test)
        if np.sum(test) == 0:
            return False
        return True


    def ret(self):
        self.data[:] = 0
        self.restart()
        if self.score > self.score_hei:
            self.score_hei = self.score
        self.score = 0






def main(screen):
    # 初始化函数，执行将数据清空重置。
    def init():
        game_cl.draw(screen)
        return 'Game'
    # 监控用户的输入进行游戏并判断输赢
    def game():
        use_input = get_use_input(screen)
        ret = game_cl.move(use_input)
        if ret:
            game_cl.pawn()
        game_cl.draw(screen)
        screen.addstr('%s'%game_cl.data)

        if action_dic[use_input] == 'Restart':
            game_cl.ret()
            game_cl.draw(screen)
        if action_dic[use_input] == 'Exit':
            return 'Exit'
        if game_cl.is_win():
            return 'Win'
        if game_cl.is_over():
            return 'Over'
        return 'Game'
    def win():

        use_input = get_use_input(screen)
        stat = action_dic[use_input]
        if stat == 'Restart':
            game_cl.ret()
            game_cl.draw(screen)
        if stat == 'Exit':
            return 'Exit'
        return 'Win'
    def over():

        use_input = get_use_input(screen)
        stat = action_dic[use_input]
        if stat == 'Restart':
            game_cl.ret()
            game_cl.draw(screen)
        if stat == 'Exit':
            return 'Exit'
        return 'Over'

    game_cl = Game2048()
    state_init = 'Init'
    state = {
        'Init': init,
        'Game': game,
        'Win': win,
        'Over': over,
        'Exit':lambda :'Exit'
    }

    while state_init != 'Exit':
        state_init = state[state_init]()    # 状态函数执行时，返回的是下一个状态。

curses.wrapper(main)