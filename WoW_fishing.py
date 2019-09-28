"""
notes :
1.支持各个水域钓鱼，注意确保屏幕下方三分之一矩形区域全为水域，没有怪物和其他钓鱼者干扰。
2.调节 RMS（触发响度），确保其值小于水花声但大于其他背景声音。（关闭背景音可获得更好效果）
3.将特效调至最低可获得最佳效果。(95% 以上成功率)
4.请勿于官方服务器，仅用于在某些外服、单机客户端测试各个地点各时段鱼群的构成和比例。
5.程序对截图进行颜色分析，确定鱼漂坐标，然后以水花声为收杆触发条件。由于是个人使用，不再做过多说明。

Version 1.2 : TODO
1.代码重构。
2.数据统计。

Version 1.1 :
1.调节水域截屏区域，大幅提升成功率。
2.解决水下诱鱼器过期时死锁的BUG。
3.注释部分DEBUG代码，减少响应时间。
4.增加测试代码

Version 1.0 :
修改原作者代码，使其可用于中文客户端。
SOURCE: wdavid214
MODIFIED BY: ClausewitzCPU0

"""
from win32gui import GetWindowText, GetForegroundWindow, GetWindowRect
from PIL import ImageGrab, Image
import imageio
import numpy as np
import time
import sys
import pyautogui

import audioop
import pyaudio

# need to filter out image outliers. check distance to middle pixel to end, if too great then use 2nd last pixel and check dist til u find
# how about just using 10th last pixel hard coded?

# open audio stuff to listen on mic for speaker feedback going in (turn wow vol all the way up)
chunk = 1024
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=2,  # need this to work (like other record script)
                rate=44100,
                input=True,
                frames_per_buffer=chunk,)
                # input_device_index=0)

RMS = 3500
# buf=40 # avoid boundary false trigger; not too far though
buf = 0  # alrdy compensated for boundary in initial rect adjustments

z = 0

# looks like we can find anything between 100 and 200 pixels in out_subtraction_green
# to find bob once it appears. then run audio loop til trigger

