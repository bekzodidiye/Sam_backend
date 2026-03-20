from django.core.exceptions import ValidationError

def validate_image_size(value):
    filesize = value.size
    if filesize > 10 * 1024 * 1024:
        raise ValidationError("Rasm hajmi 10MB dan oshmasligi kerak")
