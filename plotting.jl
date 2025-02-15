#plot using julia 

using PyPlot
using DelimitedFiles
using CairoMakie

bathymetry = readdlm("/Users/hodahashemi/Documents/Playground/MITgcm-master/verification/tutorial_global_oce_latlon/input/bathymetry.bin")

# Create a figure
fig = Figure(resolution = (1200, 600))

# Create an axis
ax = Axis(fig[1, 1], title = "Model Bathymetry", xlabel = "Longitude", ylabel = "Latitude")

# Plot the bathymetry data
heatmap!(ax, bathymetry, colormap = :viridis)

# Add a colorbar
Colorbar(fig[1, 2], ax, label = "Depth (m)")

# Display the plot
display(fig)

