#!/usr/bin/env pyven

import tempfile, subprocess, os, sys, aridity

studiodir = os.path.dirname(os.path.realpath(__file__))

def projectconfpath(args):
    projectconfname = 'studioproject.arid'
    if args:
        projectdir, = args
        return os.path.join(os.path.abspath(projectdir), projectconfname)
    elif os.path.exists(projectconfname):
        return os.path.abspath(projectconfname)
    else:
        return os.path.join(studiodir, projectconfname)

def main():
    projectconf = projectconfpath(sys.argv[1:])
    configdir = os.path.join(os.path.expanduser('~'), '.tidalstudio')
    os.makedirs(configdir, exist_ok = True)
    with tempfile.TemporaryDirectory(dir = configdir) as tempdir:
        vimrc = os.path.join(tempdir, 'vimrc')
        sendblock = os.path.join(tempdir, 'sendblock.py')
        screenrc = os.path.join(tempdir, 'screenrc')
        context = aridity.Context()
        with aridity.Repl(context) as repl:
            printf = repl.printf
            printf("cd %s", studiodir)
            printf('. tidalstudio.arid')
            printf('tidalstudio')
            printf("\tvimrcPath = %s", vimrc)
            printf("\tsendblock = %s", sendblock)
            printf("\t. %s", projectconf)
            printf("redirect %s", vimrc)
            printf('tidalstudio < vimrc.aridt')
            printf("redirect %s", sendblock)
            printf('" = $(pystr)')
            printf('tidalstudio < sendblock.py.aridt')
            printf("redirect %s", screenrc)
            printf('" = $(screenstr)')
            printf('tidalstudio < screenrc.aridt')
        subprocess.check_call(['screen', '-S', context.resolved('tidalstudio', 'sessionName').value, '-c', screenrc])

if '__main__' == __name__:
    main()
