from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action

from common.models import Category, Message
from common.serializer import CategoryReadSerializer, CategoryWriteSerializer, MessageSerializer


# Create your views here.


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategoryReadSerializer

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CategoryWriteSerializer
        return CategoryReadSerializer

    @action(detail=False, methods=['get'])
    def parents(self, request, *args, **kwargs):
        parents = self.get_queryset().filter(subcategories__isnull=False).distinct()
        serializer = self.get_serializer(parents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def sub_categories(self, request, *args, **kwargs):
        parents = self.get_queryset().filter(subcategories__isnull=True).distinct()
        serializer = self.get_serializer(parents, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class MessageListViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer


    @swagger_auto_schema(method='get', operation_summary="List messages by category", manual_parameters=[
        openapi.Parameter('category_id', openapi.IN_QUERY, description="Category ID", type=openapi.TYPE_INTEGER),
    ])
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        category_id = request.query_params.get('category_id')
        if category_id is None:
            return Response({"error": "Category ID is required"}, status=400)

        messages = Message.objects.filter(category_id=category_id).order_by('-id')
        serializer = self.get_serializer(messages, many=True)
        return Response(serializer.data)
