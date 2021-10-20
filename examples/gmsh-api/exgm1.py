import gmsh
import sys

lc = 0

gmsh.initialize()
gmsh.model.add("exgmsh1")
gmsh.model.geo.add_point(0, 0, 0, lc, 1)
gmsh.model.geo.add_point(.1, 0, 0, lc, 2)
gmsh.model.geo.add_point(.1, .3, 0, lc, 3)
p4 = gmsh.model.geo.add_point(0, .3, 0, lc)

gmsh.model.geo.add_line(1, 2, 1)
gmsh.model.geo.add_line(3, 2, 2)
gmsh.model.geo.add_line(3, p4, 3)
gmsh.model.geo.add_line(4, 1, p4)

gmsh.model.geo.add_curve_loop([4, 1, -2, 3], 1)
gmsh.model.geo.add_plane_surface([1], 1)
#gmsh.model.geo.mesh.setRecombine(2, 1)
gmsh.model.geo.synchronize()

#gmsh.model.add_physical_group(1, [1, 2, 4], 5)
ps = gmsh.model.add_physical_group(2, [1])
gmsh.model.set_physical_name(2, ps, "My surface")

gmsh.option.setNumber("Mesh.MeshSizeFactor", 0.2)
#gmsh.option.setNumber("Mesh.Algorithm", 6)  # Frontal-Delaunay for 2D meshes
gmsh.option.setNumber("Mesh.Algorithm", 8) # Frontal-Delaunay for quads
#gmsh.model.mesh.setAlgorithm(2, 33, 1)
gmsh.option.setNumber("Mesh.Smoothing", 100)
gmsh.option.setNumber("Mesh.RecombineAll", 1)
gmsh.option.setNumber("Mesh.RecombinationAlgorithm", 2) # or 3

gmsh.model.mesh.generate(2)

entities = gmsh.model.get_entities()

for e in entities:
    dim = e[0]
    tag = e[1]
    node_tags, node_coords, node_params = gmsh.model.mesh.get_nodes(dim, tag)
    elem_types, elem_tags, elem_node_tags = gmsh.model.mesh.get_elements(dim, tag)

    type = gmsh.model.getType(e[0], e[1])
    name = gmsh.model.getEntityName(e[0], e[1])
    if len(name): name += ' '
    print("Entity " + name + str(e) + " of type " + type)



    num_elem = sum(len(i) for i in elem_tags)
    print(" - Mesh has " + str(len(node_tags)) + " nodes and " + str(num_elem) +
          " elements")

    for i in elem_node_tags:
        print(len(i))


    # # * Upward and downward adjacencies:
    # up, down = gmsh.model.get_adjacencies(e[0], e[1])
    # if len(up):
    #     print(" - Upward adjacencies: " + str(up))
    # if len(down):
    #     print(" - Downward adjacencies: " + str(down))

    # physicalTags = gmsh.model.getPhysicalGroupsForEntity(dim, tag)
    # if len(physicalTags):
    #     s = ''
    #     for p in physicalTags:
    #         n = gmsh.model.getPhysicalName(dim, p)
    #         if n: n += ' '
    #         s += n + '(' + str(dim) + ', ' + str(p) + ') '
    #     print(" - Physical groups: " + s)

    # partitions = gmsh.model.getPartitions(e[0], e[1])
    # if len(partitions):
    #     print(" - Partition tags: " + str(partitions) + " - parent entity " +
    #           str(gmsh.model.getParent(e[0], e[1])))

    # # * List all types of elements making up the mesh of the entity:
    # for t in elem_types:
    #     name, dim, order, numv, parv, _ = gmsh.model.mesh.getElementProperties(t)
    #     print(" - Element type: " + name + ", order " + str(order) + " (" +
    #           str(numv) + " nodes in param coord: " + str(parv) + ")")

gmsh.write("exgmsh1.msh")

#if '-nopopup' not in sys.argv:
#    gmsh.fltk.run()

gmsh.finalize()