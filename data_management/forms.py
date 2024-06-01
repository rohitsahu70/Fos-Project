from django import forms
from .models import FileUpload
import xml.etree.ElementTree as ET
from django.core.exceptions import ValidationError
import struct
import json
import csv
from io import StringIO

class FileUploadForm(forms.ModelForm):
    kml_file = forms.FileField(required=False)  # Ensure that a KML file is required
    event_details = forms.CharField(required=False, widget=forms.Textarea(attrs={'hidden': True}), initial="{}")
    fibre_calibrations = forms.FileField(required=False) # Ensure that a CSV file is required

    class Meta:
        model = FileUpload
        fields = ['file', 'fos_serial_number', 'kml_file', 'event_type', 'event_description', 'event_details', 'fibre_calibrations']

    def clean_event_details(self):
        keys = self.data.getlist('key[]')
        values = self.data.getlist('value[]')

        # Trim whitespace and filter out empty keys or values
        keys = [key.strip() for key in keys if key.strip()]
        values = [value.strip() for value in values if value.strip()]

        if len(keys) != len(values):
            raise forms.ValidationError("Each key must have a corresponding value and neither can be empty.")

        # Create dictionary, skipping empty pairs if any remain (not likely due to above filtering)
        event_details_dict = {k: v for k, v in zip(keys, values) if k and v}

        return event_details_dict

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and not file.name.endswith('.bin'):
            raise ValidationError("Only .bin files are allowed.")

        # Process file header if present
        if file:
            file.seek(0)
            header_data = file.read(128)
            header_info = self.process_header(header_data)
            for key, value in header_info.items():
                setattr(self.instance, key, value)
            file.seek(0)

        return file
    

    def clean_fibre_calibrations(self):
        csv_file = self.cleaned_data.get('fibre_calibrations')
        if csv_file:
            csv_file.seek(0)
            content = csv_file.read().decode('utf-8')
        
            fieldnames = ["start", "end", "dist"]
            reader = csv.DictReader(StringIO(content), fieldnames=fieldnames)
        
            data = []
            cumulative_physical_distance = 0 

            for entry in reader:
                entry["start"] = int(entry["start"])
                entry["end"] = int(entry["end"])
                entry["dist"] = int(entry["dist"])

                cumulative_physical_distance += entry["dist"]
            
                new_entry = {
                    "start": entry["start"],
                    "end": entry["end"],
                    "dist": entry["dist"],
                    "total": cumulative_physical_distance
                }
                data.append(new_entry)

            return data
        return None

    def clean_kml_file(self):
        kml_file = self.cleaned_data.get('kml_file')
        if kml_file: #changing this codition 
            if not kml_file.name.endswith('.kml'):
                raise ValidationError("Only KML files are allowed.")

            # Attempt to parse the KML file to ensure it's valid
            try:
                kml_data = kml_file.read()  
                kml_str = kml_data.decode('utf-8') 
                ET.fromstring(kml_str)  # Parse XML to validate structure
                self.cleaned_data['kml_map_data'] = kml_str
            except ET.ParseError:
                raise ValidationError("Invalid KML file.")
        return kml_file


    def save(self, commit=True):
        instance = super().save(commit=False)
        if 'kml_map_data' in self.cleaned_data:
            instance.kml_map_data = self.cleaned_data['kml_map_data']
        if commit:
            instance.save()
        return instance
                
    def process_header(self, data):
        # Unpack format includes all fields from your file's binary header
        fmt = '<HIIIHHII24sI8s8sII'
        fmt_das = '<ff'  # Format for additional DAS data, if applicable

        # Check that the data length matches what is expected to unpack
        expected_length = struct.calcsize(fmt)
        actual_length = len(data)
        if actual_length < expected_length:
            raise ValueError(f"Header data is incomplete, expected at least {expected_length} bytes, got {actual_length} bytes.")
    
        if actual_length > expected_length:
            # Only unpack up to the expected length of the main data
            main_data = struct.unpack(fmt, data[:expected_length])
        else:
            main_data = struct.unpack(fmt, data)

        # Assuming that the DAS data follows immediately after the main data
        das_start_index = expected_length
        das_end_index = das_start_index + struct.calcsize(fmt_das)
        if actual_length >= das_end_index:
            das_data = data[das_start_index:das_end_index]
            das_cut_in, das_cut_out = struct.unpack(fmt_das, das_data)
        else:
            das_cut_in = das_cut_out = None  # Handle case where DAS data is not present

        # Building a dictionary with unpacked data
        header_info = {
            'channel': main_data[0],
            'number_of_bins': main_data[1],
            'start': main_data[2],
            'end': main_data[3],
            'adc_clock': main_data[4],
            'pulse_repetition_rate': main_data[5],
            'pulse_width': main_data[6],
            'file_recording_rev': main_data[7],
            'time_date': main_data[8],  # Assuming this index is correct
            'number_data_rows': main_data[9],
            'rec_type': main_data[10],
            'das_filter_cut_in_freq': das_cut_in,
            'das_filter_cut_out_freq': das_cut_out
        }

        return header_info

from django import forms
from .models import FileUpload

class FileFilterForm(forms.Form):
    fos_serial_number = forms.CharField(required=False, label='FOS Serial Number')
    event_type = forms.ChoiceField(choices=FileUpload.EVENT_CHOICES, required=False, label='Event Type')
    channel = forms.IntegerField(required=False)
    file_name = forms.CharField(required=False, label='File Name')  # Assuming you have a filename field
    event_description = forms.CharField(required=False, label='Event Description')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fos_serial_number'].widget.attrs.update({'placeholder': 'FOS Serial Number'})
        self.fields['channel'].widget.attrs.update({'placeholder': 'Channel'})
        self.fields['file_name'].widget.attrs.update({'placeholder': 'File Name'})
        self.fields['event_description'].widget.attrs.update({'placeholder': 'Event Description'})

        
