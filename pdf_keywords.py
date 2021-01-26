from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import PDFPageAggregator
from pdfminer3.converter import TextConverter
import io
import glob
from tqdm import tqdm
import re
import sys


KEYWORDS = [] # insert keyword here
FILES_DIR = '' # insert path here
MATCH_OUTPUT_FILE = './pdf_match.txt'
NO_MATCH_OUTPUT_FILE = './pdf_no_match.txt'
ERROR_OUTPUT_FILE = './errors.txt'



def words_in_string(word_list, string_to_check):
    """
    Returns a set of words in a given string given a list
    """
    return set(word_list).intersection(string_to_check.split())


def pdf_get_text(file_path):
    """
    Returns the text in a pdf file
    """
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)

    with open(file_path, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                    caching=True,
                                    check_extractable=True):
            page_interpreter.process_page(page)

        text = fake_file_handle.getvalue()

    # close open handles
    converter.close()
    fake_file_handle.close()

    return text


def main():
    files = glob.glob(FILES_DIR, recursive=True)
    error_count = 0
    success_count = 0
    total_total_match_count = 0
    

    for item in tqdm(files):
        print('Opening: {}'.format(item))

        file_dict = dict()

        try:
            text = pdf_get_text(item)
            
            for keyword in KEYWORDS:
                count = sum(1 for _ in re.finditer(r'\b%s\b' % re.escape(keyword), text))

                file_dict[keyword] = count

            total_match_count = sum(file_dict.values())
            total_total_match_count += total_match_count

            if total_match_count != 0:
                with open(SUCCESS_OUTPUT_FILE, 'a+') as f:
                    f.write('===== START =====\n')
                    f.write('FILE: {}\n'.format(item))

                    for word, count in file_dict.items():
                        if count != 0:
                            line_to_write = "'{}' appears {} times\n".format(word, count)
                            f.write(line_to_write)

                    f.write('====== END ======\n\n')

                print("{} contains {} keywords".format(item, total_match_count))
            else:
                print("{} contains no keywords".format(item))
                with open(NO_MATCH_OUTPUT_FILE, 'a+') as f:
                    f.write('FILE: {} contains no keywords\n'.format(item))

            success_count += 1

        except Exception as e:
            print('Error occured, writing to error file...')
            error_count += 1
            with open(ERROR_OUTPUT_FILE, 'a+') as f:
                f.write('Error occured in {filename}: {error}\n'.format(filename=item, error=e))


    print('====== END OF SCRIPT SUMMARY ======')
    print('Files parsed: {}'.format(len(files)))
    print('Successfully parsed: {}'.format(success_count))
    print('Failed to parse: {}'.format(error_count))
    print('Total number of keywords found: {}'.format(total_total_match_count))
    print('=============== END ===============')



if __name__ == '__main__':
    if len(KEYWORDS) == 0:
        print("Please enter keywords in list")
        sys.exit()
    elif FILES_DIR == '':
        print("Please enter directory of files to parse")
        sys.exit()
    
    main()
