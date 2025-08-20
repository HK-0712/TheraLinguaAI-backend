# backend/urls.py

from django.contrib import admin
from django.urls import path, include # <-- 在這裡加入 include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 新增這一行：
    # 告訴 Django，所有以 'api/' 開頭的 URL，
    # 都應該被轉交給 'api.urls' 這個檔案去處理。
    path('api/', include('api.urls')),
]