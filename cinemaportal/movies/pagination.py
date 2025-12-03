# movies/pagination.py
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class InfiniteScrollPagination(PageNumberPagination):
    page_size = 20                    
    page_size_query_param = 'page_size'  

    def get_paginated_response(self, data):
        return Response({
            "films": data,
            "hasMore": self.page.has_next()
        })


class ReviewsPagination(PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data):
        return Response({
            "reviews": data,
            "hasMore": self.page.has_next()
        })
