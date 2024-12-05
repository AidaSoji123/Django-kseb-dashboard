from django.shortcuts import render
from django.db.models import Sum
from .models import KsebCds, CdsDailyData, CdsPreset


def calculate_totals(sections):
    """
    Utility function to calculate total value, actual quantity, and completion percentage
    for a given set of sections.
    """
    total_value = CdsDailyData.objects.filter(section__in=sections).aggregate(
        total_value=Sum('value')
    )['total_value'] or 0

    actual_qty = CdsPreset.objects.filter(section__in=sections).aggregate(
        actual_qty=Sum('actual_qty')
    )['actual_qty'] or 0

    completion_percentage = (total_value / actual_qty) * 100 if actual_qty > 0 else 0

    return total_value, actual_qty, completion_percentage


def index(request):
    # Fetch Circles, Divisions, and Sections
    circles = KsebCds.objects.filter(category=KsebCds.CategoryChoices.CIRCLE)
    divisions = KsebCds.objects.filter(category=KsebCds.CategoryChoices.DIVISION)
    sections = KsebCds.objects.filter(category=KsebCds.CategoryChoices.SECTION)

    # Overview block data
    overview_blocks = [
        {"name": "Total Circles", "value": circles.count()},
        {"name": "Total Divisions", "value": divisions.count()},
        {"name": "Total Sections", "value": sections.count()},
    ]

    # Calculate totals for each circle
    for circle in circles:
        # Fetch sections under all divisions of the circle
        circle_sections = sections.filter(parent__parent=circle)
        # Calculate totals for the circle
        circle.total_value, circle.total_actual_qty, circle.completion_percentage = calculate_totals(circle_sections)

    # Calculate totals for each division
    for division in divisions:
        # Fetch sections under this division
        division_sections = sections.filter(parent=division)
        # Calculate totals for the division
        division.total_value, division.total_actual_qty, division.completion_percentage = calculate_totals(division_sections)

    # Calculate totals for each section
    for section in sections:
        # Each section is a single unit, so pass it as a queryset
        section.total_value, section.total_actual_qty, section.completion_percentage = calculate_totals([section])

    # Pass data to the context
    context = {
        'circles': circles,
        'divisions': divisions,
        'sections': sections,
        'overview_blocks': overview_blocks,
    }

    return render(request, 'index.html', context)
