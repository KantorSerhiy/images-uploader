from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Image, User, Plan, ThumbnailSize, BinaryImage


@admin.register(User)
class User(UserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {
            "fields": (
                "first_name",
                "last_name",
                "email",
                "plan",
            )
        }
         ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                ),
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("username", "password1", "password2", "plan"),
            },
        ),
    )


admin.site.register(Image)
admin.site.register(Plan)
admin.site.register(ThumbnailSize)
admin.site.register(BinaryImage)
