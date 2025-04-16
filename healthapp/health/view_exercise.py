from rest_framework.response import Response
from rest_framework import viewsets, generics, status
from . import serializers
from rest_framework.decorators import action
from .models import  Exercise


class ExerciseViewSet(viewsets.ViewSet, generics.ListAPIView):
    queryset = Exercise.objects.prefetch_related('tag').filter(active=True)
    serializer_class = serializers.ExerciseDetailSerializer

    @action(methods=['get'], url_path='actual-result', detail=True)
    def get_actual_result(self, request, pk):
        actual_result = self.get_object().actualresult_set.filter(active=True)
        return Response(serializers.ActualResultSerializer(actual_result, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='predicted-result', detail=True)
    def get_predicted_result(self, request, pk):
        predicted_result = self.get_object().predictedresult_set.filter(active=True)
        return Response(serializers.ActualResultSerializer(predicted_result, many=True).data, status=status.HTTP_200_OK)

    @action(methods=['get'], url_path='instruct', detail=True)
    def get_predicted_result(self, request, pk):
        instruct = self.get_object().instruct_set.filter(active=True)
        return Response(serializers.InstructSerializer(instruct, many=True).data, status=status.HTTP_200_OK)