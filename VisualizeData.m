%% IMU
clc
close all
clear

data_size = 6;
num_data = 6;
length = 10000;
series=zeros(6, length);
s = serialport("COM4", 115200);
tiledlayout(3,2);
titles = ["Ang X" "Ang Y" "Ang Z" "Lin X" "Lin Y" "Lin Z"];
for i = 1:length
    d = str2num(read(s, data_size*num_data+num_data-1, "string"));
    series(1:6, i) = d;
    if(rem(i, 100) == 0)
        for j = 1:num_data
            nexttile(j);
            plot(series(j,:));
            title(titles(j));
        end
        drawnow;
    end
end

%% EMG
clc
close all
clear

data_size = 6;
num_data = 7;
length = 10000;
series=zeros(num_data, length);
s = serialport("COM4", 115200);
tiledlayout(4,2);
titles = ["ADC0" "ADC1" "ADC2" "ADC4" "ADC5" "ADC6" "ADC7"];
for i = 1:length
    d = str2num(read(s, data_size*num_data+num_data-1, "string"));
    series(1:num_data, i) = d;
    if(rem(i, 100) == 0)
        for j = 1:num_data
            nexttile(j);
            plot(series(j,:));
            title(titles(j));
        end
        drawnow;
    end
end