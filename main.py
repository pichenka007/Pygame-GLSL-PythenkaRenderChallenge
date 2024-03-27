import pygame as pg
import pygame_shaders
import glm
import time
import cv2
import numpy as np
from moviepy.editor import *

#https://www.shadertoy.com/view/Ms2SDc

pg.init()

clock = pg.time.Clock()

SAVE = False
OUT_NAME = "under-hexagons"
SOUND_NAME = "Toby_Fox_-_Temmie_Village_64962790.mp3" # if the video should remain without sounds, specify ""

W, H = int(1920/2), int(1080/2)
FPS = 30

sc = pg.display.set_mode((W, H), pg.OPENGL | pg.HWSURFACE | pg.DOUBLEBUF)

lol = pg.Surface((W, H))
display = pg.Surface((W, H))

#screen_shader = pygame_shaders.Shader((W, H), (W, H), (0, 0), "virtex.txt", "frag.txt", display) # <- Here we supply our default display, it's this display which will be displayed onto the opengl context via the screen_shader

shader = pygame_shaders.Shader((W, H), (W, H), (0, 0), "virtex.txt", "frag.txt", display) #<- give it to our shader

out = cv2.VideoWriter(OUT_NAME+".avi", cv2.VideoWriter_fourcc('M','J','P','G'), FPS, (W, H)) #создаем видео

def bytes_to_image_opencv(byte_data):
	np_arr = np.frombuffer(byte_data, np.uint8)
	np_arr = np_arr.reshape((H, W, 3))
	np_arr = np_arr[::-1]
	return np_arr


start_frame = 0
if SOUND_NAME != "":
	end_frame = round(AudioFileClip(SOUND_NAME).duration*FPS)
	if not SAVE:
		pg.mixer.init()
		song = pg.mixer.music.load(SOUND_NAME)
else:
	end_frame = FPS*60
frame = start_frame
totaltime = 0

t = time.time()
if not SAVE:
	pg.mixer.music.play()

while True:
	for event in pg.event.get():
		if event.type == pg.QUIT:
			exit()

	if frame >= end_frame:
		out.release() #генерируем
		cv2.destroyAllWindows() #завершаем
		if SOUND_NAME != "":
			import moviepy.editor as mpe
			my_clip = mpe.VideoFileClip(OUT_NAME+".avi") #наш видео-файл со скриншотами
			my_clip.write_videofile(OUT_NAME+".mp4", audio=SOUND_NAME)
		os.remove(f"{OUT_NAME}.avi")
		print(f"all time: {round((time.time()-t)/60, 1)} min")
		exit()
	tt = time.time()

	if SAVE:
		shader.shader_data = {"iTime": [frame/FPS],
							  "iResolution": [W, H]}
	else:
		shader.shader_data = {"iTime": [time.time()-t],
							  "iResolution": [W, H]}

	"""
	#shader.send("iResolutionx", [screen.get_size()[0]])
	#shader.send("iResolutiony", [screen.get_size()[1]])
	#shader.send("iTime", [time.time()-t])
	"""

	ttt = time.time()

	shader.render()

	render_time = time.time()-ttt

	frame += 1

	if not SAVE:
		sc.blit(display, (0, 0))

		pg.display.flip()
	ttt = time.time()

	if SAVE:
		cv2_img = bytes_to_image_opencv(shader.ctx._screen.read())

		img_bgr = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)

	convert_time = time.time()-ttt

	ttt = time.time()

	if SAVE:
		out.write(img_bgr)

	save_time = time.time()-ttt
	if SAVE:
		print("render time: {} | convert time: {} | save time: {} | {} / {} | total time {} minuts".format(str(round(render_time, 5))+" "*(7-len(str(round(render_time, 5)))), str(round(convert_time, 5))+" "*(7-len(str(round(convert_time, 5)))), str(round(save_time, 5))+" "*(7-len(str(round(save_time, 5)))), end_frame, frame, round((time.time()-tt)*(end_frame-frame)/FPS, 1)))

	if not SAVE:
		clock.tick(FPS)