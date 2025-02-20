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

#delete job
del mdb.jobs[job_name]
print(job_name, 'deleted!')