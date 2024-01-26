from keras.models import load_model
import keras.utils as image
import numpy as np
import heapq
import json


# all_class = ['Apple_Apple_scab', 'Apple_Black_rot', 'Apple_Cedar_apple_rust', 'Apple_healthy',
#              'Cherry_including_sour_healthy', 'Cherry_including_sour_Powdery_mildew',
#              'Corn_maize_Cercospora_leaf_spot_Gray_leaf_spot', 'Corn_maize_Common_rust', 'Corn_maize_healthy', 'Corn_maize_Northern_Leaf_Blight', 'Grape_Black_rot',
#              'Grape_Esca_Black_Measles', 'Grape_healthy', 'Grape_Leaf_blight_Isariopsis_Leaf_Spot)',
#              'Peach_Bacterial_spot', 'Peach_healthy',
#              'Pepper_bell_Bacterial_spot', 'Pepper_bell_healthy',
#              'Potato_Early_blight', 'Potato_healthy', 'Potato_Late_blight',
#              'RiceLeafs_Brown_Spot', 'RiceLeafs_Healthy', 'RiceLeafs_Hispa', 'RiceLeafs_Leaf_Blast',
#              'Squash_Powdery_mildew',
#              'Strawberry_healthy', 'Strawberry_Leaf_scorch',
#              'Tomato_Bacterial_spot', 'Tomato_Early_blight', 'Tomato_healthy', 'Tomato_Late_blight',
#              'Tomato_Leaf_Mold', 'Tomato_Septoria_leaf_spot', 'Tomato_Spider_mites_Two-spotted_spider_mite',
#              'Tomato_Target_Spot', 'Tomato_Tomato_mosaic_virus', 'Tomato_Tomato_Yellow_Leaf_Curl_Virus',
#              'Wheat_Brown_rust', 'Wheat_Healthy', 'Wheat_Septoria', 'Wheat_Stripe_rust', 'Wheat_Yellow_rust']

# для бета версии
all_class = ['Corn_maize_Cercospora_leaf_spot_Gray_leaf_spot', 'Corn_maize_Common_rust',
             'Corn_maize_healthy', 'Corn_maize_Northern_Leaf_Blight',
             'Potato_Early_blight', 'Potato_healthy', 'Potato_Late_blight',
             'Wheat_Brown_rust', 'Wheat_Yellow_rust']


def get_treatment(disease_name):
    try:
        with open(f'media/doctor_files/{disease_name}.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            treatment = data['treatment']
        return treatment
    except FileNotFoundError:
        return False


def preprocess_images(filename):
    img = image.load_img(f'main/load_image/{filename}', target_size=(256, 256))
    result_image = image.img_to_array(img)
    result_image /= 255
    result_image = np.expand_dims(result_image, axis=0)
    return result_image


def predict(filename):
    model = load_model(r".\main\model\beta_model_point_2.h5")
    image = preprocess_images(filename)
    result = [dict(), dict(), dict()]
    res = model.predict(np.array(image))
    max_values = heapq.nlargest(3, zip(res[0], all_class))
    for i in range(3):
        acc = round(max_values[i][0] * 100, 2)
        if acc > 50:
            result[i]['disease'] = max_values[i][1]
            result[i]['accuracy'] = acc
        else:
            continue
    return result
