# rest_framework
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# account_books
from .models import AccountBook
from .serializers import  AccountBookCreateSerializer

# project
from payhere.permissions import IsOwner


class AccountBookView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = AccountBookCreateSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

