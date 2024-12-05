from django.db import models


class KsebCds(models.Model):
    class CategoryChoices(models.TextChoices):
        CIRCLE = "circle", "Circle"
        DIVISION = "division", "Division"
        SECTION = "section", "Section"

    title = models.CharField(max_length=50)
    category = models.CharField(max_length=100, choices=CategoryChoices.choices)
    parent = models.ForeignKey("self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children")
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class CdsDailyData(models.Model):
    section = models.ForeignKey(KsebCds, on_delete=models.CASCADE, related_name="daily_data")
    date = models.DateField()
    value = models.FloatField()

    def __str__(self):
        return f"Data for {self.section.title} on {self.date}"


class CdsDailyDataImport(models.Model):
    section = models.ForeignKey(KsebCds, on_delete=models.CASCADE, related_name="imported_data")
    section_name = models.CharField(max_length=50)
    date = models.DateField()
    value = models.FloatField()

    def __str__(self):
        return f"Imported data for {self.section_name} on {self.date}"


class CdsPreset(models.Model):
    section = models.ForeignKey(KsebCds, on_delete=models.CASCADE, related_name="presets")
    actual_qty = models.FloatField()
    qty_ulccs = models.FloatField()

    def __str__(self):
        return f"Preset for {self.section.title}"
