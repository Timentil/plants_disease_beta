from django.http import HttpResponse
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .predict_images import predict
# from djangoproject.main_db import get_diseases_list, get_disease, add_user, login_user, save_story, get_story
from main_db import get_diseases_list, get_disease, add_user, login_user, save_story, get_story
import base64


def recognition_page(request):
    return render(request, 'main/recognition.html')


def result_page(request):
    return render(request, 'main/result.html')


def index_page(request):
    return render(request, 'main/index.html')


class PredictAPI(APIView):
    def get(self, request):
        return Response({'method': 'predict_images', 'request': 'get'})

    def post(self, request):
        return Response(get_disease(request.data))


class GetDiseasesAPI(APIView):
    def get(self, request):
        return Response({'method': 'get_diseases_list', 'request': 'get'})

    def post(self, request):
        return Response(get_diseases_list(name=request.data["name"], plant=request.data["plant"]))


class AddUserAPI(APIView):
    def get(self, request):
        return Response({'method': 'add_user', 'request': 'get'})

    def post(self, request):
        res = add_user(request.data['email'], request.data['password'], request.data['FIO'])
        if res == 0:
            return Response({'answer': 'Пользователь с такой почтой уже существует'})
        elif res == 1:
            return Response({'answer': 'Длина пароля должна быть от 8 до 20 символов'})
        else:
            return Response({'answer': 'success'})


class LoginUserAPI(APIView):
    def get(self, request):
        return Response({'method': 'login_user', 'request': 'get'})

    def post(self, request):
        res = login_user(request.data['email'], request.data['password'])
        if res == 0:
            return Response({'answer': 'Пользователь с такой почтой не зарегистрирован'})
        elif res == 1:
            return Response({'answer': 'Неверный пароль'})
        else:
            return Response({'answer': 'success', 'user_id': res[1], 'FIO': res[2]})


class GetStoryAPI(APIView):
    def get(self, request):
        return Response({'method': 'get_story', 'request': 'get'})

    def post(self, request):
        return Response(get_story(request.data["user_id"]))


class TestSaveImages(APIView):
    def post(self, request):
        answer = {"data": []}
        count = 0
        for image in request.data["images"]:
            image_decode = base64.b64decode(image['image'])
            with open(f'main/test_save_images/image{count}.jpg', 'wb') as image_result:
                image_result.write(image_decode)
            image_base_64 = base64.b64encode(image_decode)
            answer["data"].append({"image": image_base_64, "text": "Изображение сохранено"})
            count += 1
        return Response(answer)


def success(request):
    return HttpResponse('successfully uploaded')