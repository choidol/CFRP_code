# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *
import __main__

import numpy as np
import time
import os

from data import manage_data as md

import section
import regionToolset
import displayGroupMdbToolset as dgm
import part
import material
import assembly
import optimization
import step
import interaction
import load
import mesh
import job
import sketch
import visualization
import xyPlot
import displayGroupOdbToolset as dgo
import connectorBehavior

#.pkl 파일 가져오기
data_p = md.read_pkl("data/parameter.pkl")

#layer 개수를 데이터에서 자동으로 확인
col_count = data_p.shape[1] #데이터에서 열 개수 가져옴
n_layer = int(col_count/19) #정수형으로 layer 개수 확인

#데이터에서 데이터 수량 확인 후, n_iteration 결정
n_iteration = data_p.shape[0] 
n_iteration = 3 #iteration 할 숫자에서 1 더해야 함. 만약에 필요 없다면, 그냥 주석처리 하면 됨.



#------Part------
#Generate Part
s = mdb.models['Model-1'].ConstrainedSketch(name='__profile__', 
    sheetSize=200.0)
g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
s.setPrimaryObject(option=STANDALONE)
session.viewports['Viewport: 1'].view.setValues(nearPlane=177.16, 
    farPlane=199.964, cameraPosition=(41.9904, 22.7052, 188.562), 
    cameraTarget=(41.9904, 22.7052, 0))
session.viewports['Viewport: 1'].view.setValues(cameraPosition=(52.2776, 
    43.8088, 188.562), cameraTarget=(52.2776, 43.8088, 0))
s.rectangle(point1=(0.0, 0.0), point2=(100.0, 50.0))
p = mdb.models['Model-1'].Part(name='Part-1', dimensionality=THREE_D, type=DEFORMABLE_BODY)
p = mdb.models['Model-1'].parts['Part-1']
p.BaseShell(sketch=s)
s.unsetPrimaryObject()
p = mdb.models['Model-1'].parts['Part-1']
session.viewports['Viewport: 1'].setValues(displayedObject=p)
del mdb.models['Model-1'].sketches['__profile__']



#------Assembly------
#Create Instance
a = mdb.models['Model-1'].rootAssembly
a.DatumCsysByDefault(CARTESIAN)
p = mdb.models['Model-1'].parts['Part-1']
a.Instance(name='Part-1-1', part=p, dependent=OFF)



#-------Step-------
#Create Step
mdb.models['Model-1'].StaticStep(name='Step-1', previous='Initial', 
    initialInc=0.1)
session.viewports['Viewport: 1'].assemblyDisplay.setValues(step='Step-1')



#-------Load-------
#Create Load
a = mdb.models['Model-1'].rootAssembly
s1 = a.instances['Part-1-1'].edges
side1Edges1 = s1.getSequenceFromMask(mask=('[#2 ]', ), )
region = a.Surface(side1Edges=side1Edges1, name='Surf-1')
mdb.models['Model-1'].ShellEdgeLoad(name='Load-1', createStepName='Step-1', 
    region=region, magnitude=100.0, distributionType=UNIFORM, field='', 
    localCsys=None, traction=TRANSVERSE)

#Create Boundary Condition
a = mdb.models['Model-1'].rootAssembly
e1 = a.instances['Part-1-1'].edges
edges1 = e1.getSequenceFromMask(mask=('[#8 ]', ), )
region = a.Set(edges=edges1, name='Set-1')
mdb.models['Model-1'].EncastreBC(name='BC-1', createStepName='Step-1', 
    region=region, localCsys=None)



#-------Mesh-------
#Global Seeds
a = mdb.models['Model-1'].rootAssembly
partInstances =(a.instances['Part-1-1'], )
a.seedPartInstance(regions=partInstances, size=8.0, deviationFactor=0.1, 
    minSizeFactor=0.1)

#Mesh Part Instance
a = mdb.models['Model-1'].rootAssembly
partInstances =(a.instances['Part-1-1'], )
a.generateMesh(regions=partInstances)



#------Field Output Requests------
a = mdb.models['Model-1'].rootAssembly
a.regenerate()
session.viewports['Viewport: 1'].setValues(displayedObject=a)
mdb.models['Model-1'].FieldOutputRequest(name='F-Output-2', 
    createStepName='Step-1', variables=('S', 'E', 'CFAILURE'), layupNames=(
    'Part-1-1.CompositeLayup-1', ), layupLocationMethod=ALL_LOCATIONS, 
    rebar=EXCLUDE)



