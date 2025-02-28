from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Farm(models.Model):
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class FinancialCategory(models.Model):
    name = models.CharField(max_length=50)  # e.g., "Milk Sales", "Feed"
    is_income = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class FinancialRecord(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    category = models.ForeignKey(FinancialCategory, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    date = models.DateField(auto_now_add=True)  # Auto-set to current date
    recorded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='financial_records')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.category.name} - {self.amount} ETB ({self.date})"

class ProfitSnapshot(models.Model):
    farm = models.ForeignKey(Farm, on_delete=models.CASCADE)
    total_income = models.DecimalField(max_digits=12, decimal_places=2)
    total_expense = models.DecimalField(max_digits=12, decimal_places=2)
    net_profit = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField(auto_now_add=True)  # Auto-set to current date

    def calculate_profit(self):
        self.net_profit = self.total_income - self.total_expense
        self.save()

    def __str__(self):
        return f"{self.farm.name} Profit on {self.date}: {self.net_profit} ETB"