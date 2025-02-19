import numpy as np
from scipy.stats import truncnorm


#------ 사용자 설정값 ------
n_samples = 2000 #재활용 데이터 개수
n_layers = 25 #레이어 개수

elastic = [130000, 70000, 0.25, 5000, 5000, 5000] #길이: 6
failstress = [1300, -1000, 40, -100, 100, 0, 0] #길이: 7
failstrain = [0.015, -0.01, 0.005, -0.01, 0.01] #길이: 5

pattern_angle = np.array([0, 45, 90, 135]) #이런 패턴 순으로 지정.

#정상 물성치 분포 설정
mean_drop = 0.08 #평균 성능 하락률
std_drop = 0.01 #표준편차
lower = 0.06 #성능 최소 하락률
upper = 0.10 #성능 최대 하락률



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

print("names shape:", names.shape)
print("original shape:", original.shape)
print("recycled shape:", recycled.shape)



#---------- original, recycled 합친 후 csv 저장 ----------
data = np.concatenate((names, original, recycled), axis = 0) #1행에 original, 2행부터 recycled data

np.savetxt("recycled_parameter.csv", data, delimiter=",", fmt = "%s")
