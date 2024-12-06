from django.shortcuts import render
from django.db.models import Sum
from .models import KsebCds, CdsDailyData, CdsPreset

def round_to_two(value):
    """Helper function to round a value to 2 decimal places."""
    return round(value, 2)

def calculate_totals(sections):
    # Aggregate total value for the given sections
    total_value = CdsDailyData.objects.aggregate(Sum("value"))['value__sum'] or 0
    # Aggregate actual quantity for the given sections
    actual_qty = CdsPreset.objects.aggregate(Sum('actual_qty'))['actual_qty__sum'] or 0
    qty_ulccs = CdsPreset.objects.aggregate(Sum('qty_ulccs'))['qty_ulccs__sum'] or 0
    
    # Calculate the completion percentage
    completion_percentage = (total_value / actual_qty) * 100 if actual_qty > 0 else 0

    # return total_value, actual_qty, completion_percentage, qty_ulccs
      # Round values to two decimal places
    return (
        round_to_two(total_value),
        round_to_two(actual_qty),
        round_to_two(completion_percentage),
        round_to_two(qty_ulccs)
    )


def index(request):
    # Get selected filters (circle and division) from GET parameters
    selected_circle_id = request.GET.get('circleFilter', None)
    selected_division_id = request.GET.get('divisionFilter', None)
    # Fetch the circle
    circle = KsebCds.objects.get(title="Kozhikode", category=KsebCds.CategoryChoices.CIRCLE)

    # Fetch divisions explicitly by their parent and title
    balussery = KsebCds.objects.get(title="Balussery", parent=circle, category=KsebCds.CategoryChoices.DIVISION)
    kozhikode = KsebCds.objects.get(title="Kozhikode", parent=circle, category=KsebCds.CategoryChoices.DIVISION)
    feroke = KsebCds.objects.get(title="Feroke", parent=circle, category=KsebCds.CategoryChoices.DIVISION)

    # Fetch sections for each division explicitly
    balussery_sections = KsebCds.objects.filter(parent=balussery, category=KsebCds.CategoryChoices.SECTION)
    kozhikode_sections = KsebCds.objects.filter(parent=kozhikode, category=KsebCds.CategoryChoices.SECTION)
    feroke_sections = KsebCds.objects.filter(parent=feroke, category=KsebCds.CategoryChoices.SECTION)

    # Calculate totals for the circle
    circle_sections = KsebCds.objects.filter(category=KsebCds.CategoryChoices.SECTION, parent__parent=circle)
    total_value, total_actual_qty, completion_percentage, total_qty_ulccs = calculate_totals(circle_sections)

    # Calculate totals for each division explicitly
    balussery_totals = calculate_totals(balussery_sections)
    kozhikode_totals = calculate_totals(kozhikode_sections)
    feroke_totals = calculate_totals(feroke_sections)
    
        # Fetch the list of circles and divisions
    circles = KsebCds.objects.filter(category=KsebCds.CategoryChoices.CIRCLE)
    divisions = KsebCds.objects.filter(category=KsebCds.CategoryChoices.DIVISION)

    # Filtering sections based on selected circle and division
    sections = KsebCds.objects.filter(category=KsebCds.CategoryChoices.SECTION)

    if selected_circle_id:
        sections = sections.filter(parent__parent__id=selected_circle_id)

    if selected_division_id:
        sections = sections.filter(parent__id=selected_division_id)

    # Pass data to the context
    context = {
        'circles': circles,
        'division': divisions,
        'sections': sections,
        'selected_circle_id': selected_circle_id,
        'selected_division_id': selected_division_id,
        'circle': {
            'name': circle.title,
            'total_value': total_value,
            'total_actual_qty': total_actual_qty,
            'completion_percentage': completion_percentage,
            'total_qty_ulccs': total_qty_ulccs,
        },
        'divisions': {
            'balussery': {
                'name': balussery.title,
                'total_value': balussery_totals[0],
                'total_actual_qty': balussery_totals[1],
                'completion_percentage': balussery_totals[2],
                'total_qty_ulccs': balussery_totals[3],
            },
        'kozhikode': {
                'name': kozhikode.title,
                'total_value': kozhikode_totals[0],
                'total_actual_qty': kozhikode_totals[1],
                'completion_percentage': kozhikode_totals[2],
                'total_qty_ulccs': kozhikode_totals[3],
            },
        'feroke': {
                'name': feroke.title,
                'total_value': feroke_totals[0],
                'total_actual_qty': feroke_totals[1],
                'completion_percentage': feroke_totals[2],
                'total_qty_ulccs': feroke_totals[3],
            },
        },
    }

    return render(request, 'index.html', context)

from django.http import JsonResponse
from .models import KsebCds

def get_sections(request):
    division_id = request.GET.get('division_id')

    if division_id:
        sections = KsebCds.objects.filter(parent_id=division_id, category=KsebCds.CategoryChoices.SECTION)
        sections_data = []

        for section in sections:
            sections_data.append({
                'id': section.id,
                'title': section.title,
                'total_value': section.total_value,
                'completion_percentage': section.completion_percentage,
                'actual_qty': section.actual_qty,
                'qty_ulccs': section.qty_ulccs,
            })

        return JsonResponse({'sections': sections_data})

    return JsonResponse({'sections': []})

