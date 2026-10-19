"""Tests for the PixelIQ Result Generator.

Covers the PixelIQ branding that must appear across the UI and inside the
generated PDFs, plus the full upload → column mapping → preview → generate
workflow.
"""
import tempfile
from io import BytesIO

import pandas as pd
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from django.urls import reverse

from .models import ResultHistory, SchoolSettings
from .utils import calculate_gpa, process_student_data

TEMP_MEDIA = tempfile.mkdtemp(prefix='pixeliq_test_media_')

SAMPLE_DATA = {
    'Roll': [1, 2, 3],
    'Name': ['Alice Rahman', 'Bob Karim', 'Cara Islam'],
    'Class': ['Ten', 'Ten', 'Ten'],
    'Shift': ['Morning', 'Morning', 'Morning'],
    'Section': ['A', 'A', 'A'],
    'Semester': ['Final', 'Final', 'Final'],
    'Bangla': [85, 70, 92],
    'English': [78, 65, 85],
    'Math': [92, 80, 88],
}

COLUMN_MAPPING = {
    'name_column': 'Name',
    'roll_column': 'Roll',
    'class_column': 'Class',
    'shift_column': 'Shift',
    'section_column': 'Section',
    'semester_column': 'Semester',
    'subject_columns': ['Bangla', 'English', 'Math'],
}


def make_sample_excel_file():
    buf = BytesIO()
    pd.DataFrame(SAMPLE_DATA).to_excel(buf, index=False)
    return SimpleUploadedFile(
        'sample_results.xlsx',
        buf.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )


class PixelIQBrandingTests(TestCase):
    """The PixelIQ brand must be visible on every public page."""

    def test_homepage_carries_pixeliq_brand(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('PixelIQ Result Generator', content)
        self.assertIn('pixeliqit.com', content)
        self.assertIn('pixeliq_logo.png', content)
        # Old brand must be gone
        self.assertNotIn('School Result Generator', content)

    def test_login_page_carries_pixeliq_brand(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('PixelIQ', content)
        self.assertIn('pixeliqit.com', content)
        self.assertIn('pixeliq_logo.png', content)
        self.assertIn('<title>PixelIQ Result Generator · Login</title>', content)

    def test_page_titles_are_pixeliq_branded(self):
        for url_name, expected_tail in [
            ('index', 'Home'),
            ('login', 'Login'),
            ('download_sample_excel', None),
        ]:
            response = self.client.get(reverse(url_name))
            if expected_tail is None:
                continue
            self.assertIn(
                f'PixelIQ Result Generator · {expected_tail}',
                response.content.decode(),
                f'title branding missing on {url_name}',
            )

    def test_admin_site_headers_are_branded(self):
        from django.contrib import admin
        self.assertIn('PixelIQ', admin.site.site_header)
        self.assertIn('pixeliqit.com', admin.site.index_title)

    def test_sample_excel_download_works(self):
        response = self.client.get(reverse('download_sample_excel'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('sample_student_results.xlsx', response['Content-Disposition'])


class GradingLogicTests(TestCase):
    def test_grade_boundaries(self):
        self.assertEqual(calculate_gpa(85), ('A+', 5.00))
        self.assertEqual(calculate_gpa(75), ('A', 4.00))
        self.assertEqual(calculate_gpa(65), ('A-', 3.50))
        self.assertEqual(calculate_gpa(55), ('B', 3.00))
        self.assertEqual(calculate_gpa(45), ('C', 2.00))
        self.assertEqual(calculate_gpa(35), ('D', 1.00))
        self.assertEqual(calculate_gpa(10), ('F', 0.00))

    def test_positions_ranked_by_total(self):
        df = pd.DataFrame(SAMPLE_DATA)
        students = process_student_data(df, COLUMN_MAPPING)
        positions = [s['position'] for s in students]
        self.assertEqual(sorted(positions), [1, 2, 3])
        # Highest total (Math 88 + ... Alice total 255, Cara 265) -> Cara first
        top = [s for s in students if s['position'] == 1][0]
        self.assertEqual(top['name'], 'Cara Islam')


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class FullWorkflowTests(TestCase):
    """End-to-end: login, upload, map, preview, generate branded PDF."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='pixeliq_tester', password='pass-1234'
        )
        self.client.force_login(self.user)

    def test_upload_maps_preview_generate_produces_branded_pdf(self):
        # Upload
        response = self.client.post(
            reverse('upload_excel'),
            {'excel_file': make_sample_excel_file()},
        )
        self.assertRedirects(response, reverse('column_mapping'))

        # Column mapping
        post_data = dict(COLUMN_MAPPING)
        post_data['subject_columns'] = COLUMN_MAPPING['subject_columns']
        response = self.client.post(reverse('column_mapping'), post_data)
        self.assertRedirects(response, reverse('result_preview'))

        # Preview
        response = self.client.get(reverse('result_preview'))
        self.assertEqual(response.status_code, 200)
        preview_content = response.content.decode()
        self.assertIn('Alice Rahman', preview_content)
        self.assertIn('3 students processed', preview_content)

        # Generate PDF
        response = self.client.get(reverse('generate_results'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        pdf_bytes = b''.join(response.streaming_content)
        self.assertGreater(len(pdf_bytes), 1000)

        # PDF content must carry the PixelIQ brand
        from PyPDF2 import PdfReader
        reader = PdfReader(BytesIO(pdf_bytes))
        self.assertGreaterEqual(len(reader.pages), 3)
        text = '\n'.join(page.extract_text() or '' for page in reader.pages)
        self.assertIn('PixelIQ Result Generator', text)
        self.assertIn('pixeliqit.com', text)
        self.assertIn('Alice Rahman', text)

        # PDF metadata must be branded
        meta_title = str(reader.metadata.title or '')
        meta_author = str(reader.metadata.author or '')
        self.assertIn('PixelIQ', meta_title)
        self.assertIn('pixeliqit.com', meta_author)

        # History record saved
        self.assertEqual(ResultHistory.objects.count(), 1)
        history = ResultHistory.objects.first()
        self.assertTrue(history.pdf_file.name)
        self.assertEqual(history.total_students, 3)

    def test_settings_page_lists_brand(self):
        response = self.client.get(reverse('settings'))
        self.assertEqual(response.status_code, 200)
        content = response.content.decode()
        self.assertIn('PixelIQ Result Generator', content)
        # Fresh settings row created for the user
        self.assertTrue(SchoolSettings.objects.filter(user=self.user).exists())

    def test_upload_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('upload_excel'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('/admin/login/', response['Location'])
