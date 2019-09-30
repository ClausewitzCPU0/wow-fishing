import pyaudio

p = pyaudio.PyAudio()
target = '立体声混音'
#逐一查找声音设备
for i in range(p.get_device_count()):
    devInfo = p.get_device_info_by_index(i)
    if devInfo['name'].find(target)>=0 and devInfo['hostApi'] == 0 :
        print('已找到内录设备,序号是 ',i)
print('无法找到内录设备!')
