import os
import sys
import os.path

from distutils import errors
from jcc import cpp

TIKA_VERSION = '1.8'
OSGI_VERSION = '5.0.0'

TIKA_APP = "tika-app-%s.jar" %(TIKA_VERSION)
TIKA_CORE = "tika-core-%s.jar" %(TIKA_VERSION)
TIKA_PARSERS = "tika-parsers-%s.jar" %(TIKA_VERSION)
OSGI = "org.osgi.core-%s.jar" %(OSGI_VERSION)
OSGI_COMPENDIUM = "org.osgi.compendium-%s.jar" %(OSGI_VERSION)

deps =  {
    "osgi_core": OSGI,
    "osgi_compendium": OSGI_COMPENDIUM,
    "tika_app": TIKA_APP,
    "tika_core": TIKA_CORE,
    "tika_parsers": TIKA_PARSERS,
    "jcc": "jcc"
    }

def check_deps(required, found):
    satisfied = True
    for r in required:
        if r not in found:
            satisfied = False
            print "%s not found!" % (required[r])
    return satisfied


def find_deps(required):
    classpath = [x for x in os.environ.get("CLASSPATH", "").split(":") if x] + ["lib", "win", os.getcwdu()]
    path = sys.path + ["lib", "win"]
    found = {}
    def __probe(paths):
        for p in paths:
            for j in required:
                joined = os.path.join(p, deps[j])
                if os.path.exists(joined) and not j in found:
                    found[j] = joined

    __probe(classpath)
    __probe(path)
    return found


def get_jcc_args(jcc_path):
    jcc_options = {
        'include': (found['tika_app'], found['osgi_core'],  found['osgi_compendium'] ),
        'package': ('org.xml.sax'),
        'jar': (found['tika_core'],found['tika_parsers'],),
        'python': 'tika',
        'version': TIKA_VERSION,
        'module': 'tika_parser',
        'reserved': ('asm',),
        'classes': ('java.io.File', 'java.io.FileInputStream', 'java.io.ByteArrayInputStream', 'java.io.StringBufferInputStream'),
        }
    jcc_args = [os.path.join(jcc_path, 'nonexistent-argv-0')]
    setup_args = []
    egg_info_mode = False
    maxheap = '64m'
    for k, v in jcc_options.iteritems():
        if k in ['classes']:
            jcc_args.extend(v)
        elif hasattr(v, '__iter__'):
            for value in v:
                jcc_args.append('--%s' % k)
                jcc_args.append(value)
        else:
            jcc_args.append('--%s' % k)
            jcc_args.append(v)

    for arg in sys.argv[1:]:
        if arg == 'install':
            jcc_args.append('--install')
        elif arg == 'build':
            jcc_args.append('--build')
        elif arg == '-c':
            pass
        elif arg == 'egg_info':
            jcc_args.append('--egg-info')
        elif arg == '--vmarg':
            jcc_args.append(arg)
            i += 1
            jcc_args.append(sys.argv[i])
        elif arg == '--maxheap':
            i += 1
            maxheap = sys.argv[i]
        else:
            setup_args.append(arg)

    for extra_arg in setup_args:
        jcc_args.append('--extra-setup-arg')
        jcc_args.append(extra_arg)

    jcc_args.extend(['--maxheap', maxheap])
    return jcc_args


found = find_deps(deps)
if not check_deps(deps, found):
    raise errors.DistutilsFileError("Dependencies not satisfied. Run 'sh deps.sh' (you will need maven installed)")
jcc_args = get_jcc_args(found["jcc"])
cpp.jcc(jcc_args)
