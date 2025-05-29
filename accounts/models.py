from django.db import models
from django.contrib.auth.models import User

class FinancialGoal(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    goal_name = models.CharField(max_length=100)
    target_amount = models.PositiveIntegerField()
    duration_months = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.goal_name}"
    
class BudgetEntry(models.Model):
    month = models.CharField(max_length=20)
    budget = models.FloatField()
    expenses = models.FloatField()

    def _str_(self):
        return f"{self.month}: Budget {self.budget}, Expenses {self.expenses}"
