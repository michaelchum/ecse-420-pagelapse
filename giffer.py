from images2gif import writeGif
from PIL import Image
import os, sys
import argparse

def giffer(files, xsize, ysize, framelen, dither, loops, outfile):
	for i, fname in enumerate(files):
		if not os.path.isfile(fname):
			del args[i]
	
	images = [Image.open(fname) for fname in files]
	for im in images:
		im.thumbnail((xsize, ysize), Image.ANTIALIAS)

	writeGif(filename=outfile, images=images, duration=framelen, dither=dither, loops=loops, width=xsize, height=ysize)

if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--xsize', default=200, type=int)
	parser.add_argument('--ysize', default=200, type=int)
	parser.add_argument('--framelen', default=0.2, type=float)
	parser.add_argument('--loops', default=0, type=int)
	parser.add_argument('--dither', default=True, type=bool)
	parser.add_argument('--outfile', default='out.gif', type=str)
	parser.add_argument('files', nargs='*')
	args = parser.parse_args()
	giffer(files=args.files, xsize=args.xsize, ysize=args.ysize, framelen=args.framelen, dither=args.dither, loops=args.loops, outfile=args.outfile)

