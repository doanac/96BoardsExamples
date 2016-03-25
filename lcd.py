# based on but modified to use libsoc:
#  https://github.com/youngage/grove-lcd
import time

from libsoc import I2C


class Backlight(I2C):
    def __init__(self, bus):
        super(Backlight, self).__init__(bus, 0x62)

    def open(self):
        super(Backlight, self).open()
        # initialize LCD
        self.write((0x0, 0x00))
        self.write((0x1, 0x00))
        self.write((0x8, 0xAA))  # enable PWM

    def close(self):
        self.write((0x08, 0))
        super(Backlight, self).close()

    def set_RGB(self, r, g, b):
        self.write((0x2, b))
        self.write((0x3, g))
        self.write((0x4, r))


class Screen(I2C):
    # commands
    LCD_CLEARDISPLAY = 0x01
    LCD_RETURNHOME = 0x02
    LCD_ENTRYMODESET = 0x04
    LCD_DISPLAYCONTROL = 0x08
    LCD_CURSORSHIFT = 0x10
    LCD_FUNCTIONSET = 0x20
    LCD_SETCGRAMADDR = 0x40
    LCD_SETDDRAMADDR = 0x80

    # flags for display entry mode
    LCD_ENTRYRIGHT = 0x00
    LCD_ENTRYLEFT = 0x02
    LCD_ENTRYSHIFTINCREMENT = 0x01
    LCD_ENTRYSHIFTDECREMENT = 0x00

    # flags for display on/off control
    LCD_DISPLAYON = 0x04
    LCD_DISPLAYOFF = 0x00
    LCD_CURSORON = 0x02
    LCD_CURSOROFF = 0x00
    LCD_BLINKON = 0x01
    LCD_BLINKOFF = 0x00

    # flags for display/cursor shift
    LCD_DISPLAYMOVE = 0x08
    LCD_CURSORMOVE = 0x00
    LCD_MOVERIGHT = 0x04
    LCD_MOVELEFT = 0x00

    # flags for function set
    LCD_8BITMODE = 0x10
    LCD_4BITMODE = 0x00
    LCD_2LINE = 0x08
    LCD_1LINE = 0x00
    LCD_5x10DOTS = 0x04
    LCD_5x8DOTS = 0x00

    def __init__(self, bus, oneline=False):
        super(Screen, self).__init__(bus, 0x3e)
        self.oneline = oneline

    def open(self):
        super(Screen, self).open()

        # wait for display init after power-on
        time.sleep(0.050)

        disp_func = Screen.LCD_DISPLAYON
        if not self.oneline:
            disp_func |= self.LCD_2LINE

        # send function set
        self.cmd(Screen.LCD_FUNCTIONSET | disp_func)
        time.sleep(0.005)
        self.cmd(Screen.LCD_FUNCTIONSET | disp_func)
        time.sleep(0.001)
        self.cmd(Screen.LCD_FUNCTIONSET | disp_func)
        self.cmd(Screen.LCD_FUNCTIONSET | disp_func)

        # turn on the display
        self.disp_ctrl = (
            Screen.LCD_DISPLAYON | Screen.LCD_CURSOROFF | Screen.LCD_BLINKOFF)
        self.display()

        # clear it
        self.clear()

        # set default text direction (left-to-right)
        disp_mode = Screen.LCD_ENTRYLEFT | Screen.LCD_ENTRYSHIFTDECREMENT
        self.cmd(Screen.LCD_ENTRYMODESET | disp_mode)

    def close(self):
        self.clear()
        super(Screen, self).close()

    def cmd(self, command):
        assert command >= 0 and command < 256
        self.write((0x80, command))

    def write_char(self, c):
        assert c >= 0 and c < 256
        self.write((0x40, c))

    def write_string(self, text):
        for char in text:
            self.write_char(ord(char))

    def display(self):
        self.disp_ctrl |= Screen.LCD_DISPLAYON
        self.cmd(Screen.LCD_DISPLAYCONTROL | self.disp_ctrl)

    def nodisplay(self):
        self.disp_ctrl &= ~Screen.LCD_DISPLAYON
        self.cmd(Screen.LCD_DISPLAYCONTROL | self.disp_ctrl)

    def clear(self):
        self.cmd(Screen.LCD_CLEARDISPLAY)
        time.sleep(0.002)  # 2ms

    def home(self):
        self.cmd(Screen.LCD_RETURNHOME)
        time.sleep(0.002)  # 2ms

    def set_cursor(self, col, row):
        col = (col | 0x80) if row == 0 else (col | 0xc0)
        self.cmd(col)


class LCD:
    def __init__(self, bus, oneline=False):
        self.backlight = Backlight(bus)
        self.screen = Screen(bus, oneline)

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def open(self):
        self.backlight.open()
        self.screen.open()

    def close(self):
        self.screen.close()
        self.backlight.close()


if __name__ == '__main__':
    with LCD(0) as lcd:
        lcd.backlight.set_RGB(0xFF, 0, 0)  # red background
        lcd.screen.write_string('hello')
        lcd.screen.set_cursor(1, 2)
        lcd.screen.write_string('world')
        time.sleep(4)
