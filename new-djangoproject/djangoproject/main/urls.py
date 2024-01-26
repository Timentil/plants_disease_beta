from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('', index_page),
    path('recognition.html', recognition_page),
    path('result.html', result_page),
    path('success', success, name='success'),
    path('api/v1/predict_images', PredictAPI.as_view()),
    path('api/v1/get_diseases', GetDiseasesAPI.as_view()),
    path('api/v1/test_save_images', TestSaveImages.as_view()),
    path('api/v1/add_user', AddUserAPI.as_view()),
    path('api/v1/login_user', LoginUserAPI.as_view()),
    path('api/v1/get_story', GetStoryAPI.as_view())
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
