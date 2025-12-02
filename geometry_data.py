class FaceData:
    """
    Raw vertex information
    """

    def __init__(self, child_node, matrix, color_code, winding=None, texmap=None, pe_tex_path=None):
        self.child_node = child_node
        self.matrix = matrix
        self.color_code = color_code
        self.winding = winding
        self.texmap = texmap
        self.pe_tex_path = pe_tex_path

        self.vertices = None
        self.pe_texmaps = []

    def process(self):
        self.vertices = FaceData.transform_vertices(self.child_node, self.matrix, self.winding)

        # TODO: this probably need to be done after the mesh is fully built so that the texture projection works properly
        if self.pe_tex_path is not None:
            self.pe_texmaps = self.pe_tex_path.build_pe_texmap(self.child_node, self.matrix, self.vertices)

    # https://github.com/rredford/LdrawToObj/blob/802924fb8d42145c4f07c10824e3a7f2292a6717/LdrawData/LdrawToData.cs#L219
    # https://github.com/rredford/LdrawToObj/blob/802924fb8d42145c4f07c10824e3a7f2292a6717/LdrawData/LdrawToData.cs#L260
    @staticmethod
    def transform_vertices(child_node, matrix, winding=None):
        vertices = child_node.vertices
        vert_count = len(vertices)

        if winding == "CW":  # else winding == "CCW" or winding is None:
            if vert_count == 3:
                vertices = [vertices[0], vertices[2], vertices[1]]
            elif vert_count == 4:
                vertices = [vertices[0], vertices[3], vertices[2], vertices[1]]

        vertices = [matrix @ v for v in vertices]

        # line type 5 also has 4 vertices
        if child_node.meta_command in ["4"] and vert_count == 4:
            FaceData.fix_bowties(vertices)

        return vertices

    # handle bowtie quadrilaterals - 6582.dat
    # https://github.com/TobyLobster/ImportLDraw/pull/65/commits/3d8cebee74bf6d0447b616660cc989e870f00085
    @staticmethod
    def fix_bowties(vertices):
        nA = (vertices[1] - vertices[0]).cross(vertices[2] - vertices[0])
        nB = (vertices[2] - vertices[1]).cross(vertices[3] - vertices[1])
        nC = (vertices[3] - vertices[2]).cross(vertices[0] - vertices[2])
        if nA.dot(nB) < 0:
            vertices[2], vertices[3] = vertices[3], vertices[2]
        elif nB.dot(nC) < 0:
            vertices[2], vertices[1] = vertices[1], vertices[2]


class GeometryData:
    """
    Raw mesh data used to build the final mesh.
    """

    def __init__(self):
        self.key = None
        self.file = None
        self.bfc_certified = None
        self.edge_data = []
        self.face_data = []
        self.line_data = []

    def process(self):
        for edge_data in self.edge_data:
            edge_data.process()

        for face_data in self.face_data:
            face_data.process()

        for line_data in self.line_data:
            line_data.process()

    def add_edge_data(self, child_node, matrix, color_code):
        self.edge_data.append(FaceData(
            child_node=child_node,
            matrix=matrix,
            color_code=color_code,
        ))

    def add_face_data(self, child_node, matrix, color_code, texmap=None, pe_tex_path=None, winding=None):
        self.face_data.append(FaceData(
            child_node=child_node,
            matrix=matrix,
            color_code=color_code,
            texmap=texmap,
            pe_tex_path=pe_tex_path,
            winding=winding,
        ))

    def add_line_data(self, child_node, matrix, color_code):
        self.line_data.append(FaceData(
            child_node=child_node,
            matrix=matrix,
            color_code=color_code,
        ))
