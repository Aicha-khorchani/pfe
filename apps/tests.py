from django.test import TestCase
from django.urls import reverse
from .models import adddata, centreddata  # Adjust the import based on your models' location
from datetime import date
from decimal import Decimal

class AddDataModelTest(TestCase):

    def setUp(self):
        # Create an instance of centreddata for ForeignKey
        self.centreddata = centreddata.objects.create(name='Lead Test')  # Adjust this if needed

    def test_adddata_post(self):
        # URL to the view where the form is submitted
        url = reverse('add_data_view')  # Replace 'add_data_view' with the actual name of your view

        # Data to post
        data = {
            'lead': self.centreddata.id,  # ID of the lead ForeignKey
            'owner': 'John Doe',
            'contract_file': None,  # Set None or file upload as needed
            'nextdate': date.today(),
            'revenue': Decimal('10000.00'),
            'size': Decimal('150.5000'),
            'number': Decimal('5000.0000'),
            'score': Decimal('95.50'),
            'worker': Decimal('45.500'),
            'leadsrc': 'Referral',
            'sector': 'Technology',
            'status': 'new',
            'note': 'Initial contact with lead',
        }

        # Make POST request
        response = self.client.post(url, data)

        # Check if the response status is 302 (redirect after successful form submission)
        self.assertEqual(response.status_code, 302)

        # Check if the object is saved in the database
        self.assertEqual(adddata.objects.count(), 1)

        # Fetch the saved object and verify its fields
        saved_data = adddata.objects.first()
        self.assertEqual(saved_data.lead, self.centreddata)
        self.assertEqual(saved_data.owner, 'John Doe')
        self.assertEqual(saved_data.revenue, Decimal('10000.00'))
        self.assertEqual(saved_data.size, Decimal('150.5000'))
        self.assertEqual(saved_data.score, Decimal('95.50'))
        self.assertEqual(saved_data.worker, Decimal('45.500'))
        self.assertEqual(saved_data.status, 'new')
        self.assertEqual(saved_data.note, 'Initial contact with lead')
