import numpy as np
import subprocess
import time

from data import manage_data as md #내가 생성한 패키지



#사용자 세팅 값에서 n_iteration하고 n_samples 가져오기
setting_values = md.read_csv("setting.csv")
n_iteration = int(setting_values[0][1]) + 1 #n_sample 값에서 original 값 1 추가해서
n_layers = int(setting_values[1][1])

#n_iteration = 3 #이건 시험용으로 코드를 진행할 때, setting값과 무관하게 n_iteration 변경할 수 있음.

#setting.csv의 기본 세팅값들을 토대로 시험 데이터 생성
setting_filename = "setting.csv"
data_pa = md.crt_pa(setting_filename) #데이터 list로 출력됨.



#------time------
# 전체 실제 반복 횟수
total_iterations = n_iteration
# 시작 시간 기록
start_time = time.time()
completed_iterations = 0  # 실제 수행한 반복 횟수 카운트



for i in range(n_iteration):

    iteration_start = time.time() # 각 반복 시작 시각
    completed_iterations += 1 # 실제 수행한 반복 횟수 업데이트

    parameter = np.atleast_2d(data_pa[i]) #i행의 데이터 선정, 2차원 numpy 배열으로 변경.
    
    md.save_pkl(parameter, "data/parameter.pkl") #.pkl로 데이터 저장 

    subprocess.run("abaqus cae noGUI=abaqus/script.py", shell=True, encoding="utf-8") #abaqus를 CLI 환경에서 실행.
    #창을 띄우기 위해서는 "noGUI"를 "script"로 변경.
    #현재 버전에서는 40번 라인에서 아래의 error가 발생. 
    #abaqus 프로세스의 종료 과정에서 발생하는 것으로 예상.

    """
    *** Error: ABQcaeK.exe / rank 0 / thread 0  encountered a system exception 0xC0000005 (EXCEPTION_ACCESS_VIOLATION)

    *** ERROR CATEGORY:  CAE

    Abaqus Error: cae exited with an error.
    """

    # 진행 상황 및 시간 계산
    iteration_time = time.time() - iteration_start              # 이번 반복 소요 시간
    elapsed_time = time.time() - start_time                        # 전체 경과 시간
    average_time = elapsed_time / completed_iterations             # 평균 반복 소요 시간
    remaining_iterations = total_iterations - completed_iterations   # 남은 반복 횟수
    estimated_remaining = average_time * remaining_iterations        # 예상 남은 시간 (초 단위)
    progress_percent = (completed_iterations / total_iterations) * 100
    print("\nProgress: {:.2f}% ({} / {} iterations completed)".format(progress_percent, completed_iterations, total_iterations))
    print("Iteration time: {:.2f}sec\nElapsed time: {:.2f}sec\nRemaining time: {:.2f}min".format(iteration_time, elapsed_time, estimated_remaining/60))
    print("-" * 50)
    

print("종료!")