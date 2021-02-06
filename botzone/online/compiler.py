config = dict(
    cpp = dict(
        suffix = 'cpp',
        images = ['botzone/env-full', 'botzone/env-cpp'],
        time_limit = 1000,
        sub_time_limit = 1000,
        memory_limit = 256,
        compile_command = 'g++ -D_BOTZONE_ONLINE -O2 -D_GLIBCXX_USE_CXX11_ABI=0 -Wall -mavx {code} -ljson -lpthread -o {target}',
        run_command = '{target}'
    ),
    cpp11 = dict(
        suffix = 'cpp',
        images = ['botzone/env-full', 'botzone/env-cpp'],
        time_limit = 1000,
        sub_time_limit = 1000,
        memory_limit = 256,
        compile_command = 'g++ -D_BOTZONE_ONLINE -D_GLIBCXX_USE_CXX11_ABI=0 -O2 -Wall -mavx -std=c++11 -x c++ {code} -ljson -lpthread -o {target}',
        run_command = '{target}'
    ),
    cpp17 = dict(
        suffix = 'cpp',
        images = ['botzone/env-full', 'botzone/env-cpp17a', 'botzone/env-cpp17'],
        time_limit = 1000,
        sub_time_limit = 1000,
        memory_limit = 256,
        compile_command = 'g++-7 -D_BOTZONE_ONLINE -D_GLIBCXX_USE_CXX11_ABI=0 -O2 -Wall -mavx -std=c++1z -x c++ {code} -ljson -lpthread -o {target}',
        run_command = '{target}'
    ),
    cpp17a = dict(
        suffix = 'cpp',
        images = ['botzone/env-full', 'botzone/env-cpp17a'],
        time_limit = 1000,
        sub_time_limit = 1000,
        memory_limit = 256,
        compile_command = 'g++-7 -D_BOTZONE_ONLINE -O2 -Wall -mavx -std=c++1z -I /usr/local/include/jsoncpp_cxx11abi -isystem /usr/local/include/tensorflow -isystem /usr/local/include/tensorflow/bazel-genfiles -isystem /usr/local/include/tensorflow/tensorflow/contrib/makefile/downloads -isystem /usr/local/include/tensorflow/tensorflow/contrib/makefile/downloads/eigen -isystem /usr/local/include/tensorflow/tensorflow/contrib/makefile/downloads/gemmlowp -isystem /usr/local/include/tensorflow/tensorflow/contrib/makefile/downloads/nsync/public -isystem /usr/local/include/tensorflow/tensorflow/contrib/makefile/gen/protobuf-host/include -isystem /usr/lib/libtorch/include -isystem /usr/lib/libtorch/include/torch/csrc/api/include -x c++ {code} -x none -rdynamic /usr/local/lib/tensorflow_cc/libtensorflow_cc.so -ldl -lpthread -lopenblas -ljsoncpp /usr/local/lib/tensorflow_cc/libprotobuf.a -lMahjongGB -Wl,-rpath,/usr/local/lib/tensorflow_cc -rdynamic /usr/lib/libtorch/lib/libtorch.so /usr/lib/libtorch/lib/libc10.so -Wl,--no-as-needed,/usr/lib/libtorch/lib/libtorch_cpu.so -Wl,--as-needed /usr/lib/libtorch/lib/libc10.so -lpthread -Wl,--no-as-needed,/usr/lib/libtorch/lib/libtorch.so -Wl,--as-needed -Wl,-rpath,/usr/lib/libtorch/lib -o {target}',
        run_command = '{target}'
    ),
    cppo0 = dict(
        suffix = 'cpp',
        images = ['botzone/env-full', 'botzone/env-cpp'],
        time_limit = 1000,
        sub_time_limit = 1000,
        memory_limit = 256,
        compile_command = 'g++ -D_BOTZONE_ONLINE -D_GLIBCXX_USE_CXX11_ABI=0 -x c++ -Wall -mavx {code} -ljson -lpthread -o {target}',
        run_command = '{target}'
    ),
    java = dict(
        suffix = 'java',
        images = ['botzone/env-full', 'botzone/env-java'],
        time_limit = 3000,
        sub_time_limit = 2000,
        memory_limit = 256,
        compile_command = 'javac -encoding utf-8 {code}',
        run_command = '/usr/bin/java Main'
    ),
    cs = dict(
        suffix = 'cs',
        images = ['botzone/env-full', 'botzone/env-cs'],
        time_limit = 6000,
        sub_time_limit = 4000,
        memory_limit = 256,
        compile_command = 'mcs -lib:/usr/lib/mono/Botzone -r:Newtonsoft.Json {code} -out:{target}',
        run_command = '/usr/bin/mono {target}'
    ),
    js = dict(
        suffix = 'js',
        images = ['botzone/env-full', 'botzone/env-js'],
        time_limit = 2000,
        sub_time_limit = 2000,
        memory_limit = 256,
        compile_command = None,
        run_command = '/usr/bin/nodejs {target}'
    ),
    py = dict(
        suffix = 'py',
        images = ['botzone/env-full', 'botzone/env-py'],
        time_limit = 6000,
        sub_time_limit = 4000,
        memory_limit = 256,
        compile_command = None,
        run_command = '/usr/bin/python {target}'
    ),
    py3 = dict(
        suffix = 'py',
        images = ['botzone/env-full', 'botzone/env-py3'],
        time_limit = 6000,
        sub_time_limit = 4000,
        memory_limit = 256,
        compile_command = None,
        run_command = '/usr/bin/python3 {target}'
    ),
    py36 = dict(
        suffix = 'py',
        images = ['botzone/env-py36'],
        time_limit = 6000,
        sub_time_limit = 4000,
        memory_limit = 256,
        compile_command = None,
        run_command = '/usr/bin/python3.6 {target}'
    ),
    pas = dict(
        suffix = 'pas',
        images = ['botzone/env-full', 'botzone/env-pas'],
        time_limit = 1000,
        sub_time_limit = 1000,
        memory_limit = 256,
        compile_command = 'fpc {code} -o{target}',
        run_command = '{target}'
    ),
    elfbin = dict(
        suffix = 'elfbin',
        images = ['botzone/env-full', 'botzone/env-cpp17a', 'botzone/env-cpp17', 'botzone/env-cpp'],
        time_limit = 1000,
        sub_time_limit = 1000,
        memory_limit = 256,
        compile_command = None,
        run_command = '{target}'
    )
)

from collections import defaultdict
images = defaultdict(list)
for ext in config:
    for image in config[ext]['images']:
        images[image].append(ext)