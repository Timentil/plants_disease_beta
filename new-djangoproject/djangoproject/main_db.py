import psycopg2
import os
import base64
from main.predict_images import predict
import datetime
from djangoproject.settings import DATABASES
from PIL import Image
from io import BytesIO

try:
    connect = psycopg2.connect(host=DATABASES["main_db"]["host"],
                               user=DATABASES["main_db"]["user"],
                               password=DATABASES["main_db"]["password"],
                               database=DATABASES["main_db"]["db_name"])
    cur = connect.cursor()
except Exception as ex:
    print('ERROR: ', ex)


def get_diseases_list(name='', plant=''):
    answer = {"answer": []}
    cur.execute("SELECT * FROM plant_diseases")
    all_finds = cur.fetchall()
    for el in all_finds:
        cur.execute(f"SELECT name FROM plants WHERE id = '{el[1]}'")
        plant_name = cur.fetchone()
        cur.execute(f"SELECT name FROM diseases WHERE id = '{el[2]}'")
        name_disease = cur.fetchone()
        if name != '' and plant == '':
            if name == name_disease[0]:
                answer["answer"].append(
                    {"id": el[0], "plant": plant_name[0], "disease": name_disease[0], "treatment": el[3],
                     "prophylaxis": el[4], "image": el[5]})
        elif name == '' and plant != '':
            if plant == plant_name[0]:
                answer["answer"].append(
                    {"id": el[0], "plant": plant_name[0], "disease": name_disease[0], "treatment": el[3],
                     "prophylaxis": el[4], "image": el[5]})
        elif name != '' and plant != '':
            if plant == plant_name[0] and name == name_disease[0]:
                answer["answer"].append(
                    {"id": el[0], "plant": plant_name[0], "disease": name_disease[0], "treatment": el[3],
                     "prophylaxis": el[4], "image": el[5]})
        else:
            answer["answer"].append(
                {"id": el[0], "plant": plant_name[0], "disease": name_disease[0], "treatment": el[3],
                 "prophylaxis": el[4], "image": el[5]})
    return answer


def get_disease(data):
    result = {"data": []}
    count = 0

    # Проверка на наличие папки для загруженных изображений. В проекте репозитория отсутствовала и вылетала ошибка
    if not os.path.isdir('main/load_image'):
        os.makedirs('main/load_image')
    print(data)

    image = data['image'].read()
    image_open = Image.open(BytesIO(image))
    image_open = image_open.convert('RGB')
    buffer = BytesIO()
    image_open.save(buffer, format='jpeg')
    jpeg_data = buffer.getvalue()

    with open(f'main/load_image/image{count}.jpg', 'wb') as file:
        file.write(jpeg_data)
    # image_base_64 = base64.b64encode(image_decode)
    answer = predict(f'image{count}.jpg')
    if len(answer[0]) == 0 and len(answer[1]) == 0 and len(answer[2]) == 0:
        result['data'].append({'disease': 'heathy'})
        # модель определяет здоровые или нет?
    else:
        for i in range(len(answer)):
            if len(answer[i]) != 0:
                # Определение класса теперь по кодовому имени равному значению класса
                cur.execute(
                    f"SELECT pd.id, pd.treatment, pd.prophylaxis, pd.image, p.name, d.name FROM plant_diseases pd JOIN plants p ON pd.plant_id = p.id JOIN diseases d ON pd.diseases_id = d.id WHERE code_name = '{answer[i]['disease']}'")
                platn_dis = cur.fetchone()
                answer[i]['id'] = platn_dis[0]
                answer[i]['disease'] = platn_dis[5]
                answer[i]['plant'] = platn_dis[4]
                answer[i]['treatment'] = platn_dis[1]
                answer[i]['prophylaxis'] = platn_dis[2]
                answer[i]['image'] = base64.b64encode(image) # Убрал ['image']
                answer[i]['image_disease'] = platn_dis[3]
                result['data'].append(answer[i])
                count += 1
                save_story(data["user_id"], platn_dis[0], answer[i]["accuracy"], '123') # Убрал ['image']
    return result


def add_user(email, password, fio):
    cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
    result = cur.fetchall()
    if len(result) != 0:
        return 0
    else:
        if 8 <= len(password) <= 20:
            cur.execute(f"INSERT INTO users (email, password, FIO) VALUES ('{email}', '{password}', '{fio}')")
            connect.commit()
            return 2
        else:
            return 1


def login_user(email, password):
    cur.execute(f"SELECT * FROM users WHERE email = '{email}'")
    result = cur.fetchall()
    if len(result) == 0:
        return 0
    else:
        if result[0][2] == password:
            id = result[0][0]
            fio = result[0][3]
            return 2, id, fio
        else:
            return 1


def save_story(user_id, plant_diseases_id, probability, image):
    datenow = str(datetime.date.today())
    cur.execute(f"INSERT INTO story (user_id, plant_diseases_id, probability, image, date_created) "
                f"VALUES ('{user_id}', '{plant_diseases_id}', '{probability}', '{image}', '{datenow}')")
    connect.commit()


def get_story(user_id):
    cur.execute(f"SELECT * FROM story WHERE user_id = '{user_id}'")
    story_list = cur.fetchall()
    result = {"data": []}
    for el in story_list:
        cur.execute(f"SELECT * FROM plant_diseases WHERE id = '{el[2]}'")
        plant_diseases = cur.fetchone()
        cur.execute(f"SELECT name FROM plants WHERE id = '{plant_diseases[1]}'")
        plant_name = cur.fetchone()
        cur.execute(f"SELECT name FROM diseases WHERE id = '{plant_diseases[2]}'")
        name_disease = cur.fetchone()
        result["data"].append(
            {"id": el[0], "plant": plant_name[0], "disease": name_disease[0], "treatment": plant_diseases[3],
             "prophylaxis": plant_diseases[4], "probability": el[3], "image": el[4], "datetime": el[5]})
    return result
