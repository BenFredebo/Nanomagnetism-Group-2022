# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 10:25:05 2022

@author: Ben Rasmussen
@ email: ben.f.rasmussen@gmail.com

Code to process the outputted raw strings from WIEN2k eigenvalue data
"""

import csv
import numpy as np
import itertools as it
import matplotlib.pyplot as plt

########################################################################
#
# utility to generate a bash readable array of magnetization directions
# uncomment this block when needing to do so:
#
# types = [0, 1, 2, 4, -1, -2, -3, -4]
#
# direction_permutations = list(it.permutations(types, 3))
#
# bash_str_input = []
# for hkl in direction_permutations:
#    bash_str = str(hkl[0]) + " " + str(hkl[1]) + " " + str(hkl[2])
#    bash_str_input.append(bash_str)
#
# bash_str_in = '" "'.join(bash_str_input)
#
########################################################################


# reads in the data file:
# data file must be added to the path of wherever the python script is
# running. With wsl python does not like the VM
# TODO: extend this to find the path of the file

filename = "HCP_anisotropy_data.txt"
filehead = "HCP_Cobalt_2"
fh_length = len(filehead)+1


with open(filename) as f:
    data = []
    while True:
        line = f.readline()
        line.strip()
        data.append(line)
        if not line or line == '':
            break

# removes header line:
del data[0]

# depending on the specific runs, also need to remove the first nrel run
# which should be the second and third indices:

# del data[0:2]

# loops through the file lines and extracts the magnetization directions:
mag_directions = []
for line in data:
    direction = line[fh_length:fh_length+6]

    if direction != "":
        if direction[5] == '.' or (type(direction[5]) == int):
            mag_directions.append(direction)
        elif direction[5] == 's':
            direction = direction[0:5]
            mag_directions.append(direction)
        elif direction[5] == 'c':
            direction = direction[0:4]
            mag_directions.append(direction)
        else:
            print("something's wrong I can feel it")


# loops through the file lines and extracts the spin up/dn eigenvalue sums:
line_index = len(data[0]) - 17
eigenvalue_sums = []
for line in data:
    e_sum = line[line_index:-1]
    if e_sum != '':
        eigenvalue_sums.append(e_sum)

# loops through eval sums and rearranges with respect to spin up/dn:
esum_dn = []
esum_up = []

for index, esum in enumerate(eigenvalue_sums):
    if index % 2 == 0:
        esum_dn.append(float(esum))
    elif index % 2 == 1:
        esum_up.append(float(esum))


# splits the magnetization components into the HKL directions and
# gets rid of redundancies:

H = []
K = []
L = []

for m_str in mag_directions[::2]:

    if m_str[0] == "-":
        H_add = m_str[0:2]
        m_str = m_str[2:]
    else:
        H_add = m_str[0]
        m_str = m_str[1:]

    if m_str[0] == "-":
        K_add = m_str[0:2]
        m_str = m_str[2:]
        print(m_str)
    else:
        K_add = m_str[0]
        m_str = m_str[1:]

    L_add = m_str[0:]
    H.append(float(H_add))
    K.append(float(K_add))
    L.append(float(L_add))


# new filename and header:
filename_f = filehead + "_processed_data.csv"
header = ['H', 'K', 'L', 'Spin Down', 'Spin Up']
with open(filename_f, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for i in range(int(len(data)/2)):
        line = [H[i], K[i], L[i], esum_dn[i], esum_up[i]]
        writer.writerow(line)


###################################################################
#
# Utility to plot in 3d the above lists as a surface plot

# first need to normalize the lattice vectors and then multiply by
# sum of sums of eigenvalues for each directions:

# normalization factors:
norm_factors = [np.sqrt(H[i]**2+K[i]**2+L[i]**2) for i in range(len(H))]

# sums of spin up and spin down eigenvalues:
total_esum = [esum_up[e] + esum_dn[e] for e in range(len(esum_dn))]

# hard axis eigenvalue sums followed by the mae in each direction:
hard_axis_esum = min(total_esum)
mae_vector = [hard_axis_esum - total_esum[i] for i in range(len(total_esum))]

# need to divide each vector by the corresponding normalization factors:
H_norm = [H[h] / norm_factors[h] for h in range(len(H))]
K_norm = [K[k] / norm_factors[k] for k in range(len(K))]
L_norm = [L[l] / norm_factors[l] for l in range(len(L))]

# finally the x,y,z coordinates with hkl multiplied by the anisotropy in
# that direction:
H_x = [H_norm[h] * mae_vector[h] for h in range(len(H_norm))]
K_y = [K_norm[k] * mae_vector[k] for k in range(len(K_norm))]
L_z = [L_norm[l] * mae_vector[l] for l in range(len(L_norm))]

# now plots the figure in 3d:

r = [np.sqrt(H_x[i]**2 + K_y[i]**2 + L_z[i]**2) for i in range(len(H_x))]


ax = plt.axes(projection='3d')
ax.scatter(H_x, K_y, L_z, c=r, cmap='viridis', linewidth=0.5)
