from django.db import models
from django.conf.urls import url
from console import views
from django.urls import path

from console.src import autopilot, data_folders, drive, job_creation , jobs , settings,authentification


# Create your models here.
urlpatterns = [
    path('', views.index, name='index'),
    url(r'^availability/display/(?P<name>[\w@%.]+)/$', job_creation.display_availability, name='display_availability'),
    url(r'^login/(?P<accessToken>[\w@%.]+)/$', authentification.login, name='login'),
    url(r'^logout/$', authentification.logout, name='logout'),

    url(r'^get_user_info/$', authentification.get_user_info, name='get_user_info'),

    url(r'^settings/$', settings.save_credentials, name='save_credentials'),
    url(r'^settings/credentials/$', settings.save_credentials, name='save_credentials'),
    url(r'^settings/githubRepository/$', settings.save_github_repo, name='save_github_repo'),

    url(r'^settings/local/directory/$', settings.save_local_directory, name='save_local_directory'),
    url(r'^data/empty/folder/delete/$', data_folders.delete_empty_folders, name='delete_empty_folders'),

    url(r'^data/$', data_folders.display_data_folders, name='data_folders'),
    url(r'^job/create/$', job_creation.create_job, name='create_job'),
    url(r'^jobs/$', jobs.list_jobs, name='list_jobs'),
    url(r'^jobs/success/$', jobs.list_jobs_success, name='list_jobs_success'),
    url(r'^settings/controllers/$', settings.save_controller_settings, name='save_controller_settings'),
    url(r'^jobs/(?P<message>[\w@%.]+)/$', jobs.list_jobs, name='list_jobs'),
    url(r'^get_car_status_autopilot/$', autopilot.get_car_status_autopilot, name='get_car_status_autopilot'),
    url(r'^get_car_status_training/$', drive.get_car_status_training, name='get_car_status_training'),
    url(r'^home/$', views.home, name='home'),
    url(r'^data/download/$', data_folders.getfiles, name='getfiles'),
    url(r'^data/delete/$', data_folders.delete_data, name='delete_data'),
    url(r'^job/remark/delete/$', jobs.delete_remark, name='delete_remark'),
    url(r'^job/remark/add/$', jobs.add_remark, name='add_remark'),
    url(r'^job/delete/$', jobs.delete_job, name='delete_job'),
    url(r'^model/local/copy/$', jobs.copy_local, name='copy_local'),
    url(r'^autopilot/$', autopilot.autopilot, name='autopilot'),
    url(r'^proc/kill/$', autopilot.kill_proc, name='kill_proc'),
    path('availability/display/', job_creation.display_availability, name='display'),
    url(r'^status/update/id/$', jobs.update_status_by_id, name='update_status_by_id'),
    url(r'^request/cancel/$', jobs.cancel_request, name='cancel_request'),
    url(r'^data/comment/add/$', data_folders.add_data_folder_comment, name='add_data_folder_comment'),
    url(r'^data/comment/delete/$', data_folders.delete_data_folder_comment, name='delete_data_folder_comment'),
    path('drive/', drive.drive, name='drive'),

]