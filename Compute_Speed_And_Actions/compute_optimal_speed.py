import numpy as np
import math

# Input 3 coords [[x1,y1],[x2,y2],[x3,y3]]
def circle_radius(coords):

    # Flatten the list and assign to variables
    x1, y1, x2, y2, x3, y3 = [i for sub in coords for i in sub]

    a = x1*(y2-y3) - y1*(x2-x3) + x2*y3 - x3*y2
    b = (x1**2+y1**2)*(y3-y2) + (x2**2+y2**2)*(y1-y3) + (x3**2+y3**2)*(y2-y1)
    c = (x1**2+y1**2)*(x2-x3) + (x2**2+y2**2)*(x3-x1) + (x3**2+y3**2)*(x1-x2)
    d = (x1**2+y1**2)*(x3*y2-x2*y3) + (x2**2+y2**2) * \
        (x1*y3-x3*y1) + (x3**2+y3**2)*(x2*y1-x1*y2)

    # In case a is zero (so radius is infinity)
    try:
        r = abs((b**2+c**2-4*a*d) / abs(4*a**2)) ** 0.5
    except:
        r = 999

    return r


#racing_track_spain = np.load('./Spain_racing_line.npy')

prefix = 'reInvent2019_track-10-8-2020-10-12-091852'
speed_adj = 0.67
speed_adj_ratio = (4.0 - speed_adj)/4.0

racing_track = np.load('./racelines/' + prefix + '.npy')
r_list = []
s_list = []
length = len(racing_track)
i = 0
while i < (length-2):
    coords = [[racing_track[i][0], racing_track[i][1]], [racing_track[i+1][0], racing_track[i+1][1]],
                      [racing_track[i+2][0], racing_track[i+2][1]]]
    r = circle_radius(coords)
    r_list.append(r)
    s = 1.7 * math.sqrt(r)
    if s > 4.0:
        s = 4.0
    s_list.append(s)

    i += 1

s_list.extend([2, 2])
s_arr = np.array(s_list)
s_arr_adj = s_arr * speed_adj_ratio
print(s_arr.shape)
print(racing_track.shape)
s_arr1 = np.reshape(s_arr_adj, (-1, 1))
final = np.concatenate((racing_track, s_arr1), axis=1)


py_fname = './enhanced/' + prefix + '.py'
with open(py_fname, "w") as file:
    print("Writing python code to %s" % py_fname)
    file.write(np.array_repr(final))

print(final)

