from django.db import models

# Create your models here.
class Component(models.Model):
    name=models.CharField(max_length=50)
    category=models.CharField(max_length=10)
    description=models.TextField()
    unitMeasure=models.CharField(max_length=8)
    costPerUnit=models.IntegerField()
    currentStock=models.PositiveIntegerField()
    maximumStock=models.PositiveIntegerField()
    safeStock=models.PositiveIntegerField()
    industryLine=models.CharField(max_length=15)
    suppliedBy=models.CharField(max_length=25)

    def __str__(self):
        return f"{self.name}"

class Usage(models.Model):
    component=models.ForeignKey(Component,on_delete=models.CASCADE,related_name="usages")
    quantityUsed=models.PositiveIntegerField()
    dateAndTime=models.DateTimeField()

    def __str__(self):
        return f"{self.component.name} on {self.dateAndTime}"