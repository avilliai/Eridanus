
from run.resource_collector.service.zLibrary.canvas import create_book_image

# Create Zlibrary object and login


# Search for books

# Getting image content
def search_book(Z,book,num):
    results = Z.search(message=book, order="bestmatch")
    #print(results)
    result=[]
    for book_result in results['books'][:num]:
        try:
            p=create_book_image(book_result)
            result.append([f"book_id: {book_result['id']}\nhash: {book_result['hash']}",p])
        except:
            continue
    return result
def download_book(Z,book_id,hash):
    book={"id":str(book_id),"hash":hash}
    r=Z.downloadBook(book)
    filename, file_content = r
    path=f"data/text/books/{filename}"
    with open(path, "wb") as f:
        f.write(file_content)
    return path


