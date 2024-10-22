from math import sin, cos

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0 ,255)
GRAY = (128, 128, 128)
MAROON = (128, 0, 0)
LIME = (0, 128, 0)
NAVY = (0, 0, 128)
OLIVE = (128, 128, 0)
TEAL = (0, 128, 128)
PURPLE = (128, 0, 128)

def dot(a, b):
    a_rows = len(a)
    a_cols = len(a[0])
    b_rows = len(b)
    b_cols = len(b[0])
    # Dot product matrix dimentions = a_rows x b_cols
    product = [[0 for _ in range(b_cols)] for _ in range(a_rows)]
    if a_cols == b_rows:
        for i in range(a_rows):
            for j in range(b_cols):
                for k in range(b_rows):
                    product[i][j] += a[i][k] * b[k][j]
    else:
        print("INCOMPATIBLE MATRIX SIZES")
    return product

def projectPoints(points, XAngle, YAngle, ZAngle, center_pos, scale=100):
    '''
    Orthographic Projects 3D points to an image plane
    INPUT           
	points : CSV Filename
	XAngle : Camera Rotation angle around X-Axis
	YAngle : Camera Rotation angle around Y-Axis
	ZAngle : Camera Rotation angle around Z-Axis
    center_pos : Camera projrvtion point
    scale : Translation scale
	OUTPUT
    projected_points : Output array of image points
    '''
    projection_matrix = [[1, 0, 0],[0, 1, 0]]
    projected_points = [[n, n] for n in range(len(points))]
    rotation_x = [                     [1, 0, 0], [0, cos(XAngle), -sin(XAngle)], [0, sin(XAngle),  cos(XAngle)]]
    rotation_y = [[cos(YAngle),  0, sin(YAngle)],                      [0, 1, 0], [-sin(YAngle), 0, cos(YAngle)]]
    rotation_z = [[cos(ZAngle), -sin(ZAngle), 0], [sin(ZAngle),  cos(ZAngle), 0], [0, 0, 1]]    
    
    for i, point in enumerate(points):
        rotate_x = dot(rotation_x, point)
        rotate_y = dot(rotation_y, rotate_x)
        rotate_z = dot(rotation_z, rotate_y)
        point_2d = dot(projection_matrix, rotate_z)
        
        x = int(point_2d[0][0] * scale) + center_pos[0]
        y = int(point_2d[1][0] * scale) + center_pos[1]
        projected_points[i] = [x, y]
    return projected_points 