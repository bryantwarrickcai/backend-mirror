import json
import csv
from io import StringIO
from unittest.mock import patch, Mock
from django.test import TestCase, Client
from django.urls import reverse
from django.http import HttpResponse


class CSVExportTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = '/csv/export/' 
        self.valid_ocr_data = {
            "DEMOGRAPHY": {
                "subject_initials": "LMNO",
                "sin": "76543",
                "study_drug": "Amlodipine Besylate 10 mg",
                "screening_date": "12/MAR/2024",
                "gender": "Male",
                "date_of_birth": "01/MEI/1999",
                "age": 25,
                "weight_kg": "48",
                "height_cm": "166",
                "bmi": "21"
            },
            "MEDICAL_HISTORY": {
                "smoker_cigarettes_per_day": None
            },
            "VITAL_SIGNS": {
                "systolic_bp": "108",
                "diastolic_bp": "77",
                "heart_rate": "85"
            },
            "SEROLOGY": {
                "hbsag": "Negative",
                "hcv": "Negative",
                "hiv": "Negative"
            },
            "URINALYSIS": {
                "ph": [8, "4-8", None, "Carik Celup"],
                "density": 1.039,
                "glucose": "(-)",
                "ketone": "(-)",
                "urobilinogen": "(-)",
                "bilirubin": "(-)",
                "blood": "(-)",
                "leucocyte_esterase": "(-)",
                "nitrite": "(-)"
            },
            "HEMATOLOGY": {
                "hemoglobin": [11, "10-25", "g/dL", "Reflectance Photomtr"],
                "hematocrit": 33,
                "leukocyte": 7,
                "erythrocyte": 70,
                "thrombocyte": 183,
                "esr": 10
            },
            "CLINICAL_CHEMISTRY": {
                "bilirubin_total": None,
                "alkaline_phosphatase": None,
                "sgot": 20,
                "sgpt": 21,
                "ureum": 19,
                "creatinine": 0.89,
                "random_blood_glucose": 122
            }
        }

    # ============ POSITIVE TEST CASES ============

    # --- Happy Test ---
    
    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_successful_csv_export_with_ocr_data(self, mock_json_to_csv):
        """Test successful CSV export with valid OCR medical data"""
        mock_json_to_csv.return_value = None
        
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_ocr_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="report.csv"')
        
        mock_json_to_csv.assert_called_once()
        call_args = mock_json_to_csv.call_args
        self.assertEqual(call_args[0][0], self.valid_ocr_data)
        
        writer_arg = call_args[0][1]
        self.assertTrue(hasattr(writer_arg, 'writerow'))
        self.assertTrue(hasattr(writer_arg, 'writerows'))

    # --- Input variations ---

    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_minimal_ocr_data(self, mock_json_to_csv):
        """Test with minimal OCR data"""
        minimal_data = {"DEMOGRAPHY": {"subject_initials": "ABC"}}
        response = self.client.post(
            self.url,
            data=json.dumps(minimal_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        mock_json_to_csv.assert_called_once_with(minimal_data, mock_json_to_csv.call_args[0][1])


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_empty_json_object(self, mock_json_to_csv):
        """Test with empty JSON object"""
        response = self.client.post(
            self.url,
            data='{}',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        mock_json_to_csv.assert_called_once_with({}, mock_json_to_csv.call_args[0][1])


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_null_json_value(self, mock_json_to_csv):
        """Test with null JSON value"""
        response = self.client.post(
            self.url,
            data='null',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        mock_json_to_csv.assert_called_once_with(None, mock_json_to_csv.call_args[0][1])


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_json_array(self, mock_json_to_csv):
        """Test with JSON array"""
        array_data = [self.valid_ocr_data, {"DEMOGRAPHY": {"subject_initials": "XYZ"}}]
        response = self.client.post(
            self.url,
            data=json.dumps(array_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        mock_json_to_csv.assert_called_once_with(array_data, mock_json_to_csv.call_args[0][1])


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_unicode_characters(self, mock_json_to_csv):
        """Test with Unicode characters in data"""
        unicode_data = {
            "DEMOGRAPHY": {
                "subject_initials": "José María",
                "study_drug": "Paracétamol 500mg™"
            }
        }
        response = self.client.post(
            self.url,
            data=json.dumps(unicode_data, ensure_ascii=False),
            content_type='application/json; charset=utf-8'
        )
        self.assertEqual(response.status_code, 200)
        mock_json_to_csv.assert_called_once_with(unicode_data, mock_json_to_csv.call_args[0][1])


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_large_dataset(self, mock_json_to_csv):
        """Test with large OCR dataset"""
        large_data = {
            "patients": [
                {**self.valid_ocr_data, "DEMOGRAPHY": {**self.valid_ocr_data["DEMOGRAPHY"], "sin": str(i)}}
                for i in range(100)
            ]
        }
        response = self.client.post(
            self.url,
            data=json.dumps(large_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        mock_json_to_csv.assert_called_once_with(large_data, mock_json_to_csv.call_args[0][1])


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_special_characters_in_data(self, mock_json_to_csv):
        """Test with special characters that might break CSV"""
        special_data = {
            "DEMOGRAPHY": {
                "subject_initials": 'Test "Quote"',
                "notes": "Line1\nLine2\tTabbed",
                "study_drug": "Drug, with comma"
            }
        }
        response = self.client.post(
            self.url,
            data=json.dumps(special_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        mock_json_to_csv.assert_called_once_with(special_data, mock_json_to_csv.call_args[0][1])


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_deeply_nested_data(self, mock_json_to_csv):
        """Test with deeply nested medical data"""
        nested_data = {
            "PATIENT": {
                "demographics": self.valid_ocr_data["DEMOGRAPHY"],
                "test_results": {
                    "blood_work": self.valid_ocr_data["HEMATOLOGY"],
                    "additional": {"level3": {"level4": "deep_value"}}
                }
            }
        }
        response = self.client.post(
            self.url,
            data=json.dumps(nested_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        mock_json_to_csv.assert_called_once_with(nested_data, mock_json_to_csv.call_args[0][1])


    def test_very_large_json_string_field(self):
        """Test with very large string field"""
        large_string_data = {
            "NOTES": "x" * 10000,  # 10KB string
            "DEMOGRAPHY": {"subject_initials": "TEST"}
        }
        response = self.client.post(
            self.url,
            data=json.dumps(large_string_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    # --- Response behavior ---

    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_response_headers_correct(self, mock_json_to_csv):
        """Test that successful response has correct headers"""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_ocr_data),
            content_type='application/json'
        )
        self.assertIsInstance(response, HttpResponse)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertEqual(response['Content-Disposition'], 'attachment; filename="report.csv"')


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_csrf_exempt_works(self, mock_json_to_csv):
        """Test that CSRF protection is bypassed"""
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_ocr_data),
            content_type='application/json'
        )
        self.assertNotEqual(response.status_code, 403)
        self.assertEqual(response.status_code, 200)


    def test_non_json_content_type_still_works(self):
        """Test that non-JSON content type can still work if body is valid JSON"""
        response = self.client.post(
            self.url,
            data=json.dumps({"test": "data"}),
            content_type='text/plain'
        )
        self.assertEqual(response.status_code, 200)

    # ============ NEGATIVE TEST CASES ============

    # --- Method validation ---

    def test_get_method_not_allowed(self):
        """Test that GET method returns 405"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)


    def test_put_method_not_allowed(self):
        """Test that PUT method returns 405"""
        response = self.client.put(
            self.url,
            data=json.dumps(self.valid_ocr_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 405)


    def test_delete_method_not_allowed(self):
        """Test that DELETE method returns 405"""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, 405)

    # --- Invalid input data ---

    def test_invalid_json_syntax(self):
        """Test with invalid JSON syntax - should return 400 with error message"""
        invalid_json_cases = [
            '{"key": value}',        # unquoted value
            '{"key": "value",}',     # trailing comma
            '{key: "value"}',        # unquoted key
            '{"key": "value"',       # missing closing brace
        ]
        for invalid_json in invalid_json_cases:
            with self.subTest(json_data=invalid_json):
                response = self.client.post(
                    self.url,
                    data=invalid_json,
                    content_type='application/json'
                )
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response['Content-Type'], 'application/json')
                response_data = json.loads(response.content)
                self.assertIn('error', response_data)
                self.assertEqual(response_data['error'], 'Invalid JSON format')


    def test_empty_request_body(self):
        """Test with empty request body - should return 400"""
        response = self.client.post(
            self.url,
            data='',
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'Invalid JSON format')


    def test_malformed_unicode(self):
        """Test with malformed Unicode - should return 400"""
        response = self.client.post(
            self.url,
            data=b'{"invalid": "\xff\xfe"}',
            content_type='application/json; charset=utf-8'
        )
        self.assertEqual(response.status_code, 400)

    # --- Exception handling ---

    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_json_to_csv_exception(self, mock_json_to_csv):
        """Test when json_to_csv raises an exception - should return 500"""
        mock_json_to_csv.side_effect = ValueError("CSV conversion failed")
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_ocr_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response['Content-Type'], 'application/json')
        response_data = json.loads(response.content)
        self.assertIn('error', response_data)
        self.assertEqual(response_data['error'], 'CSV conversion failed')
        self.assertEqual(response_data['message'], 'CSV conversion failed')


    @patch('csv_export.utility.json_to_csv.json_to_csv')
    def test_json_to_csv_memory_error(self, mock_json_to_csv):
        """Test when json_to_csv raises MemoryError"""
        mock_json_to_csv.side_effect = MemoryError("Not enough memory")
        response = self.client.post(
            self.url,
            data=json.dumps(self.valid_ocr_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['error'], 'CSV conversion failed')

 # Strategy Pattern Tests

class StrategyPatternTestCase(TestCase):
    """Test cases specifically for Strategy Pattern implementation"""
    
    def test_abstract_strategy_cannot_be_instantiated(self):
        """Test that abstract ExportStrategy cannot be instantiated"""
        from csv_export.strategies import ExportStrategy

        with self.assertRaises(TypeError):
            ExportStrategy()
    
    def test_csv_export_strategy_implementation(self):
        """Test CSVExportStrategy implementation"""
        from csv_export.strategies import CSVExportStrategy, ExportStrategy
        from unittest.mock import Mock
        
        strategy = CSVExportStrategy()
        self.assertIsInstance(strategy, ExportStrategy)
        
        self.assertTrue(hasattr(strategy, 'export'))
        self.assertTrue(callable(strategy.export))
        
        mock_writer = Mock()
        test_data = {"test": "data"}
        
        with patch('csv_export.utility.json_to_csv.json_to_csv') as mock_json_to_csv:
            strategy.export(test_data, mock_writer)
            mock_json_to_csv.assert_called_once_with(test_data, mock_writer)
    
    def test_abstract_method_properties(self):
        """Test abstract method properties and force execution of pass statement"""
        from csv_export.strategies import ExportStrategy
        import inspect
        
        export_method = ExportStrategy.export
        
        self.assertTrue(getattr(export_method, '__isabstractmethod__', False))
        
        sig = inspect.signature(export_method)
        params = list(sig.parameters.keys())
        self.assertEqual(params, ['self', 'data', 'writer_or_response'])
        
        mock_self = Mock()
        mock_self.__class__ = ExportStrategy
        
        result = export_method(mock_self, {}, None)
        self.assertIsNone(result)  