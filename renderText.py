# imported from old work at C:\Users\Okko Heiniö\Desktop\Python\Refraction\WaveCircuit\commandConsole.py
import math


class Text(list[str]):
    def __init__(self, *lines: 'str'):
        if len(lines) == 1 and lines[0]:
            if isinstance(lines[0], str):
                lines = lines[0].splitlines()
            else:
                lines = lines[0]
        self[:] = lines
        pass

    def InsertLine(self, row: 'int', string: 'str'):
        self.insert(row, string)

    def PopLine(self, index):
        self.pop(index)

    def InsertString(self, row: 'int', index: 'int', string: 'str'):
        self[row] = self[row][:index] + string + self[row][index:]

    def PopString(self, row: 'int', indexFrom: 'int', indexTo: 'int'):
        'removes text from line between indexFrom inclusive and indexTo exclusive'
        self[row] = self[row][:indexFrom] + self[row][indexTo:]

    def RemoveLineBreak(self, row: 'int'):
        if row > 0:
            self[row - 1] += self[row]
            self.pop(row)

    def InsertLineBreak(self, row: 'int', index: 'int'):
        self.InsertLine(row + 1, self[row][index:])
        self[row] = self[row][:index]

    def lineWrap(self, wrap: 'int'):
        out = Text()
        for line in self:
            for i in range(math.ceil(len(line) / wrap)):
                out.append(line[i * wrap:(i + 1) * wrap])
        return out

    def wrapAroundSelector(self, row: 'int', index: 'int'):
        "returns row,index. don't give impossible row values"

        if index > len(self[row]):
            # r = (row + 1) % len(self)
            if row == len(self) - 1:
                return len(self) - 1, len(self[-1])
            return row + 1, 0
        elif index < 0:
            # r = (row - 1) % len(self)
            if row == 0:
                return 0, 0
            return row - 1, len(self[row - 1])  # +index+1
        return row, index

    def clampSelector(self, row: 'int', index: 'int'):
        'returns row,index'
        if row < 0:
            return 0, 0
        elif row > len(self) - 1:
            return len(self) - 1, len(self[-1])
        else:
            return row, min(max(index, 0), len(self[row]))
        # if index < 0:
        #     return row, 0
        # elif index > len(self[row]):
        #     return row, len(self[row])
        # else:
        #     return row, index
        # # r = min(max(row, 0), len(self) - 1)
        # # i = min(max(index,0),len(self[r]))
        # return r, i

    def as_string(self): return '\n'.join(self)


class TextEditor:
    def __init__(self, text: 'list[str]|str|Text' = ''):
        if isinstance(text, str):
            self.text = Text(text.splitlines())
        else:
            self.text = Text(text)
        self.selectedLine = 0
        self.selectedIndex = 0

    def TypeText(self, string: 'str'):
        self.text.InsertString(self.selectedLine, self.selectedIndex, string)
        self.MoveRight(len(string))

    def Backspace(self):
        if self.selectedIndex == 0:
            if self.selectedLine == 0:
                return
            self.MoveLeft()
            self.text.RemoveLineBreak(self.selectedLine + 1)
            return
        self.MoveLeft()
        self.text.PopString(self.selectedLine, self.selectedIndex, self.selectedIndex + 1)

    def Enter(self):
        self.text.InsertLineBreak(self.selectedLine, self.selectedIndex)
        self.MoveRight()

    def MoveTo(self, line, index):
        self.selectedIndex = index
        self.selectedLine = line
        self._ClampSelector()

    def MoveUp(self, amount=1):
        self.MoveDown(-amount)

    def MoveDown(self, amount=1):
        self.selectedLine += amount
        self._ClampSelector()

    def MoveLeft(self, amount=1):
        self.MoveRight(-amount)

    def MoveRight(self, amount=1):
        self.selectedIndex += amount
        self._WrapAroundSelector()

    def GetLine(self, line):
        if self.selectedLine == line:
            return self.text[line][:self.selectedIndex] + '|' + self.text[line][self.selectedIndex:]
        else:
            return self.text[line]

    def _WrapAroundSelector(self):
        self.selectedLine, self.selectedIndex = self.text.wrapAroundSelector(self.selectedLine, self.selectedIndex)

    def _ClampSelector(self):
        self.selectedLine, self.selectedIndex = self.text.clampSelector(self.selectedLine, self.selectedIndex)

    def Lines(self, showSelector=False):
        if showSelector:
            return self.text[:self.selectedLine] + [self.GetLine(self.selectedLine)] + self.text[self.selectedLine + 1:]
        return self.text


import pygame
pygame.font.init()


class RenderText:
    def __init__(self, height=50, color=(255, 255, 255)):
        self.height = height
        self.font = pygame.font.SysFont('consolas', self.height)
        self.color = color

    def RenderLines(self, text: Text):
        # surface.fill((100, 0, 0))
        height = 0
        width = 0
        out = []
        for i in range(len(text)):
            s = self.font.render(text[i], False, self.color)
            out.append((s, (0, height)))
            height += self.height
            width = max(width, s.get_width())
        surface = pygame.Surface(
            (width, height), flags=pygame.SRCALPHA)
        surface.blits(out)
        return surface

    # def BlitTo(self, destination):
    #     self.surface.set_alpha(50 + 100 * self.opened)
    #     destination.blit(self.surface, (0, 0))

    def Render(self, text: 'str|Text', wrap=0):
        if wrap:
            return self.RenderLines(Text(text).lineWrap(wrap))
        return self.RenderLines(Text(text))


