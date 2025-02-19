import subprocess
import os

# 현재 스크립트의 절대 경로를 가져옵니다.
script_path = os.path.dirname(__file__)
print(script_path)

script = script_path + "\\auto_iteration.py"
print(script)

cmd = f"abaqus cae noGUI={script}"
subprocess.run("abaqus cae", shell=True)