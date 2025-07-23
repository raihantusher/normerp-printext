from django.shortcuts import render

# Create your yyyyyviews here. yyyyyyyyy   YYYYYYyYYYYYYYYYYYYYYY

def Home(req):
    return render(req, 'backend/dashboard_base.html')



def Customers(req):
    return render(req, 'backend/customer/home.html')
