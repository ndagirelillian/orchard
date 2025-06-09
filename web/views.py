from django.shortcuts import render
from inventory.models import Category, MenuItem


# Create your views here.
def home(request):
    dishes = Category.objects.order_by('?')[:12]
    foods = MenuItem.objects.order_by('?')[:3]
    return render(request, "home.html", {"dishes": dishes, "foods": foods})


def menu(request):
    menu = MenuItem.objects.all()
    return render(request, "menu.html", {"menu": menu})

# def pdf_to_image(pdf_path, output_folder):
#     images = convert_from_path(pdf_path)
#     for i, image in enumerate(images):
#         image_path = f'{output_folder}/page_{i + 1}.jpg'
#         image.save(default_storage.path(image_path), 'JPEG')
#         print(f"Saved {image_path}")

def food_filter(request, id):
    food_item = MenuItem.objects.filter(category = id)
    food_category = Category.objects.get(id = id)
    return render(request, "foods_filter.html", {"food_item":food_item, "category":food_category})