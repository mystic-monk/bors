from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment
from .models import OperatorReturn
from .forms import GeneralForm, LicenceFormSet, EmissionFormSet, AccessibilityFormSet

STEPS = [
    ('general',       'General',       1),
    ('licence',       'Licences',      2),
    ('emissions',     'Emissions',     3),
    ('accessibility', 'Accessibility', 4),
]


def index(request):
    returns = OperatorReturn.objects.all().order_by('-created_at')
    return render(request, 'returns/index.html', {'returns': returns})


def step_general(request, pk=None):
    instance = get_object_or_404(OperatorReturn, pk=pk) if pk else None

    if request.method == 'POST':
        form = GeneralForm(request.POST, instance=instance)
        if form.is_valid():
            obj = form.save()
            messages.success(request, 'General details saved.')
            return redirect('step_licence', pk=obj.pk)
    else:
        form = GeneralForm(instance=instance)

    return render(request, 'returns/step_general.html', {
        'form': form,
        'steps': STEPS,
        'current_step': 1,
        'pk': pk,
    })


def step_licence(request, pk):
    obj = get_object_or_404(OperatorReturn, pk=pk)

    if request.method == 'POST':
        formset = LicenceFormSet(request.POST, instance=obj)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Licence details saved.')
            return redirect('step_emissions', pk=pk)
    else:
        formset = LicenceFormSet(instance=obj)

    return render(request, 'returns/step_licence.html', {
        'formset': formset,
        'obj': obj,
        'steps': STEPS,
        'current_step': 2,
        'pk': pk,
    })


def step_emissions(request, pk):
    obj = get_object_or_404(OperatorReturn, pk=pk)

    if request.method == 'POST':
        formset = EmissionFormSet(request.POST, instance=obj)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Emissions data saved.')
            return redirect('step_accessibility', pk=pk)
    else:
        formset = EmissionFormSet(instance=obj)

    return render(request, 'returns/step_emissions.html', {
        'formset': formset,
        'obj': obj,
        'steps': STEPS,
        'current_step': 3,
        'pk': pk,
    })


def step_accessibility(request, pk):
    obj = get_object_or_404(OperatorReturn, pk=pk)

    if request.method == 'POST':
        formset = AccessibilityFormSet(request.POST, instance=obj)
        if formset.is_valid():
            formset.save()
            obj.status = 'submitted'
            obj.submitted_at = timezone.now()
            obj.save()
            messages.success(request, 'Return submitted successfully.')
            return redirect('success', pk=pk)
    else:
        formset = AccessibilityFormSet(instance=obj)

    features = [
        ('mechanical_ramp', 'Mechanical access ramp'),
        ('centre_door_ramps', 'Centre door ramps'),
        ('exterior_displays', 'Exterior backlit route displays'),
        ('interior_stop_displays', 'Interior stop displays'),
        ('audio_announcements', 'Automated audible stop announcements'),
        ('yellow_handrails', 'Yellow coloured handrails'),
        ('priority_seating', 'Priority seating'),
        ('contrasting_seat_covers', 'Contrasting seat covers'),
        ('induction_loop', 'Induction loop system'),
    ]
    return render(request, 'returns/step_accessibility.html', {
        'formset': formset,
        'obj': obj,
        'steps': STEPS,
        'current_step': 4,
        'pk': pk,
        'features': features,
    })


def success(request, pk):
    obj = get_object_or_404(OperatorReturn, pk=pk)
    return render(request, 'returns/success.html', {'obj': obj})


