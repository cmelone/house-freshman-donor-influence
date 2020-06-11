# this script is used to extract output from a pdf file and put it in another file
# usage: python tik.py > file_output.txt
from tika import parser
file_data = parser.from_file('pdfs/114_cmtes.pdf')
print(file_data['content'])

# test