class Chat:
    def __init__(self):
        self.text = Text()
        pass
    pass


class CommandConsole(TextEditor):  # not implemented
    def __init__(self, commands=None):
        self.text = ['']
        self.selectedLine = 0
        self.selectedIndex = 0
        self.commandBuffer = []
        if commands:
            self.commands = commands
        else:
            self.commands = {}

    def Parse(self, store=True):
        return self.ParseLine(self.selectedLine, store)

    def ParseLine(self, line, store=True):
        text = self.text[line]
        if len(text) == 0:  # or text[0]!='/':
            return False
        words = text.split()
        # print(words)
        if words[0] in self.commands:
            if words[1].isnumeric():
                out = words[0], int(words[1])
                if store:
                    self.commandBuffer.append(out)
                return out

    def TakeCommandBuffer(self):
        a = self.commandBuffer.copy()
        self.commandBuffer.clear()
        return a
    pass


class CommandConsoleVisual:  # not implemented
    def __init__(self):
        self.console = CommandConsole()
        self.height = 50
        self.font = pygame.font.Font(None, self.height)
        self.opened = True
        self.RefreshSurface()

    def RefreshSurface(self):
        self.surface = pygame.Surface(
            (600, self.height * (len(self.console.text))))
        out = []
        color = (0, 0, 200)
        for i in range(len(self.console.text)):
            out.append((self.font.render(self.console.GetLine(i), False, color), (0, i * self.height)))
        self.surface.blits(out)

    def BlitTo(self, destination):
        self.surface.set_alpha(50 + 100 * self.opened)
        destination.blit(self.surface, (0, 0))

    def KeydownEvent(self, event):
        key = event.__dict__['key']
        if key == pygame.K_PAUSE:  # pause
            if self.opened:
                self.Close()
            else:
                self.Open()
        elif self.opened:
            self.Write(event)
        self.RefreshSurface()

    def Open(self):
        self.opened = True
        # self.console.Enter()
        return

    def Close(self):
        self.opened = False
        # self.console.Parse()
        return

    def IsLocking(self):
        return self.opened

    def Write(self, event):
        # print(event)
        letter = event.__dict__['unicode']
        key = event.__dict__['key']
        mod = event.__dict__['mod']
        if key == pygame.K_ESCAPE:
            self.Close()
            return
        if key == pygame.K_BACKSPACE:
            self.console.Backspace()
            return
        if key == pygame.K_RETURN:
            if mod & pygame.KMOD_SHIFT:
                a = self.console.Parse(True)
            else:
                self.console.Enter()
            return
        a = {pygame.K_UP: self.console.MoveUp, pygame.K_RIGHT: self.console.MoveRight,
             pygame.K_DOWN: self.console.MoveDown, pygame.K_LEFT: self.console.MoveLeft}
        if key in a:
            a[key]()
        if letter:
            self.console.TypeText(letter)
            # self.text[-1]+=letter

    def TakeCommandBuffer(self):
        return self.console.TakeCommandBuffer()


class CommandArgument:  # not implemented
    # INT,BOOL,STR,VEC,OPT=range(5)
    def __init__(self, argType, name):
        self.argType = argType

    @staticmethod
    def INT(name):
        return CommandArgument(0, name)

    @staticmethod
    def BOOL(name):
        return CommandArgument(1, name)

    @staticmethod
    def STR(name):
        return CommandArgument(2, name)

    @staticmethod
    def VEC(name):
        return CommandArgument(3, name)

    @staticmethod
    def OPT(name):
        return CommandArgument(4, name)

    @staticmethod
    def AsType(argumentType, argument):
        ca = CommandArgument
        return (ca.AsInt, ca.AsBool, ca.AsStr, ca.AsVec)[argumentType](argument)

    @staticmethod
    def AsInt(argument: str):
        try:
            return int(argument)
        except:
            return

    @staticmethod
    def AsBool(argument: str):
        if argument in ('true', '1'):
            return True
        elif argument in ('false', '0'):
            return False
        else:
            return

    @staticmethod
    def AsStr(argument: str):
        return argument

    @staticmethod
    def AsVec(argument: str):
        a = argument.split(',')
        if len(a) == 2:
            try:
                return int(a[0]), int(a[1])
            except:
                return
        else:
            return

    @staticmethod
    def Parse(command: str, options):
        arguments = command.split()
        path = options
        i = 0
        while arguments[i] in path:
            path = path[arguments[i]]
        return


if __name__ == '__main__':
    ca = CommandArgument
    a = {
        'setspeed': ('frequency', ca.INT),
        'setwave': (('position', ca.VEC), ('direction', ca.INT), ('on/off', ca.BOOL)),
        'preset': {
            'copy': (('from', ca.VEC), ('to', ca.VEC), ('name', ca.STR)),
            'paste': (('at', ca.VEC), ('rotated', ca.INT), ('name', ca.STR))
        },
    }

    b = {
        ca.OPT('setspeed'): {
            ca.INT('frequency')
        },
        ca.OPT('setwave'): {

        },
        ca.OPT('preset'): {

        }
    }

    ca.OPT(
        'setspeed', ca.INT('frequency', ca.RUN())

    )
