from django.urls import path

from taschoolassistant.coba.views import (
    coba_blocking_view,
    coba_cpu_bound_view,
    coba_non_blocking_view,
    CobaNonBlockingSyncView,
    CobaNonBlockingASyncView,
)

urlpatterns = [
    path("blocking/<int:number>/", coba_blocking_view, name="coba-blocking-view"),
    path("non-blocking/<int:number>/", coba_non_blocking_view, name="coba-non-blocking-view"),
    path('cpu/<int:number>/', coba_cpu_bound_view, name='coba_cpu_bound'),
    path("sync/non-blocking/<int:number>/", CobaNonBlockingSyncView.as_view(), name="coba-sync-non-blocking-view"),
    path("async/adrf/<int:number>/", CobaNonBlockingASyncView.as_view(), name="adrf-async-view"),

]