def export_excel(request, pk):
    obj = get_object_or_404(OperatorReturn, pk=pk)
    wb = openpyxl.Workbook()

    header_font = Font(bold=True, color='FFFFFF')
    header_fill = PatternFill(start_color='1B3A6B', end_color='1B3A6B', fill_type='solid')
    center = Alignment(horizontal='center')

    def style_header_row(ws, row_num):
        for cell in ws[row_num]:
            cell.font = header_font
            cell.fill = header_fill
            cell.alignment = center

    ws1 = wb.active
    ws1.title = 'General Questions'
    ws1.append(['Data Year', 'Operator Name', 'Trading Name', 'County', 'Annual Revenue (€)', 'TaxSaver'])
    style_header_row(ws1, 1)
    ws1.append([
        obj.data_year, obj.operator_name, obj.trading_name,
        obj.county, float(obj.annual_revenue), 'Y' if obj.taxsaver else 'N',
    ])

    ws2 = wb.create_sheet('LicenceQuestions')
    ws2.append([
        'Operator Name', 'Licence No', 'Route No', 'On Free Travel', 'On YASC',
        'Date Joined', 'Service Commenced', 'Service Ceased', 'Date Ceased',
        'Total Passenger Journeys', 'Free Travel %', 'KM Operated', 'Daily PVR',
    ])
    style_header_row(ws2, 1)
    for lic in obj.licences.all():
        ws2.append([
            obj.operator_name, lic.licence_no, lic.route_no,
            'Y' if lic.on_free_travel else 'N',
            'Y' if lic.on_yasc else 'N',
            lic.date_joined.strftime('%d/%m/%Y') if lic.date_joined else '',
            'Y' if lic.service_commenced else 'N',
            'Y' if lic.service_ceased else 'N',
            lic.date_ceased.strftime('%d/%m/%Y') if lic.date_ceased else '',
            lic.total_passenger_journeys,
            float(lic.free_travel_percent),
            float(lic.km_operated),
            lic.daily_pvr,
        ])

    ws3 = wb.create_sheet('Emissions')
    ws3.append([
        'RES ID', 'Reg No', 'Regularly Deployed', 'Make', 'Model',
        'Transmission', 'Engine Type', 'Fuel Type', 'Euro Standard',
        'Make/Model Correct', 'Seats on Record', 'Correct Seats', 'AVL/GPS',
    ])
    style_header_row(ws3, 1)
    for v in obj.emissions.all():
        ws3.append([
            v.res_id, v.vehicle_reg,
            'Y' if v.regularly_deployed else 'N',
            v.make, v.model_version, v.transmission, v.engine_type,
            v.fuel_type, v.euro_standard,
            'Y' if v.make_model_correct else 'N',
            v.seats_on_record, v.correct_seats,
            'Y' if v.avl_gps else 'N',
        ])

    ws4 = wb.create_sheet('Accessibility Questions')
    ws4.append([
        'RES ID', 'Reg No', 'Wheelchair Spaces', 'Access Type',
        'Mechanical Ramp', 'Centre Door Ramps', 'Exterior Displays',
        'Interior Stop Displays', 'Audio Announcements', 'Yellow Handrails',
        'Priority Seating', 'Contrasting Seat Covers', 'Induction Loop',
    ])
    style_header_row(ws4, 1)
    for a in obj.accessibility.all():
        ws4.append([
            a.res_id, a.vehicle_reg, a.wheelchair_spaces, a.wheelchair_access_type,
            'Y' if a.mechanical_ramp else 'N',
            'Y' if a.centre_door_ramps else 'N',
            'Y' if a.exterior_displays else 'N',
            'Y' if a.interior_stop_displays else 'N',
            'Y' if a.audio_announcements else 'N',
            'Y' if a.yellow_handrails else 'N',
            'Y' if a.priority_seating else 'N',
            'Y' if a.contrasting_seat_covers else 'N',
            'Y' if a.induction_loop else 'N',
        ])

    for ws in [ws1, ws2, ws3, ws4]:
        for col in ws.columns:
            max_len = max((len(str(cell.value or '')) for cell in col), default=10)
            ws.column_dimensions[col[0].column_letter].width = min(max_len + 4, 40)

    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    filename = f'BORS_{obj.operator_name.replace(" ", "_")}_{obj.data_year}.xlsx'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    wb.save(response)
    return response
