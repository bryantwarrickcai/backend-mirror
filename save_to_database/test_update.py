# tests/test_views_update.py  (or append into your existing test_views.py)
import json
from django.test import TestCase, Client
from django.urls import reverse
from django.core.files.base import ContentFile
from save_to_database.models import CSV

class UpdateCsvRecordViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        
        # initial dataset
        self.initial_json = [{"name": "Alice", "age": 28}]
        csv_bytes = b"name,age\nAlice,28\n"
        csv_file = ContentFile(csv_bytes, name="initial.csv")
        self.csv_record = CSV.objects.create(
            name="my-dataset",
            file=csv_file,
            source_json=self.initial_json
        )

    # POSITIVE TESTS #

    def test_update_csv_record_success_put(self):
        """PUT should update the CSV record and file contents."""
        url = reverse('save_to_database:update_csv_record', kwargs={'pk': self.csv_record.pk})
        new_json = [{"name": "Bob", "age": 40}]
        payload = {"name": "updated-dataset", "source_json": new_json}

        response = self.client.put(
            url,
            data=json.dumps(payload),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['id'], self.csv_record.pk)
        self.assertEqual(data['name'], "updated-dataset")

        # fetch fresh instance
        updated = CSV.objects.get(pk=self.csv_record.pk)
        self.assertEqual(updated.source_json, new_json)

        # file exists and contains Bob
        updated.file.seek(0)
        content = updated.file.read().decode('utf-8')
        self.assertIn("Bob", content)

    # NEGATIVE TESTS #

    def test_update_csv_record_not_found(self):
        """Updating non-existent record returns 404."""
        url = reverse('save_to_database:update_csv_record', kwargs={'pk': 9999})
        response = self.client.put(url, data=json.dumps({"name":"x","source_json":[{}]}), content_type='application/json')
        self.assertEqual(response.status_code, 404)

    def test_update_csv_record_invalid_json(self):
        """Invalid JSON should return 400."""
        url = reverse('save_to_database:update_csv_record', kwargs={'pk': self.csv_record.pk})
        response = self.client.put(url, data="not-json", content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('error', response.json())

    def test_update_csv_record_wrong_method(self):
        """GET on update endpoint should be 405."""
        url = reverse('save_to_database:update_csv_record', kwargs={'pk': self.csv_record.pk})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)