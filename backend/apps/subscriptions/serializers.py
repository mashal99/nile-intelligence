from rest_framework import serializers
from .models import Invoice


class InvoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice
        fields = ['id', 'amount', 'currency', 'status', 'issued_at', 'paid_at', 'invoice_pdf_url']
