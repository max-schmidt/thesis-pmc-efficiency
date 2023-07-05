import matplotlib as mpl
# Use the pgf backend (must be set before pyplot imported)
mpl.use('pgf')
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

csvfile = r"<insert_path>"

# Read the data from the CSV file
df = pd.read_csv(csvfile, header=0)
# Group the data by the first column (filename)
groups = df.groupby(['total variables', 'file'])
# Create a new figure and axes
fig, ax = plt.subplots(figsize=(25, 10))
# Adjust layout
fig.subplots_adjust(left=0.025, right=0.998, top=0.975, bottom=0.08)
# Create a list of colors to use for the boxplots (red & blue)
colors = ['#DB3124', '#0D73DB']
# Iterate over the groups and create a boxplot for each
for i, (name, group) in enumerate(groups):
    # Extract the data for the boxplot
    data_mc = group['ganak (mc) total time']
    data_pmc = group['ganak (pmc) median time']
    # Filter out NaN data / errors
    data_mc_without_errors = data_mc[~np.isnan(data_mc)]
    data_mc_only_errors = data_mc[np.isnan(data_mc)]
    data_pmc_without_errors = data_pmc[~np.isnan(data_pmc)]
    data_pmc_only_errors = data_pmc[np.isnan(data_pmc)]
    # Filter out Timeout data
    data_mc_without_errors_timeouts = data_mc_without_errors[data_mc_without_errors != 9999]
    data_mc_only_timeouts = data_mc_without_errors[data_mc_without_errors == 9999]
    data_pmc_without_errors_timeouts = data_pmc_without_errors[data_pmc_without_errors != 9999]
    data_pmc_only_timeouts = data_pmc_without_errors[data_pmc_without_errors == 9999]
    # Create the boxplot
    boxprops1 = dict(linestyle='-', linewidth=1, color=colors[0])
    boxprops2 = dict(linestyle='-', linewidth=1, color=colors[1])
    whiskerprops1 = dict(linestyle='-', linewidth=1, color=colors[0])
    whiskerprops2 = dict(linestyle='-', linewidth=1, color=colors[1])
    flierprops1 = dict(marker='o', markerfacecolor='white', markersize=5, markeredgecolor=colors[0])
    flierprops2 = dict(marker='o', markerfacecolor='white', markersize=5, markeredgecolor=colors[1])
    medianprops = dict(linestyle='-', linewidth=1, color='black')
    meanprops = dict(marker='D', markerfacecolor='black', markersize=8)
    bp1 = ax.boxplot([data_mc_without_errors_timeouts], positions=[i*2+1.1], boxprops=boxprops1, whiskerprops=whiskerprops1, flierprops=flierprops1, medianprops=medianprops, meanprops=meanprops, widths = 0.3)
    bp2 = ax.boxplot([data_pmc_without_errors_timeouts], positions=[i*2+1.9], boxprops=boxprops2, whiskerprops=whiskerprops2, flierprops=flierprops2, medianprops=medianprops, meanprops=meanprops, widths = 0.3)
    # Add upper x-axis tick labels with the medians
    ax.text((i*2+1), 0.985, str(round(bp1['medians'][0].get_ydata()[0], 2)), transform=ax.get_xaxis_transform(), horizontalalignment='center', size='small', weight='roman', color=colors[0])
    ax.text((i*2+2), 0.985, str(round(bp2['medians'][0].get_ydata()[0], 2)), transform=ax.get_xaxis_transform(), horizontalalignment='center', size='small', weight='roman', color=colors[1])
    if len(data_mc_only_timeouts) > 0:
        ax.text((i*2+1), 0.97, str(len(data_mc_only_timeouts))+" TO", transform=ax.get_xaxis_transform(), horizontalalignment='center', size='small', weight='roman', color=colors[0])
    if len(data_pmc_only_timeouts) > 0:
        ax.text((i*2+2), 0.97, str(len(data_pmc_only_timeouts))+" TO", transform=ax.get_xaxis_transform(), horizontalalignment='center', size='small', weight='roman', color=colors[1])
    if len(data_mc_only_errors) > 0:
        ax.text((i*2+1), 0.955, str(len(data_mc_only_errors))+" E", transform=ax.get_xaxis_transform(), horizontalalignment='center', size='small', weight='roman', color=colors[0])
    if len(data_pmc_only_errors) > 0:
        ax.text((i*2+2), 0.955, str(len(data_pmc_only_errors))+" E", transform=ax.get_xaxis_transform(), horizontalalignment='center', size='small', weight='roman', color=colors[1])
    if(i):
        ax.axvline((i-1)*2+2.5, linestyle='-', linewidth=1, color='lightgrey', alpha=0.5)

# log. scale for time
ax.set_yscale('log')
plt.ylim((0.03,999))
# Set the title and labels for the graph
ax.set_title('GANAK Model Counter')
ax.set_xlabel('Datei Index')
ax.set_ylabel('Zeit (Sekunden)')
# Add a horizontal grid to the plot
ax.yaxis.grid(True, linestyle='-', which='major', color='lightgrey', alpha=0.5)
# Set the x-axis ticks and labels
ax.set_xticks([i*2+1.5 for i in range(len(groups))], range(1, len(groups)+1))
# ax.set_xticklabels(groups.groups.index(), fontsize=8)
# Add a basic legend
fig.text(0.83, 0.025, 'Slicing + Model Counting', backgroundcolor=colors[0], color='white', weight='roman', size='medium')
fig.text(0.91, 0.025, 'Projected Model Counting', backgroundcolor=colors[1], color='white', weight='roman', size='medium')
# more legend
ax.text(0.43, 0.985, "Median", transform=ax.get_xaxis_transform(), horizontalalignment='right', size='small', weight='semibold')
ax.text(0.43, 0.97, "Timeouts", transform=ax.get_xaxis_transform(), horizontalalignment='right', size='small', weight='semibold')
ax.text(0.43, 0.955, "Errors", transform=ax.get_xaxis_transform(), horizontalalignment='right', size='small', weight='semibold')
# Save the figure with the specified DPI
fig.savefig('figure-ganak.pdf', dpi=300, format='pdf')
fig.savefig('figure-ganak.pgf')
