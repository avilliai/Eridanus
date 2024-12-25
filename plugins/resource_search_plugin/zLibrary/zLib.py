
from plugins.resource_search_plugin.zLibrary.canvas import create_book_image

# Create Zlibrary object and login


# Search for books

# Getting image content
def search_book(Z,book,num):
    results = Z.search(message=book, order="bestmatch")
    #print(results)
    result=[]
    for book_result in results['books'][:num]:
        p=create_book_image(book_result)
        result.append([f"book_id: {book_result['id']}",p])
    return result
def download_book(Z,book_id):
    Z.saveBook(book_id)
