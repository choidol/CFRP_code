import numpy as np
import subprocess
import time

from data import manage_data as md #내가 생성한 패키지



#사용자 세팅 값에서 n_iteration하고 n_samples 가져오기
setting_values = md.read_csv("setting.csv")
n_iteration = int(setting_values[0][1]) + 1 #n_sample 값에서 original 값 1 추가가해서
n_iteration = 1
n_layers = int(setting_values[1][1])



#setting.csv의 기본 세팅값들을 토대로 시험 데이터 생성
setting_filename = "setting.csv"
data_pa = np.array(md.crt_pa(setting_filename))



#------time------
# 전체 실제 반복 횟수
total_iterations = n_iteration
# 시작 시간 기록
start_time = time.time()
completed_iterations = 0  # 실제 수행한 반복 횟수 카운트



for i in range(n_iteration):

    iteration_start = time.time() # 각 반복 시작 시각
    completed_iterations += 1 # 실제 수행한 반복 횟수 업데이트

    parameter = data_pa[i] #i행의 데이터 선정
    md.save_pkl(parameter, "data/parameter.pkl") #.pkl로 i행의 데이터 저장 

    subprocess.run("abaqus cae script=abaqus/script.py", shell=True, encoding="utf-8")

    # 진행 상황 및 시간 계산
    iteration_time = time.time() - iteration_start              # 이번 반복 소요 시간
    elapsed_time = time.time() - start_time                        # 전체 경과 시간
    average_time = elapsed_time / completed_iterations             # 평균 반복 소요 시간
    remaining_iterations = total_iterations - completed_iterations   # 남은 반복 횟수
    estimated_remaining = average_time * remaining_iterations        # 예상 남은 시간 (초 단위)
    progress_percent = (completed_iterations / total_iterations) * 100

print("종료!")