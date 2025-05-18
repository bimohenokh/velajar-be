# from django.contrib.auth import get_user_model
# from django.contrib.auth.models import Group
# from rest_framework import permissions, viewsets
#
# from taschoolassistant.coba.serializers import UserSerializer, GroupSerializer
#
# User = get_user_model()
#
# class UserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = User.objects.all().order_by('-date_joined')
#     serializer_class = UserSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
#
# class GroupViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows groups to be viewed or edited.
#     """
#     queryset = Group.objects.all().order_by('name')
#     serializer_class = GroupSerializer
#     permission_classes = [permissions.IsAuthenticated]
#
import asyncio
import time

import adrf.views
from asgiref.sync import sync_to_async
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.views import APIView


def coba_blocking_view(request, number):
    """
    A blocking view that simulates a long-running process.
    """
    print(f"Request number {number} received.")
    time.sleep(5)  # Simulate a long-running process
    print(f"Request number {number} finish processing.")
    return HttpResponse(f"Request number {number} finish processing.")


async def coba_non_blocking_view(request, number):
    """
    A non-blocking view that simulates a long-running process.
    """

    print(f"Request {number}: Received request for non-blocking task.")
    await asyncio.sleep(5)
    print(f"Request {number}: Non-blocking task finished.")
    return HttpResponse(f"Request {number} (non-blocking) finished.")


def cpu_intensive_task(iterations):
    """A simple function that consumes CPU."""
    print(f"Starting CPU bound task ({iterations} iterations)...")
    start_time = time.monotonic()
    result = 0
    # This loop keeps the CPU busy and holds the GIL
    for i in range(iterations):
        result += i*i # Some arbitrary calculation
    end_time = time.monotonic()
    duration = end_time - start_time
    print(f"Finished CPU bound task in {duration:.4f} seconds.")
    return result, duration

def coba_cpu_bound_view(request, number):
    """
    A view that simulates a CPU-intensive process (holds GIL).
    """
    # Adjust this number based on your machine speed.
    # Aim for something that takes ~0.5-2 seconds to run once.
    # Start lower (e.g., 10_000_000) and increase if it's too fast.
    iterations = 10_000_000 # <--- !! Adjust this !!

    print(f"\nRequest {number}: Received request for CPU bound task.")
    _result, duration = cpu_intensive_task(iterations)
    print(f"Request {number}: Finished CPU bound task on server.")
    return HttpResponse(f"Request {number} (CPU bound) finished processing in {duration:.4f}s.")

class CobaNonBlockingSyncView(adrf.views.APIView):
    # @sync_to_async
    async def get(self, request, number):
        """
        A non-blocking view that simulates a long-running process.
        """
        print(f"Request number {number} received.")
        time.sleep(5)  # Simulate a long-running process
        print(f"Request number {number} finish processing.")
        return Response(f"Request number {number} finish processing.")


class CobaNonBlockingASyncView(adrf.views.APIView):
    # @sync_to_async
    async def get(self, request, number):
        """
        A non-blocking view that simulates a long-running process.
        """
        print(f"Request number {number} received.")
        await asyncio.sleep(5)
        print(f"Request number {number} finish processing.")
        return Response(f"Request number {number} finish processing.")