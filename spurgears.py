import bpy
from math import *

def createMeshFromData(name, origin, verts, faces):
    # Create mesh and object
    me = bpy.data.meshes.new(name+'Mesh')
    ob = bpy.data.objects.new(name, me)
    ob.location = origin
    ob.show_name = False

    # Link object to scene and make active
    bpy.context.collection.objects.link(ob)
    ob.select_set(True)

    # Create mesh from given verts, faces.
    me.from_pydata(verts, [], faces)
    # Update mesh with new data
    me.update(calc_edges=True)
    return ob

def CreateSpurGear( name, teeth, modulem, cenxm, cenym, holeradm, thicknessm):
    #arguments coming in are in metres, we need to convert to millimetres
    module = modulem * 0.001
    cenx = cenxm * 0.001
    ceny = cenym * 0.001
    holerad = holeradm * 0.001
    thickness = thicknessm * 0.001 

    # phi = pressure angle (usually 20 degrees)
    phi = pi / 9
    radpitch = module * teeth / 2
    radbase = radpitch * cos(phi)

    # number of faces, edges and vertices per tooth
    nrFaces = 15
    nrEdges = 1 + (2 * nrFaces)
    
    nrVerts = 2 * (1 + nrFaces)
    nrVertsAllTeeth = nrVerts * teeth
    nrVertsHole = 2 * teeth
    nrVertsTotal = 2 * (nrVertsAllTeeth + nrVertsHole)
    
    nrFacesPerPlane = (nrFaces + 2) * teeth
    nrFacesHole = nrVertsHole
    nrFacesAllTeeth = nrVerts * teeth
    
    radadd = radpitch + module
    radded = radpitch - (module * 1.2)
    points = [[0,0] for _ in range(nrVerts)]
    
    tpitch = sqrt((1 / (cos(phi) * cos(phi))) - 1)
    tadd = sqrt(((radadd / radbase) * (radadd / radbase)) - 1)
    
    angpitch = atan((sin(tpitch) - (tpitch * cos(tpitch)))/(cos(tpitch) + (tpitch * sin(tpitch))))
    angadd = atan((sin(tadd) - (tadd * cos(tadd)))/(cos(tadd) + (tadd * sin(tadd))))
    
    for i in range (1,nrFaces + 1):
        t = (i - 1) * tadd / (nrFaces - 1)
        ptx = radbase * (cos(t) + (t * sin(t)))
        pty = radbase * (sin(t) - (t * cos(t)))
        points[i][0] = (ptx * cos(angpitch + (0.5 * pi / teeth))) + (pty * sin(angpitch + (0.5 * pi / teeth)))
        points[i][1] = (pty * cos(angpitch + (0.5 * pi / teeth))) - (ptx * sin(angpitch + (0.5 * pi / teeth)))
        
        points[nrVerts - 1 - i][0] = points[i][0]
        points[nrVerts - 1 - i][1] = - points[i][1]
        
    points[0][1] = points[1][1]
    points[0][0] = sqrt((radded * radded) - (points[1][1] * points[1][1]))
    points[nrVerts - 1][0] = points[0][0]
    points[nrVerts - 1][1] = - points[0][1]
    
    # get the edges, vertices and faces
    #edges = [[0, 0] for _ in range(nrEdges * teeth)]
    verts = [[0, 0, 0] for _ in range(nrVertsTotal)]
    faces = [[0,0,0,0] for _ in range((nrFacesPerPlane * 2) + nrFacesHole + nrFacesAllTeeth)]
    
    # the rest of the teeth
    
    for n in range(teeth):
        # the vertices on the rest of the teeth
        for i in range(nrVerts):
            verts[i + (n * nrVerts)][0] = (points[i][0] * cos(n * 2 * pi / teeth)) - (points[i][1] * sin(n * 2 * pi / teeth))
            verts[i + (n * nrVerts)][1] = (points[i][0] * sin(n * 2 * pi / teeth)) + (points[i][1] * cos(n * 2 * pi / teeth))
            verts[i + (n * nrVerts)][2] = 0
            
        # The faces on the rest of the teeth
        for i in range(nrFaces):
            faces[i + (n * nrFaces)][0] = i + (n * nrVerts)
            faces[i + (n * nrFaces)][1] = i + 1 + (n * nrVerts)
            faces[i + (n * nrFaces)][2] = nrVerts + (n * nrVerts) - (i + 2)
            faces[i + (n * nrFaces)][3] = nrVerts + (n * nrVerts) - (i + 1)
            
    # the vertices for the hole
    for n in range(nrVertsHole):
        ptx = holerad * cos((n - 0.5) * pi / teeth)
        pty = holerad * sin((n - 0.5) * pi / teeth)
        
        verts[n + (teeth * nrVerts)][0] = ptx
        verts[n + (teeth * nrVerts)][1] = pty
        
    # the rest of the faces on that plane
    for n in range(teeth):
        i = (2 * n) + (teeth * nrFaces)
        print(i)
        #print(n * nrFaces)
        faces[i][0] = n * nrVerts
        faces[i][1] = ((n + 1) * nrVerts) - 1
        faces[i][2] = (2 * n) + (nrVerts * teeth) + 1
        faces[i][3] = (2 * n) + (nrVerts * teeth)
        
        if n < teeth - 1:
            i = (2 * n) + 1 + (teeth * nrFaces)
            faces[i][0] = ((n + 1) * nrVerts) - 1
            faces[i][1] = (n + 1) * nrVerts
            faces[i][2] = (2 * (n + 1)) + (nrVerts * teeth)
            faces[i][3] = (2 * (n)) + (nrVerts * teeth) + 1
        else:
            i = (2 * n) + 1 + (teeth * nrFaces)
            faces[i][0] = ((n + 1) * nrVerts) - 1
            faces[i][1] = 0
            faces[i][2] = (nrVerts * teeth)
            faces[i][3] = (2 * (n)) + (nrVerts * teeth) + 1
        
    # do the other plane
    # the vertices on the other plane
    for i in range((nrVerts + 2) * teeth):
        j = i + ((nrVerts + 2) * teeth)
        verts[j][0] = verts[i][0]
        verts[j][1] = verts[i][1]
        verts[j][2] = thickness
            
    # the faces on the other plane
    for i in range(nrFacesPerPlane):
        j = i + ((nrFaces + 2) * teeth)
        faces[j][0] = faces[i][0] + (nrVerts + 2) * teeth
        faces[j][1] = faces[i][1] + (nrVerts + 2) * teeth
        faces[j][2] = faces[i][2] + (nrVerts + 2) * teeth
        faces[j][3] = faces[i][3] + (nrVerts + 2) * teeth
        
            
    # joining the two levels
    for i in range(nrFacesAllTeeth):
        j = i + (nrVertsAllTeeth + nrVertsHole)
        k = i + (2 * nrFacesPerPlane)
        if i < (nrVertsAllTeeth - 1):
            faces[k][0] = i
            faces[k][1] = i + 1
            faces[k][3] = j
            faces[k][2] = j + 1
        else:
            faces[k][0] = i
            faces[k][1] = 0
            faces[k][3] = j
            faces[k][2] = (nrVerts + 2) * teeth
            
        for i in range(2 * teeth):
            k = i + (2 * nrFacesPerPlane) + nrFacesAllTeeth
            j = i + ((nrVerts + 2) * teeth)
            if i < (2 * teeth) - 1:
                faces[k][0] = i + nrVertsAllTeeth
                faces[k][1] = i + nrVertsAllTeeth + 1
                faces[k][3] = j + nrVertsAllTeeth
                faces[k][2] = j + nrVertsAllTeeth + 1
            else:
                faces[k][0] = i + nrVertsAllTeeth
                faces[k][1] = nrVertsAllTeeth
                faces[k][3] = j + nrVertsAllTeeth
                faces[k][2] = ((nrVerts + 2) * teeth) + nrVertsAllTeeth

    createMeshFromData( name, [cenx, ceny, 0], verts, faces)
        

# CreateSpurGear( name, teeth, module, cenxm, cenym, holeradm, thicknessm)
# name = any meaningful name, you decide - that's the name that will be shown in the Outliner
# teeth = number of teeth
# module = pitch circle diameter / no. of teeth, in millimetres
# (cenxm, cenym) - the centre of the gear wheel, all dimensions in millimetres
# holeradm - radius of the hole, in millimetres
# thicknessm - thickness of the gear wheel, in millimetres 
CreateSpurGear("MyGear", 24, 36, 0, 0, 10, 10)