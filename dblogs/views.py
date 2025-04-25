from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from .models import DataBaseLogs
from .serializers import DataBaseLogsSerializer

# Create your views here.

@api_view(['GET'])
def get_database_logs(request):
    try:
        search = request.GET.get('search')
        level = request.GET.get('level')
        action = request.GET.get('action')
        version = request.GET.get('version')
        index = int(request.GET.get('index', 0))
        offset = int(request.GET.get('offset', 10))

        query = Q()
        if search:
            query &= Q(description__icontains=search) | Q(error__icontains=search)
        if level:
            query &= Q(level=level)
        if action:
            query &= Q(action=action)
        if version:
            query &= Q(webhook_version=version)

        logs = DataBaseLogs.objects.filter(query).order_by('-created_at')
        total = logs.count()
        logs = logs[index:index + offset]

        serializer = DataBaseLogsSerializer(logs, many=True)
        return Response({
            'success': True,
            'message': 'Logs fetched successfully',
            'total': total,
            'results': serializer.data
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
def delete_database_log(request):
    try:
        log_id = request.GET.get('log_id')
        if not log_id:
            return Response({'success': False, 'message': 'Log ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        log = DataBaseLogs.objects.filter(id=log_id).first()
        if not log:
            return Response({'success': False, 'message': 'Log not found'}, status=status.HTTP_400_BAD_REQUEST)

        log.delete()
        return Response({'success': True, 'message': 'Log deleted successfully'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
