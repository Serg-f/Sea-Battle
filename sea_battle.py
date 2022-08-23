import random as r

SIZE_GAME_POLE = 10


class Ship:
    def __init__(self, length, tp=1, x=None, y=None):
        if not type(length) == type(tp) == int or not 1 <= length <= 4 or tp not in (1, 2):
            raise ValueError('Wrong length or tp')
        self._length = length
        self._tp = tp
        self._x = x
        self._y = y
        self._is_move = True
        self._cells = [1] * length

    def __setattr__(self, key, value):
        if key == '_x' or key == '_y':
            if value is not None and type(value) != int:
                raise ValueError('Wrong x or y')
        super().__setattr__(key, value)

    def set_start_coords(self, x, y):
        self._x = x
        self._y = y

    def get_start_coords(self):
        return self._x, self._y

    def move(self, go):
        if self._is_move:
            if self._tp == 1:
                self._x += go
            else:
                self._y += go

    def is_collide(self, ship):
        ship_x, ship_y = ship.get_start_coords()
        width_self = self._length if self._tp == 1 else 1
        width_ship = ship._length if ship._tp == 1 else 1
        height_self = self._length if self._tp == 2 else 1
        height_ship = ship._length if ship._tp == 2 else 1
        max_x = max(self._x + width_self - 1, ship_x + width_ship - 1)
        min_x = min(self._x, ship_x)
        max_y = max(self._y + height_self - 1, ship_y + height_ship - 1)
        min_y = min(self._y, ship_y)
        if max_x - min_x < width_self + width_ship and max_y - min_y < height_self + height_ship:
            return True
        return False

    def is_out_pole(self, size):
        if self._tp == 1:
            if self._x < 0 or self._x + self._length > size or not 0 <= self._y < size:
                return True
        elif self._y < 0 or self._y + self._length > size or not 0 <= self._x < size:
            return True
        return False

    def __index_check(self, ind):
        if type(ind) != int or not 0 <= ind < len(self._cells):
            raise IndexError('Index out of range self._cells')

    def __getitem__(self, item):
        self.__index_check(item)
        return self._cells[item]

    def __setitem__(self, key, value):
        self.__index_check(key)
        if value == 'X':
            self._is_move = False
        self._cells[key] = value


class GamePole:
    def __init__(self, size):
        if type(size) != int or size < 8:
            raise ValueError('Wrong size of GamePole')
        self._size = size
        self._ships = []
        self._pole = [['-'] * size for _ in range(size)]
        self.init()

    def init(self):
        for i in range(4, 0, -1):
            for j in range(5 - i):
                self._ships.append(Ship(i, r.randint(1, 2)))
        for i, ship in enumerate(self._ships):
            is_collide = False
            while ship.get_start_coords() == (None, None) or is_collide:
                ship.set_start_coords(r.randrange(self._size), r.randrange(self._size))
                is_collide = ship.is_out_pole(self._size)
                for j in range(i):
                    if ship.is_collide(self._ships[j]):
                        is_collide = True
                        break
        self._init_pole()

    def _init_pole(self):
        self._pole = [['-'] * self._size for _ in range(self._size)]
        for ship in self._ships:
            x, y = ship.get_start_coords()
            for k in range(ship._length):
                if ship._tp == 1:
                    self._pole[x + k][y] = ship[k]
                else:
                    self._pole[x][y + k] = ship[k]

    def get_ships(self):
        return self._ships

    def __is_collide(self, ship_check):
        for ship in self._ships:
            if ship == ship_check:
                continue
            if ship.is_collide(ship_check):
                return True
            if ship_check.is_out_pole(self._size):
                return True
        return False

    def move_ships(self):
        for ship in self._ships:
            step = r.choice((-1, 1))
            ship.move(step)
            if self.__is_collide(ship):
                ship.move(-step)
                ship.move(-step)
                if self.__is_collide(ship):
                    ship.move(step)
        self._init_pole()

    def get_pole(self):
        return tuple(tuple(row) for row in self._pole)

    def show(self):
        print(' ', *range(self._size), sep='  ')
        [print(i, *row, sep='  ') for i, row in enumerate(self._pole)]
        print()

    def get_quant_of_destroyed_ships(self):
        res = 0
        for ship in self._ships:
            if all(map(lambda x: x == 'X', ship._cells)):
                res += 1
        return res


