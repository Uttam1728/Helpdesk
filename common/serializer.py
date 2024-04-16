from rest_framework import serializers

from common.models import Category, Message


class CategoryReadSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    has_subcategories = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ['id', 'category_name', 'answer', 'contact_person', 'is_active', 'created_on', 'updated_on', 'subcategories', 'has_subcategories']
        read_only_fields = ['id', 'created_on', 'updated_on']

    def get_subcategories(self, obj):
        subcategories = obj.subcategories.all()
        return CategoryReadSerializer(subcategories, many=True).data

    def get_has_subcategories(self, obj):
        return obj.subcategories.exists()

class CategoryWriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'category_name', 'answer', 'contact_person', 'parent_category']
        read_only_fields = ['id', ]


# serializers.py
class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'sender', 'content', 'timestamp']
