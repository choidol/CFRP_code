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