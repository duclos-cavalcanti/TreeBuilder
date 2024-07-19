import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from .args import pargs

def merge(files):
    imgs = [mpimg.imread(f) for f in files]
    fig, axs = plt.subplots(1, len(imgs), figsize=(pargs.w * len(imgs), pargs.h))

    for ax, image in zip(axs, imgs):
        ax.imshow(image)
        ax.axis('off')

    plt.tight_layout()
    return plt, fig 
