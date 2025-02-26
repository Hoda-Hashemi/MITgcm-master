#%%
# import pertinent modules
import numpy as np
import matplotlib.pyplot as plt
import os

model_dir = "/Users/hodahashemi/Documents/Playground/MITgcm-master/verification/tutorial_global_oce_latlon"

bathymetry_file = "/Users/hodahashemi/Documents/Playground/MITgcm-master/verification/tutorial_global_oce_latlon/input/bathymetry.bin"

nx,ny = 90,40 

bathymetry = np.fromfile(bathymetry_file, dtype=np.float32)

# Reshape
bathymetry = bathymetry.reshape((ny, nx))

# make a plot of the bathymetry
plt.figure(figsize=(12, 6))
plt.imshow(bathymetry, cmap='viridis', origin='lower')
plt.colorbar(label='Depth (m)')
plt.title('Model Bathymetry')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()

# %%
# read in the data from files into grids for theta, salt, uvel, and vvel
import numpy as np
import matplotlib.pyplot as plt
import MITgcmutils as mit
# %%

base_path = '/Users/hodahashemi/Documents/Playground/MITgcm-master/verification/tutorial_global_oce_latlon/run/'

# List of data files to read
data_files = [
    'sFluxtave.0000000000.001.001.data',
    'sFluxtave.0000000000.002.001.data',
    'sFluxtave.0000000010.001.001.data',
    'sFluxtave.0000000010.002.001.data',
    'sFluxtave.0000000020.001.001.data',
    'sFluxtave.0000000020.002.001.data'
]

meta_files = [
    'sFluxtave.0000000000.001.001.meta',
    'sFluxtave.0000000000.002.001.meta',
    'sFluxtave.0000000010.001.001.meta',
    'sFluxtave.0000000010.002.001.meta',
    'sFluxtave.0000000020.001.001.meta',
    'sFluxtave.0000000020.002.001.meta'
]

# Remove the .data extension from the file names
base_names = [os.path.join(base_path, file.replace('.data', '')) for file in data_files]

# Read and concatenate data
data_list = [mit.rdmds(base_name) for base_name in base_names]
data = np.concatenate(data_list, axis=0)

# Define the figure size
fig, ax = plt.subplots(figsize=(20, 3))

# Plot the data
im = ax.imshow(data[0], cmap='viridis')  # Adjust the index as needed
cbar = plt.colorbar(im, ax=ax)

# Customize the plot
ax.set_title('MITgcm Output Data')
plt.show()

# %%

