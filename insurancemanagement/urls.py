from django.contrib import admin
from django.urls import path, include
from insurance import views
from django.contrib.auth.views import LogoutView, LoginView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('customer/', include('customer.urls')),
    path('', views.home_view, name=''),
    path('logout', LogoutView.as_view(template_name='insurance/logout.html'), name='logout'),
    path('aboutus', views.aboutus_view),
    path('contactus', views.contactus_view),
    path('afterlogin', views.afterlogin_view, name='afterlogin'),

    # --- Auth ---
    path('adminlogin', LoginView.as_view(template_name='insurance/adminlogin.html'), name='adminlogin'),
    path('admin-dashboard', views.admin_dashboard_view, name='admin-dashboard'),

    # --- Clients ---
    path('admin-view-customer', views.admin_view_customer_view, name='admin-view-customer'),
    path('update-customer/<int:pk>', views.update_customer_view, name='update-customer'),
    path('delete-customer/<int:pk>', views.delete_customer_view, name='delete-customer'),

    # --- Catégories ---
    path('admin-category', views.admin_category_view, name='admin-category'),
    path('admin-add-category', views.admin_add_category_view, name='admin-add-category'),
    path('admin-view-category', views.admin_view_category_view, name='admin-view-category'),
    path('admin-update-category', views.admin_update_category_view, name='admin-update-category'),
    path('update-category/<int:pk>', views.update_category_view, name='update-category'),
    path('admin-delete-category', views.admin_delete_category_view, name='admin-delete-category'),
    path('delete-category/<int:pk>', views.delete_category_view, name='delete-category'),

    # --- Dossiers ---
    path('admin-dossier', views.admin_dossier_view, name='admin-dossier'),
    path('admin-add-dossier', views.admin_add_dossier_view, name='admin-add-dossier'),
    path('admin-view-dossier', views.admin_view_dossier_view, name='admin-view-dossier'),
    path('update-dossier/<int:pk>', views.update_dossier_view, name='update-dossier'),
    path('delete-dossier/<int:pk>', views.delete_dossier_view, name='delete-dossier'),

    # --- Véhicules ---
    path('admin-add-vehicle', views.admin_add_vehicle_view, name='admin-add-vehicle'),
    path('admin-view-vehicle', views.admin_view_vehicle_view, name='admin-view-vehicle'),

    # --- Remise Compagnie ---
    path('admin-view-remise', views.admin_view_remise_view, name='admin-view-remise'),
    path('admin-add-remise', views.admin_add_remise_view, name='admin-add-remise'),

    # --- Questions ---
    path('admin-question', views.admin_question_view, name='admin-question'),
    path('update-question/<int:pk>', views.update_question_view, name='update-question'),
]
