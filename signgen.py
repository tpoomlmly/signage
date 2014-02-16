
import os
import subprocess
import tempfile
import errno
from xml.sax.saxutils import escape

WITH_IMAGE    = 'with-image'
WITHOUT_IMAGE = 'without-image'

template_dir  = 'templates'
image_dir     = 'images'


def image_path(img):
    if os.path.exists(img):
        return os.path.realpath(img)
    path = os.path.join(image_dir, img)
    if os.path.exists(path):
        return os.path.realpath(path)
    return None


def template_path(img):
    path = os.path.join(template_dir, img)
    if os.path.exists(path):
        return os.path.realpath(path)
    return None


def do_sub(svg_str, key, val):
    val = val if val is not None else ""
    return svg_str.replace("$$__{}__$$".format(key), val)


def do_subs(svg_str, subs_dict):
    for key, val in subs_dict.items():
        svg_str = do_sub(svg_str, key, val)
    return svg_str


def generate_SVG(size, msg, output_fname, image_file=None):

    img_type = WITHOUT_IMAGE
    image = None
    if image_file is not None:
        image = image_path(image_file)
        if image is None:
            raise ValueError("Image file '{}' "
                             "does not exist".format(image_file))
        img_type = WITH_IMAGE

    svg_fname = "{size}-{type}.svg".format(size=size, type=img_type)
    svg_fname = template_path(svg_fname)

    if svg_fname is None:
        raise ValueError("Requested template for '{}' '{}' does "
                         "not exist".format(size, img_type))

    with open(svg_fname, 'r') as f:
        svg_str = f.read()

    with open(output_fname, 'w') as f:
        f.write(do_subs(svg_str, {'MESSAGE': msg,
                                  'IMAGE'  : image}))


def SVG_to_PDF(svg_fname, pdf_fname):
    try:
        subprocess.call(['inkscape', '-A', pdf_fname, svg_fname],
                        stderr=subprocess.PIPE)
    except OSError as err:
        if err.errno == errno.ENOENT:
            exit("Unable to generate sign, Inkscape may not be installed")
        else:
            raise

def generate_PDF(size, msg, output_fname, raw_message=False, image_file=None):
    if not raw_message:
        msg = escape(msg)
        msg = msg.replace("\n", "<flowRegionBreak />")
    tmp_fd, tmp_fname = tempfile.mkstemp()
    generate_SVG(size, msg, tmp_fname, image_file=image_file)
    SVG_to_PDF(tmp_fname, output_fname)
    os.close(tmp_fd)
    os.remove(tmp_fname)
