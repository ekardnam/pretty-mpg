#!/usr/bin/env python3
from argparse import ArgumentParser
from glob import glob
from os.path import basename
from random import choice
from select import select
from subprocess import Popen, DEVNULL, PIPE
from sys import stdout, stdin
from termios import tcsetattr, tcgetattr, TCSADRAIN
from tty import setcbreak

def set_term_title(title):
    stdout.write(f'\x1b]2;{title}\x07')

def send_notify(text):
    Popen(['notify-send', text]).wait()

def main(folder):
    set_term_title(f'Playing {basename(folder)}')

    original_settings = tcgetattr(stdin)
    # set terminal raw mode
    setcbreak(stdin)
    files = glob(f'{folder}/*.mp3')
    try:
        while True:
            file = choice(files)
            print(f'[+] Playing {file}')
            send_notify(f'Playing {basename(file)}')
            proc = Popen(['/usr/bin/mpg123', '-q', file], stdout=DEVNULL, stderr=DEVNULL, stdin=PIPE)
            while proc.poll() is None:
                tuple = select([stdin], [], [], 1)
                for i in tuple[0]:
                    if i == stdin:
                        cmd = i.read(1)
                        if cmd == 'n':
                            print('[+] Switching song')
                            proc.kill()
                        elif cmd == chr(27): #esc
                            raise KeyboardInterrupt()
    except KeyboardInterrupt:
        print('[+] Quitting')
    finally:
        tcsetattr(stdin, TCSADRAIN, original_settings)
        if proc is not None and proc.poll() is None:
            proc.kill()

if __name__ == '__main__':
    parser = ArgumentParser(description='pretty-mpg.py - Shuffle MP3 using mpg123')
    parser._action_groups.pop()
    required_named_args = parser.add_argument_group('required arguments')
    required_named_args.add_argument('--playlist', help='folder containing MP3 to be shuffled', required=True)
    args = parser.parse_args()
    main(args.playlist)
