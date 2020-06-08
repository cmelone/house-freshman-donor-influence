from tika import parser
file_data = parser.from_file('pdfs/114_cmtes.pdf')
print(file_data['content'])