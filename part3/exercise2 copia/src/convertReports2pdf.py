import pdfkit
import glob
import imgkit
import img2pdf
import sys
import fitz

if __name__ == "__main__":
 for html_file in glob.glob("./part3/exercise2/reports/html/*.html"):
    png_filepath = html_file.replace("html", "png")
    pdf_filepath = html_file.replace("html", "pdf")
    imgkit.from_file(html_file, png_filepath)
    
     
    doc = fitz.open()                            # PDF with the pictures
    img = fitz.open(png_filepath)  # open pic as document
    rect = img[0].rect                       # pic dimension
    pdfbytes = img.convertToPDF()            # make a PDF stream
    img.close()                              # no longer needed
    imgPDF = fitz.open("pdf", pdfbytes)      # open stream as PDF
    page = doc.newPage(width=rect.width,   # new page with ...
                       height=rect.height)  # pic dimension
    page.showPDFpage(rect, imgPDF, 0)
    # image fills the page
    doc.save(pdf_filepath)
      
  
