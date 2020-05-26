import os
import time
from itertools import count, cycle
from pathlib import Path

import cv2
import matplotlib
from matplotlib import rc, animation
import matplotlib.colors as clr
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FFMpegWriter, FuncAnimation


COLOR_MAP = clr.LinearSegmentedColormap.from_list(
    "mycmap",
    [
        (1 - (1 - q) ** 4, c)
        for q, c in zip(
            np.linspace(0, 1, 20), cycle(["#ffff88", "#000000", "#ffaa00"])
        )
    ],
    N=2048,
)

MAX_FRAMES = 2
#
# MAX_ZOOM for these coordinates (0.357535415497125, 0.070571561552046)
# 1.7592187E13 can go higher but it is possible that it zooms into a non
# borderregion region but 1.7592187E13 is already a huge zoom-factor
#
MAX_ZOOM = 100000
RMIN, RMAX, IMIN, IMAX = -2.5, 1.5, -2, 2
OUTPUT_FILENAME = "OUTPUT.mp4"
IMAGES_PATH = Path("data")

def mandelbrot(
    rmin,
    rmax,
    rpoints,
    imin,
    imax,
    ipoints,
    max_iterations=1000,
    infinity_border=10
):
    image = np.zeros((rpoints, ipoints))
    r, i = np.mgrid[rmin:rmax:(rpoints * 1j), imin:imax:(ipoints * 1j)]
    c = r + 1j * i
    z = np.zeros_like(c)
    for k in range(max_iterations):
        z = z ** 2 + c
        mask = (np.abs(z) > infinity_border) & (image == 0)
        image[mask] = k
        z[mask] = np.nan
    return -image.T


def init():
    return plt.gca()


def animate(frame_number):
    #
    # Standard:  0.357535415497125, 0.070571561552046
    #
    r_center, i_center = 0.340037926617566, -0.051446751669 
    zoom = (frame_number / MAX_FRAMES) ** 3 * MAX_ZOOM + 1
    scalefactor = 1 / zoom
    rmin_ = (RMIN - r_center) * scalefactor + r_center 
    imin_ = (IMIN - i_center) * scalefactor + i_center
    rmax_ = (RMAX - r_center) * scalefactor + r_center
    imax_ = (IMAX - i_center) * scalefactor + i_center
    #
    # Increase rpoints and ipoints for better resolution.
    #
    image = mandelbrot(rmin_, rmax_, 1000, imin_, imax_, 1000)
    plt.axis('off', bbox_inches='tight', pad_inches = 0, tight_layout=True)
    plt.imshow(image, cmap=COLOR_MAP, interpolation='none')
    #
    # Counter starts with zero; so last frame number is MAX_FRAMES - 1.
    #
    print(
        "Frame number {} created; next frame: {} | {:.2%}".format(
            frame_number, frame_number + 1, (frame_number + 1) / MAX_FRAMES
        )
    )
    
    
def cut_frames(video_filename, target_path):
    video = cv2.VideoCapture(video_filename)
    try:
        #
        # create a directory named data
        #
        try:
            target_path.mkdir(exist_ok=True)
            #
            # if directory was not created then raise an error
            #
        except OSError:
            print("Error: Creating directory for data failed")
        else:
            #
            # frame
            #
            currentframe = 0
            for frame_number in count():
                is_ok, frame = video.read()
                if not is_ok:
                    break
                #
                # if video is still left continue creating images
                #
                image_filename = './data/frame' + str(currentframe) + '.jpg'
                print("Creating...", image_filename)
                #
                # writing the extracted images 
                #
                cv2.imwrite(image_filename, frame)
                #
                # increasing counter so that it will 
                # show how many frames are created
                #
                currentframe +=1
    finally:
        video.release()
        cv2.destroyAllWindows() 

        
def main():
    rc('animation', html='html5')
    fig_size = 8
    fig = plt.figure(
        figsize=(fig_size, fig_size), 
        dpi = 150,
        tight_layout=True
    )
    Writer = animation.writers['ffmpeg']
    writer = animation.FFMpegWriter(
        fps=2,
        metadata=dict(artist='Lukas Kretschmann'),
        bitrate = -1, 
        extra_args=['-pix_fmt', 'yuv420p'] 
    )
    print("Video Processing")
    start_time = time.monotonic()
    anim = animation.FuncAnimation(fig, animate, init_func=init, frames=MAX_FRAMES, interval=150)
    anim.save('OUTPUT.mp4', writer=writer, dpi = 150)
    end_time = time.monotonic()
    print("Took:", end_time - start_time, "Next Step: Frame slicing")
    start_time = time.monotonic()
    cut_frames(OUTPUT_FILENAME, IMAGES_PATH)
    end_time = time.monotonic()
    print("Took:", end_time - start_time, " FINISHED")
    
    
if __name__ == "__main__":
    main()