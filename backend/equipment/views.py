from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Avg, Count
import pandas as pd

from .models import Equipment, UploadHistory

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from django.http import HttpResponse
from django.utils.timezone import now

from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

@method_decorator(csrf_exempt, name='dispatch')
class UploadCSV(APIView):
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        file = request.FILES.get('file')

        if not file:
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            df = pd.read_csv(file)
        except Exception:
            return Response(
                {"error": "Invalid CSV file"},
                status=status.HTTP_400_BAD_REQUEST
            )

        required_cols = {"Equipment Name", "Type", "Flowrate", "Pressure", "Temperature"}
        if not required_cols.issubset(df.columns):
            return Response(
                {"error": "CSV missing required columns"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # clear old data 
        Equipment.objects.all().delete()

        # save CSV rows into DB
        for _, row in df.iterrows():
            Equipment.objects.create(
                name=row["Equipment Name"],
                type=row["Type"],
                flowrate=row["Flowrate"],
                pressure=row["Pressure"],
                temperature=row["Temperature"]
            )

        # analytics from DB
        summary = {
            "total_equipment": Equipment.objects.count(),
            "avg_flowrate": round(Equipment.objects.aggregate(Avg("flowrate"))["flowrate__avg"], 2),
            "avg_pressure": round(Equipment.objects.aggregate(Avg("pressure"))["pressure__avg"], 2),
            "avg_temperature": round(Equipment.objects.aggregate(Avg("temperature"))["temperature__avg"], 2),
            "type_distribution": dict(
                Equipment.objects.values("type")
                .annotate(count=Count("id"))
                .values_list("type", "count")
            )
        }

        UploadHistory.objects.create(summary=summary) # Save upload history
        ids_to_keep = UploadHistory.objects.values_list('id', flat=True).order_by('-uploaded_at')[:5] #save only last 5 uploads
        UploadHistory.objects.exclude(id__in=ids_to_keep).delete() #delete older uploads

        return Response(summary, status=status.HTTP_201_CREATED)


class EquipmentList(APIView):
    def get(self, request):
        data = list(
            Equipment.objects.values(
                "id",
                "name",
                "type",
                "flowrate",
                "pressure",
                "temperature",
                "created_at"
            )
        )
        return Response(data, status=status.HTTP_200_OK)


class EquipmentSummary(APIView):
    def get(self, request):
        summary = {
            "total_equipment": Equipment.objects.count(),
            "avg_flowrate": Equipment.objects.aggregate(Avg("flowrate"))["flowrate__avg"],
            "avg_pressure": Equipment.objects.aggregate(Avg("pressure"))["pressure__avg"],
            "avg_temperature": Equipment.objects.aggregate(Avg("temperature"))["temperature__avg"],
            "type_distribution": dict(
                Equipment.objects.values("type")
                .annotate(count=Count("id"))
                .values_list("type", "count")
            )
        }
        return Response(summary, status=status.HTTP_200_OK)


class UploadHistoryList(APIView):      #stores last 5 upload histories only
    def get(self, request):
        uploads = UploadHistory.objects.order_by("-uploaded_at")[:5]
        data = [
            {
                "uploaded_at": u.uploaded_at,
                "summary": u.summary
            }
            for u in uploads
        ]
        return Response(data, status=status.HTTP_200_OK)


class PressureTemperatureView(APIView):  #purely for pressure vs temperature chart
    def get(self,request):
        data = list(
            Equipment.objects.values(
                "pressure",
                "temperature"
            )
        )
        return Response(data, status=status.HTTP_200_OK)
    
class GeneratePDFReport(APIView):       #pdf need to be generated in backend separately.
    def get(self, request):
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="equipment_report.pdf"'

        doc = SimpleDocTemplate(
            response,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        styles = getSampleStyleSheet()
        story = []

        # Title
        story.append(Paragraph("<b>Equipment Analytics Report</b>", styles['Title']))
        story.append(Spacer(1, 0.3 * inch))

        # Date
        story.append(Paragraph(f"Generated on: {now().strftime('%d %b %Y, %H:%M')}", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Summary from DB
        total = Equipment.objects.count()
        avg_flow = Equipment.objects.aggregate(Avg("flowrate"))["flowrate__avg"]
        avg_pressure = Equipment.objects.aggregate(Avg("pressure"))["pressure__avg"]
        avg_temp = Equipment.objects.aggregate(Avg("temperature"))["temperature__avg"]

        story.append(Paragraph("<b>Summary</b>", styles['Heading2']))
        story.append(Paragraph(f"Total Equipment: {total}", styles['Normal']))
        story.append(Paragraph(f"Average Flowrate: {avg_flow:.2f}", styles['Normal']))
        story.append(Paragraph(f"Average Pressure: {avg_pressure:.2f}", styles['Normal']))
        story.append(Paragraph(f"Average Temperature: {avg_temp:.2f}", styles['Normal']))
        story.append(Spacer(1, 0.3 * inch))

        # Equipment type distribution
        story.append(Paragraph("<b>Equipment Type Distribution</b>", styles['Heading2']))

        data = [["Type", "Count"]]
        qs = Equipment.objects.values("type").annotate(count=Count("id"))

        for item in qs:
            data.append([item["type"], item["count"]])

        table = Table(data)
        story.append(table)

        doc.build(story)
        return response
    
