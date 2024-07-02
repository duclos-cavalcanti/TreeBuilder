import glob
import os
import shutil

def slide(file:str, i:int):
    content =  f"---\n"
    content += f"layout: image\n"
    content += f"image: /plot/images/{file}\n"
    content +=  f"---\n"
    content +=  f"\n"
    content +=  f"# Slide {i}\n"
    
    return content

def export(dir:str):
    plotdir = os.path.join(os.getcwd(), "docs", "slidev", "plot")
    images  = glob.glob(os.path.join(plotdir, "images", '*.png'))
    mds     = glob.glob(os.path.join(plotdir, '*.md'))
    files   = []
    names   = []

    for f in images + mds:
        os.remove(f"{f}")
        print(f"REMOVING {f}")

    for f in os.listdir(dir):
        if f.endswith(".png"):
            name = f.split(".png")[0]
            names.append(name)
            files.append(f)
            src = os.path.join(dir, f)
            dst = os.path.join(os.getcwd(), "docs", "slidev", "plot", "images")
            shutil.copy(src, dst)
            print(f"COPYING {f} -> {dst}")

    paths = []
    for i, f in enumerate(files):
        content = slide(f, i + 1)
        path    = os.path.join(os.getcwd(), "docs", "slidev", "plot", f'{names[i]}.md')
        paths.append(f"./{names[i]}.md")
        
        with open(path, 'w') as file:
            file.write(content)
            print(f"WRITING -> {path}")

    with open(os.path.join(os.getcwd(), "docs", "slidev", "plot", "master.md"), 'w') as file:
        print(f"WRITING -> MASTER FILE")
        top =  "---\n"
        top += "theme: default\n"
        top += "colorSchema: light\n"
        top += "fonts:\n"
        top += "\tsans: Arial\n"
        top += "---\n"
        file.write(top)
        for p in paths:
            file.write(f'---\nsrc: {p}\n---\n\n')
