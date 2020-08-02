# Copyright 2019 Andrzej Cichocki

# This file is part of Concern.
#
# Concern is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Concern is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Concern.  If not, see <http://www.gnu.org/licenses/>.

from . import templates
from .initlogging import logging
from argparse import ArgumentParser
from aridity.config import Config
from aridity.model import Number
from importlib import import_module
from pathlib import Path
from pkg_resources import resource_filename
from screen import stuffablescreen
from tempfile import TemporaryDirectory
from termios import TIOCGWINSZ
import fcntl, os, struct, sys

log = logging.getLogger(__name__)

def toabswidth(context, resolvable):
    winsize = 'HHHH'
    ws_col = struct.unpack(winsize, fcntl.ioctl(sys.stdin, TIOCGWINSZ, bytes(struct.calcsize(winsize))))[1]
    return Number(round(resolvable.resolve(context).value * (ws_col - 1))) # Take off 1 for the separator.

def main_Concern():
    parser = ArgumentParser()
    parser.add_argument('--chdir', type = os.path.expanduser)
    config, vimargs = parser.parse_known_args()
    if config.chdir is not None:
        os.chdir(config.chdir)
    configdir = Path.home() / '.Concern'
    configdir.mkdir(parents = True, exist_ok = True)
    with TemporaryDirectory(dir = configdir) as tempdir:
        tempdir = Path(tempdir)
        concernvimrc = tempdir / 'vimrc'
        sendblock = tempdir / 'sendblock.py'
        quit = tempdir / 'quit.py'
        screenrc = tempdir / 'screenrc'
        config = Config.blank()
        config.put('Concern', 'toAbsWidth', function = toabswidth)
        with config.repl() as repl:
            printf = repl.printf
            printf(". %s", resource_filename(__name__, 'Concern.arid'))
            settings = Path.home() / '.settings.arid'
            if settings.exists():
                printf(". %s", settings)
            else:
                log.info("No such file: %s", settings)
            uservimrc = Path.home() / '.vimrc'
            if uservimrc.exists():
                printf("vimrc userPath = %s", uservimrc)
            else:
                log.info("No such file: %s", uservimrc)
            printf('Concern')
            printf("\tinterpreter = %s", sys.executable)
            printf("\tvimrcPath = %s", concernvimrc)
            printf("\tsendblock = %s", sendblock)
            printf("\tquit = %s", quit)
            printf('\tvimArgs := $list()')
            for arg in vimargs:
                printf("\tvimArgs += %s", arg)
        import_module(f".consumer.{config.Concern.consumerName}", package = __package__).configure(config)
        with config.repl() as repl:
            printf = repl.printf
            printf("redirect %s", concernvimrc)
            printf("Concern < %s", resource_filename(templates.__name__, 'vimrc.aridt'))
            printf('" = $(pystr)')
            printf("redirect %s", sendblock)
            printf("Concern < %s", resource_filename(templates.__name__, 'sendblock.py.aridt'))
            printf("redirect %s", quit)
            printf("Concern < %s", resource_filename(templates.__name__, 'quit.py.aridt'))
            printf('" = $(screenstr)')
            printf("redirect %s", screenrc)
            printf("Concern < %s", resource_filename(templates.__name__, 'screenrc.aridt'))
        doublequotekey = config.Concern.doubleQuoteKey
        stuffablescreen(doublequotekey).print('-S', config.Concern.sessionName, '-c', screenrc)
