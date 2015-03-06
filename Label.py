__author__ = 'keroth'

import barcode
import barcode.codex
import barcode.base
from barcode.writer import ImageWriter
import pyqrcode
import cairo
import cups
import subprocess
import Base32

# Constants:
# URL to the inventory page (example: 'http://i.ktt-ol.de/SPACE')
c_url = 'http://ktt-ol.de/i/'

# Filename for the QR code and barcode
# The filename for the barcode is not allowed to have a suffix because the create function already adds it.
c_img_c39 = "code39"
c_img_qr = "qr.png"

# Label size(pt) in mm 57/32
c_label_width = 161.6104
c_label_height = 90.7287

# Text font
c_font = 'Rockwell'

# PDF file
c_pdf_file = "/home/keroth/Schreibtisch/test.pdf"
# ***************************


# Functions
def draw_image(ic_ctx, iv_image, iv_top, iv_left, iv_height, iv_width):
    """Draw a scaled image on a given context."""
    image_surface = cairo.ImageSurface.create_from_png(iv_image)
    # calculate proportional scaling
    img_height = image_surface.get_height()
    img_width = image_surface.get_width()
    width_ratio = float(iv_width) / float(img_width)
    height_ratio = float(iv_height) / float(img_height)
    scale_xy = min(height_ratio, width_ratio)
    # scale image and add it
    ic_ctx.save()
    ic_ctx.scale(scale_xy, scale_xy)
    ic_ctx.translate(iv_left, iv_top)
    ic_ctx.set_source_surface(image_surface)

    ic_ctx.paint()
    ic_ctx.restore()
# ***************************


class Label (object):

    @staticmethod
    def create_barcode(code_id):

        # Visit this site for possible options:
        # https://pythonhosted.org/pyBarcode/writers/index.html#common-writer-options
        writer_options = {
            'module_width': 0.40,
            'module_height': 5.0,
            'quiet_zone': 0.0,
            # Deactivate the text because we will add it later using the cairo library.
            'write_text': False,
        }

        #
        code = barcode.codex.Code39(code_id, writer=ImageWriter(), add_checksum=False)
        code.save(c_img_c39, options=writer_options)

    @staticmethod
    def create_qrcode(code_id):
        url = pyqrcode.create(c_url + code_id)
        url.png(c_img_qr, scale=8, module_color=[0, 0, 0, 0xff], background=[0, 0, 0, 0])

    @staticmethod
    def create_pdf(code_id='ERROR', times=1):

        # Initialize the PDF file
        surface = cairo.PDFSurface(c_pdf_file, c_label_width, c_label_height)
        context = cairo.Context(surface)

        for i in range(times):

            # Create new code
            code_id = Label.create_code(code_id)

            # Create the barcode and QR code
            Label.create_barcode(code_id)
            Label.create_qrcode(code_id)

            # Display the barcode
            draw_image(context, c_img_c39+'.png', 5, 20, 30, 150)

            # write the URL below the barcode
            context.select_font_face(c_font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_NORMAL)
            context.set_font_size(8)
            context.move_to(5, 35)
            context.show_text(c_url + code_id)

            # Write the item id in the lower right corner
            context.select_font_face(c_font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
            context.set_font_size(22)
            context.move_to(65, 70)
            context.show_text(code_id)

            # Display the QR code
            draw_image(context, c_img_qr, 180, 20, 50, 50)

            # create new page
            context.show_page()

        # Print Page
        #Label.print_label()

    @staticmethod
    def print_label():
        subprocess.Popen(['lpr', c_pdf_file])

    @staticmethod
    def create_code(new_barcode='2000'):

        base32_code = Base32.base32decode(new_barcode)
        base32_code += 1
        new_barcode = Base32.base32encode(base32_code)

        new_barcode = '%4s' % new_barcode
        new_barcode = new_barcode.replace(' ', '0')

        print new_barcode
        return new_barcode