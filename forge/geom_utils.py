import panda3d.core as p3d


class GeomUtils:
    def create_3lines_axes(thickness: int, length: float) -> p3d.NodePath:
        # 3 axes = 3 lines = 6 vertices
        num_vertices = 6

        # vertex format containing position and color
        vertex_format = p3d.GeomVertexFormat.get_v3c4()

        vdata = p3d.GeomVertexData("vdata", vertex_format, p3d.Geom.UH_static)
        vdata.reserve_num_rows(num_vertices)

        # vertex writers
        vertex_writer = p3d.GeomVertexWriter(vdata, "vertex")
        color_writer = p3d.GeomVertexWriter(vdata, "color")

        # lines primitive
        lines = p3d.GeomLines(p3d.Geom.UH_static)
        lines.reserve_num_vertices(num_vertices)

        # axis colors
        colors = [
            p3d.LVecBase4f(1.0, 0.0, 0.0, 1.0),  # X - Red
            p3d.LVecBase4f(0.0, 1.0, 0.0, 1.0),  # Y - Green
            p3d.LVecBase4f(0.0, 0.0, 1.0, 1.0),  # Z - Blue
        ]

        # axis directions
        directions = [
            p3d.LVector3f(length, 0.0, 0.0),  # X
            p3d.LVector3f(0.0, length, 0.0),  # Y
            p3d.LVector3f(0.0, 0.0, length),  # Z
        ]

        vertex_index = 0

        # create each axis line
        for i in range(3):
            start_point = p3d.LPoint3f(0.0, 0.0, 0.0)
            end_point = p3d.LPoint3f(directions[i])

            # start vertex
            vertex_writer.add_data3(start_point)
            color_writer.add_data4(colors[i])

            # end vertex
            vertex_writer.add_data3(end_point)
            color_writer.add_data4(colors[i])

            # line indices
            lines.add_vertices(vertex_index, vertex_index + 1)

            vertex_index += 2

        # create Geom
        geom = p3d.Geom(vdata)
        geom.add_primitive(lines)

        # create GeomNode
        geom_node = p3d.GeomNode("3LinesAxes")
        geom_node.add_geom(geom)

        # create NodePath
        axes_np = p3d.NodePath(geom_node)
        axes_np.set_render_mode_thickness(max(thickness, 1))
        axes_np.set_scale(1.0)

        return axes_np
        
    def create_square() -> p3d.NodePath:
        # Create vertex data with V3 format (3D vertices, dynamic)
        vdata = p3d.GeomVertexData("square", p3d.GeomVertexFormat.get_v3(), p3d.Geom.UH_dynamic)

        # Create a writer for the "vertex" column
        vertex_writer = p3d.GeomVertexWriter(vdata, "vertex")

        # Define the vertices of the square
        vertices = [
            p3d.LVector3f(-1, -1, 0),
            p3d.LVector3f( 1, -1, 0),
            p3d.LVector3f( 1,  1, 0),
            p3d.LVector3f(-1,  1, 0),
        ]

        for v in vertices:
            vertex_writer.add_data3f(v)

        # Create the square geometry
        square_geom = p3d.Geom(vdata)

        # Create a GeomTriangles object to define the square's triangles
        square_triangles = p3d.GeomTriangles(p3d.Geom.UH_dynamic)

        # Define the triangles of the square
        square_triangles.add_vertices(0, 1, 2)
        square_triangles.add_vertices(2, 3, 0)

        # Add the triangles to the square's geometry
        square_geom.add_primitive(square_triangles)

        # Create a GeomNode to hold the square's geometry
        square_node = p3d.GeomNode("Square")
        square_node.add_geom(square_geom)

        # Create a NodePath to hold the GeomNode
        square_np = p3d.NodePath(square_node)
        return square_np