class SeaBattle:
    def __init__(self, size):
        self._size = size
        self.human_pole = GamePole(size)
        self.computer_pole = GamePole(size)
        self._shots = [['-'] * size for _ in range(size)]
        self._computer_shots = [['-'] * size for _ in range(size)]

    def __check_val(self, v):
        try:
            res = int(v)
            if not 0 <= res < self._size:
                raise ValueError(f'Value must be between 0 and {self._size - 1}')
        except TypeError as ex:
            raise TypeError('Value must be int type')
        except ValueError as ex:
            raise ex
        else:
            return res

    def _shot(self, pole: GamePole, x_shot, y_shot):
        if pole.get_pole()[x_shot][y_shot] == 1:
            for ship in pole.get_ships():
                x_ship, y_ship = ship.get_start_coords()
                for k in range(ship._length):
                    if ship._tp == 1 and x_shot == x_ship + k and y_shot == y_ship:
                        ship[k] = 'X'
                        return True
                    if ship._tp == 2 and x_shot == x_ship and y_shot == y_ship + k:
                        ship[k] = 'X'
                        return True
        return False

    def human_go(self):
        while 1:
            try:
                print('Input x:')
                y = self.__check_val(input())
                print('Input y:')
                x = self.__check_val(input())
            except Exception as ex:
                print(ex)
            else:
                destroyed_ships_quant = self.computer_pole.get_quant_of_destroyed_ships()
                if self._shot(self.computer_pole, x, y):
                    print("You've hit the target!")
                    self._shots[x][y] = 'X'
                    if destroyed_ships_quant != self.computer_pole.get_quant_of_destroyed_ships():
                        print("You've destroyed enemy ship!")
                        self._ship_destroyed(self._shots, x, y)
                    return True
                else:
                    print("You miss")
                    return False

    def computer_go(self):
        while 1:
            shot_x = r.randrange(self._size)
            shot_y = r.randrange(self._size)
            if self._computer_shots[shot_x][shot_y] == '-':
                break
        destroyed_ships_quant = self.human_pole.get_quant_of_destroyed_ships()
        if self._shot(self.human_pole, shot_x, shot_y):
            print("Computer has hit the target!")
            self._computer_shots[shot_x][shot_y] = 'X'
            if destroyed_ships_quant != self.human_pole.get_quant_of_destroyed_ships():
                print("Computer has destroyed your ship!")
                self._ship_destroyed(self._computer_shots, shot_x, shot_y)
            return True
        else:
            print("Computer miss")
            return False

    def _ship_destroyed(self, matrix: list, x, y):
        max_y = y
        for j in range(y, self._size):
            if matrix[x][j] == 'X':
                max_y = j
            else:
                break
        min_y = y
        for j in range(y, -1, -1):
            if matrix[x][j] == 'X':
                min_y = j
            else:
                break
        max_x = x
        for i in range(x, self._size):
            if matrix[i][y] == 'X':
                max_x = i
            else:
                break
        min_x = x
        for i in range(x, -1, -1):
            if matrix[i][y] == 'X':
                min_x = i
            else:
                break
        for i in range(self._size):
            for j in range(self._size):
                if min_x - 1 <= i <= max_x + 1 and min_y - 1 <= j <= max_y + 1 and \
                        not (min_x <= i <= max_x and min_y <= j <= max_y):
                    matrix[i][j] = '#'

    @property
    def is_human_win(self):
        for ship in self.computer_pole.get_ships():
            if any(map(lambda x: x == 1, ship._cells)):
                return False
        return True

    @property
    def is_computer_win(self):
        for ship in self.human_pole.get_ships():
            if any(map(lambda x: x == 1, ship._cells)):
                return False
        return True

    def __bool__(self):
        if self.is_human_win or self.is_computer_win:
            return False
        return True

    def show_human_pole_and_shots(self):
        print('Your pole:', 'Your shots:', sep='  ' * (self._size + 6))
        print(' ', *range(self._size), *[' '] * 4, *range(self._size), sep='  ')
        for i, (row_human, row_shots) in enumerate(zip(self.human_pole.get_pole(), self._shots)):
            print(i, *row_human, *[' '] * 3, i, *row_shots, sep='  ')
        print()

    def init_poles(self):
        self.human_pole._init_pole()
        self.computer_pole._init_pole()


battle = SeaBattle(SIZE_GAME_POLE)
is_human_go = True
while battle:
    battle.human_pole.move_ships()
    battle.computer_pole.move_ships()

    if is_human_go:
        battle.show_human_pole_and_shots()
        is_human_go = battle.human_go()
    else:
        is_human_go = not battle.computer_go()

battle.init_poles()
battle.show_human_pole_and_shots()

if battle.is_human_win:
    print('Congratulations! You win!')
else:
    print('Good luck next time')
