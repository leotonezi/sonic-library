from app.models.review import Review
from app.services.base_service import BaseService

class ReviewService(BaseService[Review]):
    def __init__(self, db):
        super().__init__(db, Review)