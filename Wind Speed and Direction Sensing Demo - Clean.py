r"""
Elation Sports Technologies LLC
26 Apr 2022

Wind Speed and Direction Sensing Demonstration

"""

import csv,time
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
import matplotlib.cm as cm
import scipy.interpolate as scipyint

def is_integer(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return float(n).is_integer()

plotAlpha = 0.25

plt.close('all')

#https://stackoverflow.com/questions/14313510/how-to-calculate-rolling-moving-average-using-numpy-scipy
#x is the data you want to take the rolling average for.
#w is the size of the window to take the average
def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'same') / w

rolling_avg_window = 10

#The number of streams of data being collected by Serial_Logger, including the timestamp
num_data_streams = 3 
timestamp_included_bool = True #Assume the timestamp is the first column
remove_trailing_newline_bool = True
plot_individual_files_boolean = True

timestr = time.strftime("%d%b%Y_%H%M%p")

folder_path = r'C:\\' #Change this to be the path to the folder containing the logged data CSV file.
animation_folder = folder_path

#Change these calibration values from [1,1,1...,1] if you need to make any conversions.
calib_values = []
for i in range(0,num_data_streams):
    calib_values.append(1)

#Multiple log files can be processed if you wish. To do so, append their
#names to this list and ensure that all the files are located in the same
#folder on your computer.
file_type = '.csv'
file_names_to_process = []
file_names_to_process.append('Log_27Apr2022_1608PM')

file_labels = []

output_suffix = 'parsed'

data_all = []

