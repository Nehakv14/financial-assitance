from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import SignUpForm
from .models import FinancialGoal
import os, json
from django.views.decorators.http import require_POST


# Load environment variables

# Sign-up
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data['email']
            user.save()
            return redirect('login')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

# Login
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'accounts/login.html', {'error': 'Invalid credentials'})
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return redirect('dashboard')
# Home
def home_view(request):
    return render(request, 'accounts/home.html')

# Dashboard
@login_required(login_url='login')
def dashboard_view(request):
    return render(request, 'accounts/dashboard.html')



# Finance Assistant View
@login_required(login_url='login')
def finance_assistant_view(request):
    error = None
    if request.method == 'POST':
        try:
            age = int(request.POST.get('age', 0))
            income = int(request.POST.get('income', 0))
            expenses = int(request.POST.get('expenses', 0))
            risk = request.POST.get('risk_appetite', 'medium')
            goal = request.POST.get('goal', '')

            if income <= 0 or expenses < 0 or age <= 0:
                raise ValueError("Please fill all fields correctly.")

            savings = income - expenses
            amount_to_invest = savings * 0.3 if savings > 0 else 0

            beginner_plans = [
                "1. Start a Recurring Deposit (RD)",
                "2. Invest small amounts in SIPs (Mutual Funds)",
                "3. Open a Sukanya Samriddhi or PPF Account"
            ]

            tax_saving_tips = [
                "Invest in ELSS Mutual Funds under Section 80C",
                "Buy Health Insurance (Deduction under 80D)",
                "Use NPS (National Pension Scheme) for extra 50K deduction"
            ]

            if age < 20:
                plans = beginner_plans
                recommended_bank = "Post Office or Paytm Money"
            else:
                if risk == 'low':
                    plans = ["PPF", "Fixed Deposits", "Post Office Schemes"]
                    recommended_bank = "SBI, Post Office"
                elif risk == 'medium':
                    plans = ["Balanced Mutual Funds", "Gold ETFs", "Life Insurance"]
                    recommended_bank = "HDFC, Axis Mutual Fund"
                else:
                    plans = ["Equity Funds", "SIP in Small-Caps", "Direct Stocks"]
                    recommended_bank = "Zerodha, Groww"

            graph_labels = ['Low Risk', 'Medium Risk', 'High Risk']
            graph_values = [2, 5, 9] if age < 20 else [3, 6, 9]
            monthly_saving_projection = [round(savings * (1 + 0.02 * i)) for i in range(6)] if savings > 0 else [0] * 6

            user_goals = FinancialGoal.objects.filter(user=request.user)

            suggestions = {
                'plans': plans,
                'bank': recommended_bank,
                'income': income,
                'expenses': expenses,
                'savings': savings,
                'amount': round(amount_to_invest),
                'graph_labels_json': json.dumps(graph_labels),
                'graph_values_json': json.dumps(graph_values),
                'monthly_projection_json': json.dumps(monthly_saving_projection),
                'ai_response': None,
                'goals': user_goals,
                'tax_tips': tax_saving_tips
            }

            return render(request, 'finance_assistant_view/investment_suggestor.html', {
                'suggestions': suggestions,
                'error': None
            })

        except Exception as e:
            error = str(e)

    # For GET or in case of error
    suggestions = {
        'plans': [],
        'bank': '',
        'income': 0,
        'expenses': 0,
        'savings': 0,
        'amount': 0,
        'graph_labels_json': json.dumps(['Low Risk', 'Medium Risk', 'High Risk']),
        'graph_values_json': json.dumps([0, 0, 0]),
        'monthly_projection_json': json.dumps([0] * 6),
        'ai_response': None,
        'goals': FinancialGoal.objects.filter(user=request.user),
        'tax_tips': []
    }

    return render(request, 'finance_assistant_view/investment_suggestor.html', {
        'suggestions': suggestions,
        'error': error
    })

from django.shortcuts import render
from django.http import JsonResponse
from gtts import gTTS
import os
import uuid
from difflib import get_close_matches  # 👈 NEW

def AIAssistant(request):
    return render(request, 'accounts/AIAssistant.html')


    # FAQ dictionary
FAQS = {
    "Hi": "yes,please continue to ask your question",
    "How much should I save every month?": "Ideally, try to save at least 20% of your monthly income.",
    "How to budget with a weekly salary?": "Divide your income into daily expenses and save a portion each week.",
    "Which expenses should I reduce?": "Cut down on unnecessary subscriptions and luxury expenses.",
    "What is EMI and what's the risk?": "EMI stands for Equated Monthly Installment. Missing payments can lead to higher interest and loan burden.",
    "How to set a strong savings goal?": "Be clear about your goal and set a timeline to achieve it.",
    "How to open a bank account?": "You need ID proof (like Aadhaar or PAN), a photo, and address proof. Visit your nearest bank and fill the application form.",
    "What is a savings account?": "A savings account is a basic bank account where you can deposit money and earn interest.",
    "What is interest rate?": "It’s the percentage your bank pays you on your savings.",
    "What’s the difference between debit and credit card?": "A debit card uses your existing balance. A credit card lets you borrow from the bank.",
    "How long can I keep a free bank account?": "Most banks offer basic accounts with no annual fees, but rules vary by bank.",
}


def steps_to_create_account(request):
    return render(request, 'accounts/create_account_steps.html')

def financeeducation(request):
    return render(request, 'accounts/financeeducation.html')

def chatbot_view(request):
    query = request.GET.get('query', '').strip()
    lang = request.GET.get('lang', 'en')

    # 🧠 Use fuzzy matching to find closest FAQ
    matches = get_close_matches(query, FAQS.keys(), n=1, cutoff=0.5)

    if matches:
        response = FAQS[matches[0]]
    else:
        response = "Sorry i could not understand your question,could you repeat it?."

    # 🎵 Generate audio
    os.makedirs("media", exist_ok=True)
    filename = f"{uuid.uuid4()}.mp3"
    audio_path = os.path.join("media", filename)
    tts = gTTS(response, lang=lang)
    tts.save(audio_path)

    return JsonResponse({
        'response': response,
        'audio': f'/media/{filename}',
    })

def steps_to_create_account(request):
    return render(request, 'accounts/create_account_steps.html')

def financeeducation(request):
    return render(request, 'accounts/financeeducation.html')




# views.py
from django.shortcuts import render, redirect
from .forms import BudgetEntryForm
from .models import BudgetEntry
import json

def budget_tracker(request):
    if request.method == 'POST':
        form = BudgetEntryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('budget_tracker')
    else:
        form = BudgetEntryForm()

    entries = BudgetEntry.objects.all()
    chart_data = [
        {
            'month': entry.month,
            'budget': entry.budget,
            'expenses': entry.expenses
        }
        for entry in entries
    ]

    context = {
        'form': form,
        'chart_data': json.dumps(chart_data)
    }
    return render(request, 'accounts/budget_tracker.html', context)
