import csv
import pickle
import json
import numpy as np
from scipy.stats import truncnorm

def crt_pa(filename): #list로 생성함!
    with open(filename, newline='') as csvfile: #csv 파일 열기
        reader = list(csv.reader(csvfile))

    # CSV 파일 순서에 맞게 직접 변수에 저장
    n_samples = int(reader[0][1])
    n_layers = int(reader[1][1])
    elastic = [float(x) for x in reader[2][1:]]
    failstress = [float(x) for x in reader[3][1:]]
    failstrain = [float(x) for x in reader[4][1:]]
    pattern_angle = [float(x) for x in reader[5][1:]]
    mean_drop = float(reader[6][1])
    std_drop = float(reader[7][1])
    lower = float(reader[8][1])
    upper = float(reader[9][1])


    #---------- 정상 데이터 생성 ----------
    #정상 물성치
    for i in range(n_layers):
        if i == 0:
            pattern_property = elastic + failstress + failstrain
            property_original = pattern_property
            continue
        property_original = property_original+ pattern_property

    #정상 각도
    angle_original = np.tile(pattern_angle, (n_layers // len(pattern_angle) + 1))[:n_layers]# 패턴을 충분히 반복한 뒤 원하는 길이만큼 자르기

    #정상 데이터
    original = np.concatenate((property_original, angle_original)) #합치기, 순서: layer_1, layer_2, ..., layer_n, angle_1, angle_2, ..., angle_n
    original = original.reshape(1, -1) #2차원 데이터로 변경



    #---------- random property, angles 생성 ----------
    #표준정규분포를 [a, b 구간으로 변환]
    a = (lower - mean_drop) / std_drop
    b = (upper - mean_drop) / std_drop

    for i in range(1, n_layers+1): 
        per = (1 - truncnorm.rvs(a, b, loc=mean_drop, scale=std_drop, size = n_samples))[:, np.newaxis]
        prop_rec = per * pattern_property
        if i == 1:
            prop_rec_tot = prop_rec
            continue

        prop_rec_tot = np.concatenate((prop_rec_tot, prop_rec), axis=1)

    #레이어 별 각도 생성
    angl_rec = np.random.uniform(low=0, high=180, size=(n_samples, n_layers))

    #물성치, 각도 합치기
    recycled = np.concatenate((prop_rec_tot, angl_rec), axis = 1)


    """
    #데이터 첫 행에 이름이 필요하다면 주석처리 된 코드 사용
    #---------- 데이터 이름 생성(첫 행에 들어갈 것들임) ----------
    property_basic_names = [
        "E1", "E2", "Nu12", "G12", "G13", "G23",
        "Ten Stress Fiber Dir", "Com Stress Fiber Dir", "Ten Stress Transv Dir", "Com Stress Transv Dir", "Shear Strength", "Cross-Prod Term Coeff", "Stress Limit",
        "Ten Strain Fiber Dir", "Com Strain Fiber Dir", "Ten Strain Transv Dir", "Com Strain Transv Dir", "Shear Strain",
    ]
    angle_basic_name = ["angle"]

    for i in range(1, n_layers+1):
        if i == 1:
            property_names = [
                "E1_1", "E2_1", "Nu12_1", "G12_1", "G13_1", "G23_1",
                "Ten Stress Fiber Dir_1", "Com Stress Fiber Dir_1", "Ten Stress Transv Dir_1", "Com Stress Transv Dir_1", "Shear Strength_1", "Cross-Prod Term Coeff_1", "Stress Limit_1",
                "Ten Strain Fiber Dir_1", "Com Strain Fiber Dir_1", "Ten Strain Transv Dir_1", "Com Strain Transv Dir_1", "Shear Strain_1",
            ]
            angle_names = ["angle_1"]
            continue


        property_elements_with_suffix = [f"{elem}_{i}" for elem in property_basic_names] #property 뒤에 _{i} 붙이기
        property_names = property_names + property_elements_with_suffix #합치기
        
        angle_elements_with_suffix = [f"{elem}_{i}" for elem in angle_basic_name] #angle 뒤에 _{i} 붙이기
        angle_names = angle_names + angle_elements_with_suffix #합치기

    names = property_names + angle_names #합치기
    names = np.array(names) #데이터 이름 생성 완성
    names = names.reshape(1, -1) #2차원 데이터로 변경
    """

    #---------- original, recycled 합친 후 return ----------
    data = list(np.concatenate((original, recycled), axis = 0)) #1행에 original, 2행부터 recycled data

    print("random parameter data shape:", len(data))
    print("random parameter data type:", type(data))

    return data



#.csv 관련 함수들
def save_csv (data, name): #data를 name이라는 이름으로 csv 파일 생성
    np.savetxt(name, data, delimiter=",", fmt = "%s")

def read_csv(name):
    with open(name, newline='') as csvfile: #csv 파일 열기
        loaded_data = list(csv.reader(csvfile))
    return loaded_data



#.pkl 관련 함수들
def save_pkl (data, name): #data를 name이라는 이름으로 pkl 파일 생성
    with open(name, "wb") as f:
        pickle.dump(data, f)

def read_pkl (name): #.pkl 읽어오기
    with open (name, "rb") as f:
        loaded_data = pickle.load(f)
    return loaded_data



#.json 관련 함수들들
def save_json (data, name): #data를 name이라는 이름으로 json 파일 생성
    with open(name, "w") as f:
        json.dump(data, f, indent=2) #indent: 들여쓰기

def read_json (name): #.json 불러오기
    with open(name, "r") as f:
        loaded_data = json.load(f)
    return loaded_data