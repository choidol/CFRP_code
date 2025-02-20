#import basic package
# -*- coding: mbcs -*-
# Do not delete the following import lines
from abaqus import *
from abaqusConstants import *
import __main__

import numpy as np
import time
import os

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