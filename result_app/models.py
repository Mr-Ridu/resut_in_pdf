from django.db import models
from django.contrib.auth.models import User

class SchoolSettings(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    school_name = models.CharField(max_length=200, default='ABC HIGH SCHOOL')
    school_address = models.TextField(default='Dhaka, Bangladesh')
    school_logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    signature_image = models.ImageField(upload_to='signatures/', blank=True, null=True)
    seal_image = models.ImageField(upload_to='seals/', blank=True, null=True)
    
    # Design settings
    PAPER_CHOICES = [
        ('A4', 'A4'),
        ('A5', 'A5'),
    ]
    ORIENTATION_CHOICES = [
        ('portrait', 'Portrait'),
        ('landscape', 'Landscape'),
    ]
    COLOR_CHOICES = [
        ('blue', 'Blue'),
        ('green', 'Green'),
        ('red', 'Red'),
        ('purple', 'Purple'),
        ('orange', 'Orange'),
    ]
    FONT_CHOICES = [
        ('english', 'English'),
        ('bengali', 'Bengali'),
    ]
    
    paper_size = models.CharField(max_length=2, choices=PAPER_CHOICES, default='A4')
    orientation = models.CharField(max_length=10, choices=ORIENTATION_CHOICES, default='portrait')
    primary_color = models.CharField(max_length=20, choices=COLOR_CHOICES, default='blue')
    font_style = models.CharField(max_length=10, choices=FONT_CHOICES, default='english')
    
    # Grading settings
    grading_system = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Settings for {self.school_name}"

class ResultHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    excel_file = models.FileField(upload_to='uploads/')
    total_students = models.IntegerField()
    pdf_file = models.FileField(upload_to='pdfs/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Result {self.id} - {self.created_at.strftime('%Y-%m-%d')}"