import pymupdf

# this helper function convert  raw pdf data to string text found in pdf


def pdf_to_text(contents: bytes) -> str:
    # Open the PDF file from the provided binary contents
    pdf = pymupdf.open(stream=contents, filetype="pdf")

    # Initialize an empty string to store the extracted text
    text = ""

    # Iterate over each page in the PDF
    for page in pdf:
        # Extract the text from the current page and append it to the text variable
        text += page.get_text()

    # Return the extracted text
    return text