for k in range(0,len(file_names_to_process)):
    
    file_name_to_process = file_names_to_process[k]

    file_path_to_process = folder_path + '\\' + file_name_to_process + file_type
    file_path_output= folder_path + '\\' + file_name_to_process + '_' + output_suffix + file_type
    
    print('Reading data from file: ' + file_name_to_process + file_type)
    
    raw_data = []
    
    with open(file_path_to_process) as csvfile:
            reader = csv.reader(csvfile,delimiter=',')
            for row in reader:
                raw_data.append(row)
    
    raw_data_2 = []
    start_row_index = 1
    
    for i in range(start_row_index,len(raw_data)):
        row_curr = []
        temp = raw_data[i][0].split(',')
        if remove_trailing_newline_bool:
            temp[-1] = temp[-1][:-1]
        for j in range(0,len(temp)):
            row_curr.append(float(temp[j]))
        raw_data_2.append(row_curr)
    
    raw_data_2 = np.array(raw_data_2)
    
    #Plot the raw data
    x_label_string = 'Time [sec]'
    y_label_string = 'Arduino Reading [from 0 to 1023]'
    fig,ax = plt.subplots()
    plt.grid(True,alpha=plotAlpha)
    plt.xlabel(x_label_string)
    plt.ylabel(y_label_string)
    plt.plot(raw_data_2[:,0],raw_data_2[:,1],'-o',label='Wind Direction Sensor')
    plt.plot(raw_data_2[:,0],raw_data_2[:,2],'-o',label='Wind Speed Sensor')
    plt.plot()
    plt.legend()
    plotTitle = 'Raw Data'
    plt.title(plotTitle)
    plt.savefig(folder_path + '\\' + file_name_to_process + '_Raw_Data' + '.png',dip=200)
    
    #Direction calibration
    raw_data_2[:,1] = raw_data_2[:,1] * (1/616) * 360
    
    #My speed calibration test: 20 rotations in 22 seconds (0.90909 rev/sec) gave average output of 34.91 (10-bit ADC)
    #and that corresponds to: 65mm radius * 2 * pi = 408.4mm circumference, so 408.4 * 0.90909 = 371.28mm/sec
    #Units in meters per second, voltage ranges from 0 to 5V
    raw_data_2[:,2] = raw_data_2[:,2] * (1/34.91) * 0.37128
    
    time_data = raw_data_2[:,0]
    direction_data = raw_data_2[:,1]
    speed_data = raw_data_2[:,2]
    
    #Modify the direction data so that it doesn't "loop around"
    for i in range(1,len(direction_data)):
        diff_norm = abs(direction_data[i] - direction_data[i-1])
        diff_1 = abs((direction_data[i] + 360) - direction_data[i-1])
        diff_2 = abs((direction_data[i] - 360) - direction_data[i-1])
        if diff_1 < diff_norm:
            direction_data[i] = direction_data[i] + 360
        elif diff_2 < diff_norm:
            direction_data[i] = direction_data[i] - 360
    
    #Perform cubic interpolation on the data
    f1 = scipyint.interp1d(time_data, speed_data, kind='cubic')
    f2 = scipyint.interp1d(time_data, direction_data, kind='cubic')
    
    #Modify the number of interpolated frames to hit the desired frame rate
    target_fps = 24
    #num_int = 1000
    time_delta_total = max(time_data) - min(time_data)
    num_frames = int(np.ceil(target_fps * time_delta_total))
    times_new = np.linspace(min(time_data), max(time_data), num=num_frames, endpoint=True)
    fps_calc = num_frames/(times_new[-1] - times_new[0])
    
    f1_data = f1(times_new)
    f2_data = f2(times_new)
    
    if timestamp_included_bool:
    
        x_label_string = 'Time [sec]'
        y_label_string = 'Speed [m/s]'
        fig,ax = plt.subplots()
        plt.grid(True,alpha=plotAlpha)
        plt.xlabel(x_label_string)
        plt.ylabel(y_label_string)
        plt.plot(time_data,speed_data,'-ob',label='Speed')
        plt.plot(times_new, f1_data, '--b')
        plt.plot()
        plt.legend()
        plotTitle = 'Wind Speed Data'
        plt.title(plotTitle)
        plt.savefig(folder_path + '\\' + file_name_to_process + '_Speed' + '.png',dpi=200)
        
        x_label_string = 'Time [sec]'
        y_label_string = 'Direction [deg]'
        fig,ax = plt.subplots()
        plt.grid(True,alpha=plotAlpha)
        plt.xlabel(x_label_string)
        plt.ylabel(y_label_string)
        plt.plot(time_data,direction_data,'-or',label='Direction')
        plt.plot(times_new, f2_data, '--r')
        plt.legend()
        plotTitle = 'Wind Direction Data'
        plt.title(plotTitle)
        plt.savefig(folder_path + '\\' + file_name_to_process + '_Direction' + '.png',dpi=200)
        
    
    #Convert the raw direction readings to theta values for animation plotting.
    direction_data_theta = np.deg2rad(f2_data)
    theta_solved_list_rad = direction_data_theta
    F_norm = f1_data
    
    #Linear map function
    #https://stackoverflow.com/questions/1969240/mapping-a-range-of-values-to-another
    def linear_map(value, leftMin, leftMax, rightMin, rightMax):
        # Figure out how 'wide' each range is
        leftSpan = leftMax - leftMin
        rightSpan = rightMax - rightMin
    
        # Convert the left range into a 0-1 range (float)
        valueScaled = float(value - leftMin) / float(leftSpan)
    
        # Convert the 0-1 range into a value in the right range.
        return rightMin + (valueScaled * rightSpan)
    
    #Have the line change color as the force magnitude changes.
    val_min = min(F_norm)
    val_max = max(F_norm)
    color_val_min = 0
    color_val_max = 1
    color_vals = []
    for i in range(0,len(F_norm)):
        val_curr = F_norm[i]
        color_vals.append(linear_map(val_curr,val_min,val_max,color_val_min,color_val_max))
    
    color_vals = np.array(color_vals)
    #https://stackoverflow.com/questions/12236566/setting-different-color-for-each-series-in-scatter-plot-on-matplotlib
    colors = cm.rainbow(color_vals)
    
    #Create a "functional" animation instead of a frames/artist-based one
    #https://github.com/lukepolson/youtube_channel/blob/main/Python%20Metaphysics%20Series/vid7.ipynb
    def update(i):
        
        #Dashed line to indicate the direction
        ln1.set_data([theta_solved_list_rad[i],theta_solved_list_rad[i]], [0,max(F_norm)])
        ln1.set_color('k')
        ln1.set_linewidth(1)
        
        ln2.set_data([theta_solved_list_rad[i],theta_solved_list_rad[i]], [0,F_norm[i]])
        ln2.set_color(colors[i])
        ln2.set_linewidth(5)
        time_string_curr = format(times_new[i], '.2f')
        ann1.set_text('t = ' + time_string_curr + ' sec')
        
        return ln1, ann1
    
    fig = plt.figure()
    ax = fig.add_axes([0.1,0.1,0.8,0.8],polar=True)
    ax.set_theta_zero_location("N")
    ax.set_theta_direction(-1)  # theta increasing clockwise
    r_limit = max(F_norm)
    ax.set_ylim(0,r_limit)
    ln1, = plt.plot([], [], ':', lw=3, markersize=8)
    ln2, = plt.plot([], [], 'b-', lw=3, markersize=8)
    ann1 = plt.annotate('Placeholder', xy=(1.3,r_limit), color = 'k', bbox=dict(boxstyle="square", alpha=1, facecolor='w'))
    
    print()
    print('Creating animation in a Figure...')
    #Interval is the delay between frames in msec. It is an integer.
    ani = animation.FuncAnimation(fig, update, frames=len(F_norm), interval=1)
    
    print()
    print('Saving MP4...')
    
    #You must have FFmpeg installed.
    #It can be downloaded from here: https://ffmpeg.org/download.html#build-windows
    plt.rcParams['animation.ffmpeg_path'] = r'C:\(...)\ffmpeg.exe' #Enter the full path to your FFmpeg.exe file here.
    writervideo = animation.FFMpegWriter(fps=target_fps) 
    ani.save(animation_folder + '\\' + file_name_to_process + '_' + 'animation' + '.mp4', writer=writervideo)
    print('MP4 saved!')
        
        
        


