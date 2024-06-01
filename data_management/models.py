import os
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField 

def upload_to_fos_directory(instance, filename):
    # Create a path with the format: "uploads/FOS<serial_number>/<filename>"
    base_path = 'uploads'
    serial_path = f'FOS{instance.fos_serial_number}'
    return os.path.join(base_path, serial_path, filename)

class FileUpload(models.Model):
    EVENT_CHOICES = [
        (0, 'None'),
        (1, 'Unknown'),
        (2, 'Leak'),
        (3, 'Walking'),
        (4, 'Animal'),
        (5, 'Digging'),
        (6, 'Climbing'),
        (7, 'Vehicle'),
        (8, 'Excavation'),
        (9, 'Vibration'),
        (10, 'Pressure Wave'),
        (11, 'Crawling'),
        (12, 'Fence Cut'),
        (13, 'Impact'),
        (14, 'HDD'),
        (15, 'Train'),
        (16, 'Elephant'),       
        (100, 'Cut Fibre')
    ]
    event_type = models.IntegerField(choices=EVENT_CHOICES, default=0)
    event_description = models.TextField(blank=True, null=True)
    event_details = models.JSONField(default=dict, blank=True, null=True)
    file = models.FileField(upload_to=upload_to_fos_directory)
    fos_serial_number = models.CharField(max_length=100)
    kml_map_data = models.TextField(null=True, blank=True) 
    fibre_calibrations = models.JSONField(blank=True, null=True)
    channel = models.IntegerField(default=0)
    number_of_bins = models.IntegerField()
    start = models.IntegerField()
    end = models.IntegerField()
    adc_clock = models.IntegerField()
    pulse_repetition_rate = models.IntegerField()
    pulse_width = models.IntegerField()
    file_recording_rev = models.IntegerField()
    number_data_rows = models.IntegerField()
    das_filter_cut_in_freq = models.FloatField(blank=True, null=True)
    das_filter_cut_out_freq = models.FloatField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploader = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    @staticmethod
    def get_event_types():
        return FileUpload.EVENT_CHOICES
        
    def __str__(self):
        return f"File for {self.fos_serial_number} uploaded by {self.uploader.username}"
    

class UploadedFile(models.Model):
    file_name = models.CharField(max_length=255)
    file_url = models.URLField()    
