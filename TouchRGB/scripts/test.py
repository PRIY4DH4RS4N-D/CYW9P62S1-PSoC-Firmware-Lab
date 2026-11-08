"""Compile and execute the real portable firmware modules with native GCC."""
import os, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
build = ROOT / 'build'
build.mkdir(exist_ok=True)
cmd = [os.environ.get('CC', 'gcc'), '-std=c11', '-Wall', '-Wextra', '-Werror', '-pedantic',
       '-DTOUCHRGB_HOST', '-Ifirmware', 'tests/native.c', 'firmware/color_engine.c',
       'firmware/capsense_input.c', 'firmware/touch_controller.c', '-lm', '-o', 'build/native_tests.exe']
subprocess.run(cmd, cwd=ROOT, check=True)
result = subprocess.run([str(build/'native_tests.exe')], cwd=ROOT, text=True, capture_output=True)
print(result.stdout, end='')
print(result.stderr, end='')
log = result.stdout+result.stderr
if not result.returncode:
    subprocess.run([os.environ.get('CC', 'gcc'), '-std=c11', '-Wall', '-Wextra', '-Werror',
                    '-Itests/stubs', '-Ifirmware', 'tests/output_driver.c', 'firmware/rgb_output.c',
                    '-o', 'build/output_tests.exe'], cwd=ROOT, check=True)
    result = subprocess.run([str(build/'output_tests.exe')], cwd=ROOT, text=True, capture_output=True)
    print(result.stdout+result.stderr, end='')
    log += result.stdout+result.stderr
(build/'software-tests.log').write_text(log)
raise SystemExit(result.returncode)
