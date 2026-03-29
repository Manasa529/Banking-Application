from django.shortcuts import render, redirect
from django.contrib.auth.hashers import make_password, check_password
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Account, Transaction
import random
import string

def generate_account_number():
    return ''.join(random.choices(string.digits, k=12))

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        if not name or not email or not password:
            messages.error(request, 'Please fill all fields!')
            return render(request, 'register.html')
        
        if Account.objects.filter(email=email).exists():
            messages.error(request, 'Email already registered!')
            return render(request, 'register.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters!')
            return render(request, 'register.html')
        
        try:
            account = Account.objects.create(
                name=name,
                email=email,
                password=make_password(password),
                account_number=generate_account_number(),
                balance=1000.00
            )
            
            Transaction.objects.create(
                account=account,
                type='deposit',
                amount=1000,
                balance_before=0,
                balance_after=1000
            )
            
            # Send welcome email
            send_mail(
                'Welcome to Bankio!',
                f'Dear {name},\n\nWelcome to Bankio! Your account has been created successfully.\n\nAccount Number: {account.account_number}\nWelcome Bonus: $1000\n\nThank you for choosing Bankio!',
                'manasasai2610@gmail.com',
                [email],
                fail_silently=True,
            )
            
            messages.success(request, 'Account created successfully! Please login.')
            return redirect('login')
            
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            return render(request, 'register.html')
    
    return render(request, 'register.html')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            account = Account.objects.get(email=email)
            if check_password(password, account.password):
                request.session['account_id'] = account.id
                request.session['account_name'] = account.name
                messages.success(request, f'Welcome back, {account.name}!')
                return redirect('dashboard')
            else:
                messages.error(request, 'Wrong password!')
        except Account.DoesNotExist:
            messages.error(request, 'Account not found!')
    
    return render(request, 'login.html')

def user_logout(request):
    request.session.flush()
    messages.success(request, 'Logged out!')
    return redirect('home')

def dashboard(request):
    if 'account_id' not in request.session:
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    account = Account.objects.get(id=request.session['account_id'])
    transactions = Transaction.objects.filter(account=account).order_by('-date')[:5]
    
    return render(request, 'dashboard.html', {
        'account': account,
        'transactions': transactions
    })

def deposit(request):
    if 'account_id' not in request.session:
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    account = Account.objects.get(id=request.session['account_id'])
    
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 0))
            
            if amount <= 0:
                messages.error(request, 'Amount must be greater than 0!')
            else:
                balance_before = account.balance
                account.balance += amount
                account.save()
                
                Transaction.objects.create(
                    account=account,
                    type='deposit',
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=account.balance
                )
                
                # Send deposit confirmation email
                send_mail(
                    'Deposit Confirmation - Bankio',
                    f'Dear {account.name},\n\nYou have successfully deposited ${amount} to your account.\n\nTransaction Details:\nAmount: ${amount}\nBalance Before: ${balance_before}\nBalance After: ${account.balance}\n\nThank you for banking with Bankio!',
                    'manasasai2610@gmail.com',
                    [account.email],
                    fail_silently=True,
                )
                
                messages.success(request, f'Deposited ${amount}! New balance: ${account.balance:.2f}')
        except ValueError:
            messages.error(request, 'Please enter a valid amount!')
        
        return redirect('dashboard')
    
    return render(request, 'deposit.html', {'balance': account.balance})

def withdraw(request):
    if 'account_id' not in request.session:
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    account = Account.objects.get(id=request.session['account_id'])
    
    if request.method == 'POST':
        try:
            amount = int(request.POST.get('amount', 0))
            
            if amount <= 0:
                messages.error(request, 'Amount must be greater than 0!')
            elif amount > account.balance:
                messages.error(request, f'Insufficient funds! Balance: ${account.balance:.2f}')
            else:
                balance_before = account.balance
                account.balance -= amount
                account.save()
                
                Transaction.objects.create(
                    account=account,
                    type='withdraw',
                    amount=amount,
                    balance_before=balance_before,
                    balance_after=account.balance
                )
                
                # Send withdrawal confirmation email
                send_mail(
                    'Withdrawal Confirmation - Bankio',
                    f'Dear {account.name},\n\nYou have successfully withdrawn ${amount} from your account.\n\nTransaction Details:\nAmount: ${amount}\nBalance Before: ${balance_before}\nBalance After: ${account.balance}\n\nThank you for banking with Bankio!',
                    'manasasai2610@gmail.com',
                    [account.email],
                    fail_silently=True,
                )
                
                messages.success(request, f'Withdrew ${amount}! Remaining: ${account.balance:.2f}')
        except ValueError:
            messages.error(request, 'Please enter a valid amount!')
        
        return redirect('dashboard')
    
    return render(request, 'withdraw.html', {'balance': account.balance})

def transactions(request):
    if 'account_id' not in request.session:
        messages.error(request, 'Please login first!')
        return redirect('login')
    
    account = Account.objects.get(id=request.session['account_id'])
    all_transactions = Transaction.objects.filter(account=account).order_by('-date')
    
    return render(request, 'transactions.html', {
        'transactions': all_transactions,
        'balance': account.balance
    })