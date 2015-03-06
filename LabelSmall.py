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
c_img_arrow = "arrow.png"

# Label size(pt) in mm 210/297
c_label_width = 595.4069
c_label_height = 842.0754

# Seperators
c_31mm = 87.8934
c_105mm = 297.7034
c_padding_top = 25.00
# 17.0116



# Text font
c_font = 'Rockwell'

# PDF file
c_pdf_file = "/home/keroth/Schreibtisch/regal.pdf"

# Storage parameters
shelf = ['00', '05', '08', '11', '14', '16', '19', '21', '26', '31', '36', '40']
start_row = '1' 
start_col = 'A'
# ***************************


# Functions
def draw_image(ic_ctx, iv_image, iv_top, iv_left):
    """Draw a scaled image on a given context."""
    image_surface = cairo.ImageSurface.create_from_png(iv_image)
    ic_ctx.save()
    ic_ctx.set_source_surface(image_surface, iv_left, iv_top)

    ic_ctx.paint()
    ic_ctx.restore()
# ***************************


class Label (object):

    @staticmethod
    def create_barcode(code_id):

        # Visit this site for possible options:
        # https://pythonhosted.org/pyBarcode/writers/index.html#common-writer-options
        writer_options = {
            'module_width': 0.10,
            'module_height': 2.0,
            'quiet_zone': 0.0,
            'write_text': False,
        }

        #
        code = barcode.codex.Code39(code_id, writer=ImageWriter(), add_checksum=False)
        code.save(c_img_c39, options=writer_options)

    @staticmethod
    def create_qrcode(code_id):
        url = pyqrcode.create(c_url + code_id)
        url.png(c_img_qr, scale=2, module_color=[0, 0, 0, 0xff], background=[0, 0, 0, 0])

    @staticmethod
    def create_pdf(rows, cols):

        # Initialize the PDF file
        surface = cairo.PDFSurface(c_pdf_file, c_label_width, c_label_height)
        context = cairo.Context(surface)

        # Marker
        c_left = True
        label_rows = 0
        row = start_row

        for r in range(rows):
            col = start_col
            for c in range(cols):
                for i in shelf[:]:

                    spacing_right = 0

                    if label_rows == 9:
                        # create new page
                        context.show_page()
                        label_rows = 0

                    if label_rows == 0:
                        # Draw separator

                        context.set_line_width(0.1)
                        context.set_source_rgb(0, 0, 0)
                        context.move_to(297.7034, 0.0)
                        context.line_to(297.7034, c_label_height)
                        context.stroke()

                        context.set_line_width(0.1)
                        context.set_source_rgb(0, 0, 0)
                        context.move_to(0.0, c_padding_top + c_31mm * label_rows)
                        context.line_to(c_label_width, c_padding_top + c_31mm * label_rows)
                        context.stroke()

                    if not c_left:
                        spacing_right = c_105mm

                    spacing_down = c_31mm * label_rows

                    code_id = 'H' + row + col + i

                    # Create the barcode and QR code
                    Label.create_barcode(code_id)
                    Label.create_qrcode(code_id)

                    # Display the barcode
                    draw_image(context, c_img_c39+'.png', 3 + spacing_down + c_padding_top, 80 + spacing_right)

                    # Write the item id in the lower right corner
                    context.select_font_face(c_font, cairo.FONT_SLANT_NORMAL, cairo.FONT_WEIGHT_BOLD)
                    context.set_font_size(22)
                    context.move_to(80 + spacing_right, 62 + spacing_down + c_padding_top)
                    context.show_text(code_id)

                    # Display the QR code
                    draw_image(context, c_img_qr, 12 + spacing_down + c_padding_top, 10 + spacing_right)

                    if i == '00':
                    # Add Arrow
                        draw_image(context, c_img_arrow, 12 + spacing_down + c_padding_top, 220 + spacing_right)

                    # change side
                    if c_left:
                        c_left = False
                    else:
                        c_left = True
                        label_rows += 1

                        context.set_line_width(0.1)
                        context.set_source_rgb(0, 0, 0)
                        context.move_to(0.0, c_padding_top + c_31mm * label_rows)
                        context.line_to(c_label_width, c_padding_top + c_31mm * label_rows)
                        context.stroke()

                col = Label.increase(col)

            row = Label.increase(row)

        # Print Page
        #Label.print_label()

    @staticmethod
    def print_label():
        subprocess.Popen(['lpr', c_pdf_file])

    @staticmethod
    def increase(new_barcode):

        base32_code = Base32.base32decode(new_barcode)
        base32_code += 1
        new_barcode = Base32.base32encode(base32_code)

        new_barcode = '%1s' % new_barcode

        return new_barcode