from django.shortcuts import render,HttpResponseRedirect,HttpResponse

# Create your views here.

def LoginUser(request):
    if request.method=='GET':
        return render(request,'login.html')
    elif request.method=='POST':
        print('hi................')
        Login_id = request.POST.get('loginid')
        Password = request.POST.get('psw')
        if Login_id=='123456':
            if Password=='123456':
                return HttpResponseRedirect("/home")
            else:
                return HttpResponse('Incorrect Password')
        else:
            return HttpResponse('Incorrect Login Id')
    
