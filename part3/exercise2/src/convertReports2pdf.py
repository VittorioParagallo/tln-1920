import pdfkit
import glob
if __name__ == "__main__":
 for html_file in glob.glob("./part3/exercise2/reports/html/*.html"):
   pdfkit.from_file(html_file, html_file.replace("html","pdf"))
  
