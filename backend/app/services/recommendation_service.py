from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from app.schemas.review import ReviewResponse
from app.schemas.book import BookResponse
import os
from dotenv import load_dotenv
load_dotenv()
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(temperature=0.3, model="gpt-3.5-turbo")

def generate_book_recommendations(user_reviews: list[ReviewResponse], all_books: list[BookResponse]) -> str:
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a book recommendation engine."),
        ("user", "Here is a list of books the user has reviewed and rated:\n\n{reviews}\n\nHere is a list of available books in our library:\n\n{book_list}\n\nBased on their preferences, recommend 3 new books and explain why. Be very straightforward.")
    ])

    reviews_text = "\n".join(f"{r.book_id}: {r.content} (Rating: {r.rate})" for r in user_reviews)
    books_text = "\n".join(f"{b.id}: {b.title} by {b.author} - {b.description}" for b in all_books)

    chain = prompt | llm
    return chain.invoke({"reviews": reviews_text, "book_list": books_text}).content