while True:
    if GetWindowText(GetForegroundWindow()) != '魔兽世界':
        print('World of Warcraft no active window !')
        print('-- New check 2 sec')
        time.sleep(2)
    else:

        ############# ONE TIME LOGIC AT VERY BEGINNING ####

        rect = GetWindowRect(GetForegroundWindow())
        rect = np.array(rect)
        #rect:[33 98 1975 1234] 分别表示该窗口的/左侧/顶部/右侧/底部坐标

        rect_back = np.copy(rect)

        # print(type(rect))

        rect[0] += 200
        rect[2] -= 200

        rect[3] -= 10

        # rect[1] += 25  # cut off title bar
        rect[1] += 750  # cut off title bar

        fish_area = (rect[0], rect[1], rect[2], rect[3])

        ############# END ONE TIME LOGIC AT VERY BEGINNING ####

        num_iterations = 0

        while num_iterations < 10:

            num_iterations += 1

            time.sleep(
                1.5)  # give some time for old lure to fade out ( so don't have double-lure issue which i thought was outlier)

            # cast line
            pyautogui.press('1')

            # time.sleep(.5)  # let it solidify

            continue1 = 0

            cnt = -1

            # clear out audio stream buffer to avoid double-triggers on next loop
            # print ('stopping audio stream')
            # stream.stop_stream()
            # time.sleep(2)
            # print ('starting audio stream')
            # stream.start_stream() # didnt seem to filter out old one...

            while continue1 == 0:

                cnt = cnt + 1

                time.sleep(1)  # TODO REMOVE

                print('getting new img')

                img = ImageGrab.grab(fish_area)
                # img.save('img.png')  # Saving the image

                # 对其他通道置零，只显示单个通道(b, g, r)
                # 例如只显示红色通道：cur_img[:, :, 0] = 0, cur_img[:, :, 1] = 0
                img_np = np.array(img)
                red_content = img_np[:, :, 0]
                red_content_back = red_content[:]
                green_content = img_np[:, :, 1]
                blue_content = img_np[:, :, 2]
                print('green_content:{}'.format(green_content))
                print('red_content:{}'.format(red_content))

                if cnt > 0:
                    # subtraction_green = red_content_back - green_content
                    subtraction_green = green_content - red_content_back
                    # imageio.imwrite('out_subtraction_green%d.png' % (cnt), subtraction_green)
                    # imageio.imwrite('out_subtraction_red%d.png' % (cnt), red_content_back - green_content)

                    # find intensity between 100 and 200 in subtraction green, then move mouse there.
                    # a = np.array([1, 3, 5, 6, 9, 10, 14, 15, 56])

                    # b = np.where(np.logical_and(subtraction_green>=100, subtraction_green<=200))
                    # 输出满足条件元素的坐标
                    b = np.where(subtraction_green > 200)
                    # print(type(b))
                    print('b: {}\n'.format(b))
                    # print(b[0])
                    if b[0].size > 10:
                        print(b[0].size)
                        print(b[0])
                        print(b[1])
                        print(subtraction_green)
                        # np.savetxt("foo.csv", subtraction_green, delimiter=",")

                        # imageio.imwrite('out_subtraction_green_final.png', subtraction_green)

                        jx = b[0][0]  # grab first occurrence
                        jy = b[1][0]

                        # grab middle occurrence
                        midpt1 = len(b[0]) / 2
                        print(midpt1)
                        # jx = b[0][midpt1]
                        # jy = b[1][midpt1]

                        # jx = b[0][-1] # most robust triggering i've seen is on last element.
                        # jy = b[1][-1]

                        jx = b[0][
                            -10]  # to filter out outlier... PROBLEM WASNT OUTLIER, it was 2 lures!!!! wait some more time for other one to fade away, before taking next ss.
                        jy = b[1][-10]

                        # print(rect_back)
                        # print(rect)
                        # print(jx, jy)
                        print('rect_back:{} rect:{} jx,jy:{}{}'.format(rect_back,rect,jx,jy))

                        # note: x and y were backwards coming out of the np.where function.

                        ix = jy + rect_back[0] + 200  # adjust relative to absolute screen coordinate
                        iy = jx + rect_back[1] + 750

                        print("IMAGE TRIGGERED!!!!")
                        print(ix, iy)
                        pyautogui.moveTo(ix, iy, 0.3)  # see if it triggered on the right spot

                        # don't fish yet; wait for audio trigger.
                        # pyautogui.keyDown("shiftleft")
                        # pyautogui.mouseDown(button='right')
                        # pyautogui.mouseUp(button='right')
                        # pyautogui.keyUp("shiftleft")

                        print('\nstarting audio check')

                        t1 = time.time()

                        # while rms==0:
                        # audioop.rms(fragment, width)
                        # 返回片段的均方根，即sqrt(sum(S_i^2)/n)。
                        # 这是衡量音频信号功率的指标。
                        rms = 0
                        n = 0
                        # while rms<90:
                        # while (rms<250):
                        # while (rms<250) and (time.time()-t1 < 1.0): # add check on time to filter out double-triggers from audio stream.
                        while 1:
                            data = stream.read(chunk)
                            rms = audioop.rms(data, 2)  # width=2 for format=paInt16
                            if n == 10:  # only print out every 10th one
                                print('rms value = %d' % rms)
                                n = 0
                            else:
                                n = n + 1

                            if rms > RMS:
                                if time.time() - t1 > 1.0:
                                    print('we heard the fish catch sound,rms={}'.format(rms))
                                    break  # out of while 1

                            if (time.time() - t1 > 30.0):  # it never caught; break out of while
                                print('FISH CATCH NEVER SOUNDED or something else went wrong.')
                                break

                            time.sleep(.1)

                        # print (rms)
                        print('AUDIO TRIGGERED!!!! rms value = %d' % rms)

                        time.sleep(.2)  # dont fish too early (will want to randomize all these)
                        print('ATTEMPTING TO FISH')
                        # pyautogui.keyDown("shiftleft")
                        pyautogui.mouseDown(button='right')
                        pyautogui.mouseUp(button='right')
                        # pyautogui.keyUp("shiftleft")

                        # sys.exit(1)
                        continue1 = 1
                    else:
                        break
