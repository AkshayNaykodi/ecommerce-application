from django.shortcuts import render,redirect
from django.shortcuts import HttpResponse
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth import authenticate,login,logout
from .models import product,cart,order
from django.db.models import Q
import random
import razorpay

# Create your views here.



def contact(request):
    return HttpResponse("<h1> Welcome to contact page </h1>")

def edit(request,rid):
    print("Id to be edited: ",rid)
    return HttpResponse("Id to be edited: "+rid)

def delete(request,rid):
    print("Id to be deleted: ",rid)
    return HttpResponse("Id to be deleted: "+rid)

class SimpleView(View):
    def get(self,request):
        return HttpResponse("Hello From simple view")
    
def hello(request):
    context={}
    context['greet']="Good morning"
    
    context['x']=10
    context['y']=20
    
    context['l']=[1,2,3,4,5]
    
    context['product']=[{'id':1,'name':'Harry','category':'phone','prize':20000},
                      {'id':2,'name':'Mac','category':'Laptop','prize':100000},
                      {'id':3,'name':'Shree','category':'TV','prize':50000}]
    
    return render(request,'hello.html',context)

def home(request):
    context={}
    p=product.objects.filter(is_active=True)
    context['products']=p
    #print=(p)
    return render(request,'index.html',context)

def pdetails(request,pid):
    p=product.objects.filter(id=pid)
    context={}
    context['products']=p
    return render(request,'product_details.html',context)

def register(request):
    if request.method=='POST':
        
        uname=request.POST['uname']
        upass=request.POST['upass']
        ucpass=request.POST['ucpass']
        if uname=="" or upass=="" or ucpass=="":
            context={}
            context['errmsg']="field can not be empty"
            return render(request,'register.html',context)
        
        elif upass!=ucpass:
            context={}
            context['errmsg']="password did not match"
            return render(request,'register.html',context)
        else:
            try:
                u=User.objects.create(username=uname,password=upass,email=uname)
                u.set_password(upass)
                u.save()
                context={}
                context['success']="User created successfully"
                #return HttpResponse("data is fetch successfully") 
                return render(request,'register.html',context) 
            
            except Exception:
                context={}
                context['errmsg']='user already exists'
                return render(request,'register.html',context)
             
    else:
        return render(request,'register.html')

def user_login(request):
    if request.method=="POST":
        uname=request.POST['uname']
        upass=request.POST['upass']
        if uname=="" or upass=="":
            context={}
            context['errmsg']="field can not be empty"
            return render(request,"login.html",context)
        else:
            u=authenticate(username=uname,password=upass)
            #print(u)
            #login(u)
            if u is not None:
                login(request,u)
                #login
                return redirect('/home')
            #return HttpResponse("In Else Part")
            else:
                context={}
                context['errmsg']="Invalid user name and password"
                return render(request,'login.html',context)
        #print(uname)
        #print(upass)
        return HttpResponse("Data is fetched")
    else:
        return render(request,'login.html')
    
    
#def user_login(request):
#    login(request,u)

def user_logout(request):
    logout(request)
    return redirect('/home')

def catfilter(request,cv):
    q1=Q(is_active=True)
    q2=Q(cat=cv)
    p=product.objects.filter(q1&q2)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def sort(request,sv):
    if sv == '0':
        col="price" #asc
    else:
        col = "-price" #desc
        
    p=product.objects.order_by(col)
    context={}
    context['products']=p
    return render(request,'index.html',context)

def range(request):
    min=request.GET['min']
    max=request.GET['max']
    #print(min)
    #print(max)
    #return HttpResponse("value fetched")
    q1=Q(price__gte=min)    #gte= greater than equal   give double underscore betwiin price and gte (_ _)
    q2=Q(price__lte=max)    #lte= less than equal
    q3=Q(is_active=True)
    p=product.objects.filter(q1 & q2 & q3)
    context={}
    context['products']=p
    return render(request,'index.html',context)


def addtocart(request,pid):
    userid = request.user.id
    u=User.objects.filter(id=userid)
    print(u[0])
    p=product.objects.filter(id=pid)
    print(p[0])
    q1=Q(uid=u[0])
    q2=Q(pid=p[0])
    c=cart.objects.filter(q1 and q2)
    n=len(c)
    print(n)
    context={}
    context['products']=p
    if n==1:
        context['msg']="Product already exist in the cart"
    else:
        c=cart.objects.create(uid=u[0],pid=p[0])
        c.save()
        context={}
        context['products']=p
        context['success']="Product added"
        #print(pid)
        #print(userid)
        #return HttpResponse("id is fetched")
    return render(request,'product_details.html',context)

# def add_to_cart(request, pid):
#     product = get_object_or_404(Product, pk=pid)
#     cart = request.user.cart

#     # Check if the product is already in the cart
#     if cart.products.filter(pk=pid).exists():
#         # Product already in the cart, handle accordingly (e.g., show a message)
#         pass
#     else:
#         # Product not in the cart, add it
#         cart_item = cart.objects.create(cart=cart, product=product)

#     return redirect('cart')  # Redirect to the cart page

def viewcart(request):
    if request.user.is_authenticated:
        c=cart.objects.filter(uid=request.user.id)
        np=len(c)
        s=0
        for x in c:
            #print(x)
            #print(x.pid.price)
            s=s+x.pid.price*x.qty
        
        print(s)    
        context={}
        context['products']=c
        context['total']=s
        context['n']=np
        return render(request,'cart.html',context)
    else:
        return redirect('/login')

def remove(request,cid):
    c=cart.objects.filter(id=cid)
    c.delete()
    return redirect('/viewcart')

def updateqty(request,qv,cid):
    c=cart.objects.filter(id=cid)
    #print(c)
    #print(c[0])
    #print(c[0].qty)
    if qv == '1':
        t=c[0].qty+1
        c.update(qty=t)
    else:
        if c[0].qty > 1:
            t=c[0].qty-1
            c.update(qty=t)
    #return HttpResponse("quantity updated")
    return redirect('/viewcart')

def placeorder(request):
    userid=request.user.id
    #print(userid)
    c=cart.objects.filter(uid=userid)
    #print(c)
    oid=random.randrange(1000,9999)
    #print(oid)
    for x in c:
        print(x)
        print(x.pid)
        print(x.qty)
        o=order.objects.create(order_id=oid,pid=x.pid,uid=x.uid,qty=x.qty)
        o.save()  # shift data into order table
        x.delete() # delete records from cart table
        
    orders=order.objects.filter(uid=userid)
    np=len(orders)
    s=0
    for x in orders:
        #print(x)
        #print(x.pid.price)
        s=s+x.pid.price*x.qty
        
    print(s)    
    context={}
    context['products']=orders
    context['total']=s
    context['n']=np
    #return HttpResponse("Place order successfully")
    return render(request,'placeorder.html',context)

def makepayment(request):
    orders=order.objects.filter(uid=request.user.id)
    s=0
    for x in orders:
        #print(x)
        #print(x.pid.price)
        s=s+x.pid.price*x.qty
        oid=x.order_id
    client = razorpay.Client(auth=("rzp_test_WT8RH4yp8LIGAH", "9yFuyDNu4pScDXudYS6uaTsl"))

    DATA = {
                "amount": s*100,
                "currency": "INR",
                "receipt": oid,
                "notes": {
                    "key1": "value3",
                    "key2": "value2"
                        }
            }
    payment=client.order.create(data=DATA)
    print(payment)
    uname=request.user.username
    print(uname)
    context={}
    context['data']=payment
    client.order.create(data=DATA)
    #return HttpResponse("in payment section")
    return render(request,'pay.html',context)