#------Property------
#Create Composite Layup
for i in range(1, n_layer+1): #region 생성
    p = mdb.models['Model-1'].parts['Part-1']
    f = p.faces
    faces = f.getSequenceFromMask(mask=('[#1 ]', ), )
    exec(f"region{i} = regionToolset.Region(faces=faces)")

compositeLayup = mdb.models['Model-1'].parts['Part-1'].CompositeLayup(
    name='CompositeLayup-1', description='', elementType=SHELL, 
    offsetType=MIDDLE_SURFACE, symmetric=False, 
    thicknessAssignment=FROM_SECTION)
compositeLayup.Section(preIntegrate=OFF, integrationRule=SIMPSON, 
    thicknessType=UNIFORM, poissonDefinition=DEFAULT, temperature=GRADIENT, 
    useDensity=OFF)
compositeLayup.ReferenceOrientation(orientationType=GLOBAL, localCsys=None, 
    fieldName='', additionalRotationType=ROTATION_NONE, angle=0.0, 
    axis=AXIS_3)
compositeLayup.suppress()


#------time------
# 전체 실제 반복 횟수
total_iterations = n_iteration
# 시작 시간 기록
start_time = time.time()
completed_iterations = 0  # 실제 수행한 반복 횟수 카운트



#------ iteration ------
for i in range(n_iteration): #i = 0일 때의 데이터는 의미가 없으므로 패스

    iteration_start = time.time() # 각 반복 시작 시각
    completed_iterations += 1 # 실제 수행한 반복 횟수 업데이트

    #------Property------
    for j in range(n_layer): #layer 개수만큼 물성치 설정
        exec(f"CFRP_elastic{j+1} = tuple(data_p[i, 18*j + 0 : 18*j + 6])")
        exec(f"CFRP_failstress{j+1} = tuple(data_p[i, 18*j + 6 : 18*j + 13])")
        exec(f"CFRP_failstrain{j+1} = tuple(data_p[i, 18*j + 13 : 18*j + 18])")
        exec(f"Angle{j+1} = data_p[i, 18*n_layer + j]")

        #create material-composite
        Material_name = f"Material-{j+1}"
        mdb.models['Model-1'].Material(name=Material_name)
        mdb.models['Model-1'].materials[Material_name].Elastic(type=LAMINA, table=(eval(f"CFRP_elastic{j+1}"), ))
        mdb.models['Model-1'].materials[Material_name].elastic.FailStress(table=(eval(f"CFRP_failstress{j+1}"), ))
        mdb.models['Model-1'].materials[Material_name].elastic.FailStrain(table=(eval(f"CFRP_failstrain{j+1}"), ))

    compositeLayup.deletePlies()

    for k in range(1, n_layer+1): #Layer 개수만큼 Layer 생성
        region_odj = eval(f"region{k}")
        Angle_name = eval(f"Angle{k}")
        compositeLayup.CompositePly(
            suppressed=False, 
            plyName=f'Ply-{i}.{k}', 
            region=region_odj, 
            material=f'Material-{k}', 
            thicknessType=SPECIFY_THICKNESS, 
            thickness=1.0, 
            orientationType=SPECIFY_ORIENT, 
            orientationValue=Angle_name, 
            additionalRotationType=ROTATION_NONE, 
            additionalRotationField='', 
            axis=AXIS_3, 
            angle=0.0, 
            numIntPoints=3
        )

    if i == 0:
        compositeLayup.resume()

    print("CFRP_elastic example: ", CFRP_elastic1)
    print("Angle example: ", Angle_name)
    print("composite setting completed")



    #------Job------
    #Create Job
    job_name = 'job' + str(i+1)
    mdb.Job(name=job_name, model='Model-1', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB)

    #Submit Job
    mdb.jobs[job_name].submit(consistencyChecking=OFF)

    # Wait for completion
    mdb.jobs[job_name].waitForCompletion()

    print(job_name, 'completed!')

    if i == n_iteration - 1: #마지막 작업이면 바로 넘어감
        print("finished!")
        continue

    #delete job
    del mdb.jobs[job_name]
    print(job_name, 'deleted!')

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