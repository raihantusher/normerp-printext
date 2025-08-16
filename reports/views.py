from django.http import HttpResponse
from .pdf_utlis import render_to_pdf
from datetime import datetime


def generate_pdf(request):
    # Sample data
    data = {
        'today': datetime.now().strftime('%Y-%m-%d'),
        'title': 'My PDF Report',
        'items': [
            {'name': 'Product 1', 'quantity': 1, 'price': 9.99},
            {'name': 'Product 2', 'quantity': 3, 'price': 4.99},
            {'name': 'Product 3', 'quantity': 2, 'price': 7.99},
        ]
    }

    pdf = render_to_pdf('backend/reports/demo_report.html', data)

    if pdf:
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = "Invoice_%s.pdf" % data['today']
        content = "inline; filename=%s" % filename
        response['Content-Disposition'] = content
        return response
    return HttpResponse("Error generating PDF", status=400)