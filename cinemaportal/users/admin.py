from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, ModeratorRequest

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("username", "email", "role", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "email", "avatar_url")}),
        ("Permissions", {"fields": ("role", "is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )
    search_fields = ("username", "email")
    ordering = ("username",)


@admin.register(ModeratorRequest)
class ModeratorRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at", "message_preview")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    readonly_fields = ("created_at", "id")
    actions = ["approve_request", "reject_request"]
    
    def message_preview(self, obj):
        """Показать первые 50 символов сообщения"""
        if obj.message:
            return obj.message[:50] + "..." if len(obj.message) > 50 else obj.message
        return "—"
    message_preview.short_description = "Сообщение"
    
    def approve_request(self, request, queryset):
        """Одобрить заявку и присвоить роль модератора"""
        approved_count = 0
        for mod_req in queryset.filter(status='pending'):
            user = mod_req.user
            user.role = 'moderator'
            user.save()
            mod_req.status = 'approved'
            mod_req.save()
            approved_count += 1
        
        if approved_count > 0:
            self.message_user(
                request, 
                f"✅ Одобрено {approved_count} заявок. Пользователи теперь модераторы."
            )
        else:
            self.message_user(request, "ℹ️ Нет ожидающих заявок для одобрения")
    
    approve_request.short_description = "✅ Одобрить заявки и присвоить роль модератора"
    
    def reject_request(self, request, queryset):
        """Отклонить заявку"""
        rejected_count = queryset.filter(status='pending').update(status='rejected')
        
        if rejected_count > 0:
            self.message_user(request, f"❌ Отклонено {rejected_count} заявок")
        else:
            self.message_user(request, "ℹ️ Нет ожидающих заявок для отклонения")
    
    reject_request.short_description = "❌ Отклонить заявки"
