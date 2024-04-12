from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.decorators import action

from common.models import Category
from common.serializer import CategoryReadSerializer, CategoryWriteSerializer


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
