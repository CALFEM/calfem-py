# -*- coding: iso-8859-15 -*-

"""
CALFEM Editor Example

Written by Karl Eriksson
"""

import calfem.editor as cfe
import calfem.geometry as cfg
import calfem.mesh as cfm
import calfem.vis_mpl as cfv
import calfem.utils as cfu
import calfem.core as cfc
import numpy as np

# Creating a square geometry with two markers
g = cfg.Geometry()

g.point([0.0, 0.0])  # point 0
g.point([100.0, 0.0])  # point 1
g.point([100, 100])  # point 2
g.point([0, 100])  # point 3

g.spline([0, 1])  # line 0
g.spline([1, 2])  # line 1
g.spline([2, 3])  # line 2
g.spline([3, 0])  # line 3

g.surface([0, 1, 2, 3])  # Connect lines to form surface
g.setCurveMarker(0, "A")
g.setCurveMarker(2, "B")

# Open the geometry to allow changes in the CALFEM Geometry Editor
geometry, marker_dict = cfe.edit_geometry(g)

t = 0.2
v = 0.35
E = 2.1e9
ptype = 1
ep = [ptype,t]
D = cfc.hooke(ptype, E, v)


bcs = [[marker_dict["A"], 0]]  # Every border or point marked with A will recieve boundary condition value of 0
loads = [[marker_dict["B"], 10e5]]  # Every border or point marked with B will recieve load value of 10e5

el_size_factor = 5
el_type = 3
dofs_per_node = 2

mesh = cfm.GmshMeshGenerator(geometry)
mesh.el_size_factor = el_size_factor  # Factor that changes element sizes.
mesh.el_type = el_type
mesh.dofs_per_node = dofs_per_node

coords, edof, dofs, bdofs, elementmarkers = mesh.create()

# --- Ber�kna element koordinater

ex, ey = cfc.coordxtr(edof, coords, dofs)


# --- Assemblera systemmatris

nDofs = edof.max()

K = np.zeros([nDofs, nDofs])

for eltopo, elx, ely in zip(edof, ex, ey):
    Ke = cfc.planqe(elx, ely, ep, D)
    cfc.assem(eltopo, K, Ke)
# --- L�sning av ekvationssystem

f = np.zeros([nDofs, 1])
bcPrescr = np.array([], int)
bcVal = np.array([], float)

for bc in bcs:
    bcPrescr, bcVal = cfu.applybc(bdofs, bcPrescr, bcVal, bc[0], bc[1])

for load in loads:
    cfu.applyforcetotal(bdofs, f, load[0], load[1])

a, r = cfc.solveq(K, f, bcPrescr, bcVal)

# --- Ber�kna elementkrafter

ed = cfc.extractEldisp(edof, a)

vonMises = []

# For each element:
for i in range(edof.shape[0]):

    # Determine element stresses and strains in the element.
    es, et = cfc.planqs(ex[i,:], ey[i,:], ep, D, ed[i,:])

    # Calc and append effective stress to list.
    vonMises.append(np.sqrt(np.power(es[0],2) - es[0]*es[1] + np.power(es[1],2) + 3*es[2] ) )


cfv.draw_geometry(geometry)
cfv.figure()
cfv.draw_element_values(vonMises, coords, edof, mesh.dofs_per_node, mesh.el_type, None, draw_elements=False, draw_undisplaced_mesh=False, title="Example 6 - Effective stress")
cfv.show_and_wait()
