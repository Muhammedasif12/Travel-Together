from django.shortcuts import render, redirect, HttpResponseRedirect
from .models import *
from django.db.models import Q, Sum
from django.contrib.auth import authenticate, login
from django.contrib import messages
from datetime import datetime, date
from django.core.mail import send_mail
from django.utils import timezone


# Create your views here.


# def send_email(request):
#     if request.POST:
#         sub=request.POST['subject']
#         msg=request.POST['message']
#         receiver=request.POST['receiver']

#         from_email = 'forpythonjava@gmail.com'
#         recipient_list = [receiver]
#         result=send_mail(sub, msg, from_email, recipient_list)
#         print(result)
#     return render(request,"sendMail.html")


def logout(request):
    request.session.clear()
    messages.success(request, "Logged Out")
    return HttpResponseRedirect("/signin")


def index(request):
    return render(request, "index.html")


def contact(request):
    return render(request, "contact.html")


def userRegister(request):
    return render(request, "COMMON/userRegister.html")


def artistRegister(request):
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        password = request.POST["password"]
        address = request.POST["address"]
        skill = request.POST.getlist("skills")
        sk = str(skill)
        cleaned_word = (
            sk.replace("[", "").replace("]", "").replace("'", "")
        )  # Retrieve the submitted skills value
        images = request.FILES["image"]
        if Login.objects.filter(username=email).exists():
            messages.error(request, "Email Already Exists")
        else:
            logQry = Login.objects.create_user(
                username=email,
                password=password,
                userType="Artist",
                viewPass=password,
                is_active=1,
            )
            logQry.save()
            if logQry:
                artistReg = Artist.objects.create(
                    name=name,
                    email=email,
                    phone=phone,
                    address=address,
                    skills=cleaned_word,
                    image1=images,
                    
                    loginid=logQry,
                )
                artistReg.save()
                messages.success(request, "Registration Successfull")
                return redirect("/signin")
    return render(request, "COMMON/artistRegister.html")


def userRegister(request):
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        password = request.POST["password"]
        address = request.POST["address"]

        if Login.objects.filter(username=email).exists():
            messages.error(request, "Email Already Exists")
        else:
            logQry = Login.objects.create_user(
                username=email,
                password=password,
                userType="User",
                viewPass=password,
                is_active=1,
            )
            logQry.save()
            if logQry:
                userReg = User.objects.create(
                    name=name, email=email, phone=phone, address=address, loginid=logQry
                )
                userReg.save()
                messages.success(request, "Registration Successfull")
                return redirect("/signin")
    return render(request, "COMMON/userRegister.html")


def signin(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        
        user = authenticate(username=email, password=password)
        
        if user is not None:
            if user.userType == "Artist":
                try:
                    artist = Artist.objects.get(email=email)
                    if artist.status == "Not Paid":
                        request.session["payMail"] = email
                        messages.error(request, "Please Complete Payment 💸 To Login")
                        return redirect("/payFees")
                    else:
                        login(request, user)
                        request.session["uid"] = user.id
                        messages.info(request, "Login Success")
                        return redirect("/artistHome")
                except Artist.DoesNotExist:
                    messages.error(request, "Artist information not found.")
            elif user.userType == "User":
                login(request, user)
                request.session["uid"] = user.id
                request.session["type"] = "User"
                messages.info(request, "Login Success")
                return redirect("/userHome")
            elif user.userType == "Admin":
                login(request, user)
                request.session["type"] = "Admin"
                messages.info(request, "Login Success")
                return redirect("/adminHome")
        else:
            messages.error(request, "Incorrect Email/Password..😥")
    
    return render(request, "COMMON/login.html")


######################################################--ARTIST--#########################################################


def artistHome(request):
    if "uid" not in request.session:
        messages.error(request, "Please login to continue")
        return redirect("/signin")
    
    uid = request.session["uid"]
    current_date = date.today()
    CheckPay = Login.objects.get(id=uid)
    rgDate = CheckPay.regDate
    diff = current_date - rgDate
    days = diff.days
    print(days)
    if days >= 30:
        changeStatus = Artist.objects.filter(loginid=uid).update(status="Not Paid")
        messages.error(
            request,
            "Your membership has expired. Please renew to continue using our services.",
        )
        return redirect("/logout")
    else:
        print("Helloo")
    myProfile = Artist.objects.get(loginid=uid)
    gchat = GChat.objects.filter(artistid=myProfile.id, status='requested')
    unread_count = Notification.objects.filter(artist=myProfile, is_read=False).count()
    return render(request, "ARTIST/artistHome.html", {"gchat": gchat, "unread_count": unread_count})


def payFees(request):
    current_date = date.today()
    payMail = request.session["payMail"]
    cartTotal = 750
    if request.POST:
        payStatus = Artist.objects.get(email=payMail)
        payStatus.status = "Paid"
        payStatus.save()
        regDate = Login.objects.get(username=payMail)
        regDate.regDate = current_date
        regDate.save()
        messages.success(request, "Payment Successfull..😀 Proceed to Login")
        return redirect("/signin")
    return render(request, "ARTIST/payFees.html", {"cartTotal": cartTotal})


def profile(request):
    if "uid" not in request.session:
        messages.error(request, "Please login to continue")
        return redirect("/signin")
    
    uid = request.session["uid"]
    myProfile = Artist.objects.get(loginid_id__id=uid)
    print(myProfile)
    gchat = GChat.objects.filter(artistid=myProfile.id,status='requested')
    print(gchat)
    return render(request, "ARTIST/profile.html", {"myProfile": myProfile,"gchat":gchat})


def updateProfile(request):
    if "uid" not in request.session:
        messages.error(request, "Please login to continue")
        return redirect("/signin")
    
    uid = request.session["uid"]
    myProfile = Artist.objects.get(loginid_id__id=uid)
    print(myProfile)

    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        password = request.POST["password"]
        address = request.POST["address"]
        skill = request.POST.getlist("skills")
        sk = str(skill)
        cleaned_word = (
            sk.replace("[", "").replace("]", "").replace("'", "")
        )  # Retrieve the submitted skills value
        images = request.FILES['image']

        updateProfile = Artist.objects.get(loginid=uid)
        updateProfile.name = name
        updateProfile.email = email
        updateProfile.phone = phone
        updateProfile.address = address
        updateProfile.skills = cleaned_word
        updateProfile.image1 = images
        
        updateProfile.save()

        updateLogin = Login.objects.get(id=uid)
        updateLogin.username = email
        updateLogin.set_password(password)
        updateLogin.viewPass = password
        updateLogin.save()
        messages.success(request, "Profile Updated")
        return redirect("/profile")
    return render(request, "ARTIST/updateProfile.html", {"myProfile": myProfile})


def addItems(request):
    if "uid" not in request.session:
        messages.error(request, "Please login to continue")
        return redirect("/signin")
    
    id = request.session["uid"]
    uid = Artist.objects.get(loginid=id)
    options = [
    "Active",
    "Beach & Relaxation",
    "City Breaks",
    "Culture & History",
    "Cycling",
    "Escorted",
    "Expedition Cruising",
    "Family",
    "Food & Wine",
    "Honeymoons",
    "Luxury",
    "Off-the-Beaten Track",
    "Overland",
    "Self-Drive",
    "Skiing",
    "Solo Traveller",
    "Spa Holidays",
    "Tailor-Made",
    "Train & River Journeys",
    "Walking & Trekking",
    "Wildlife & Safaris"
]
    if request.POST:
        name = request.POST["pdtname"]
        category = request.POST["category"]
        price = request.POST["price"]
        color = request.POST["color"]
        qty = request.POST["qty"]
        image = request.FILES["image"]
        desc = request.POST["desc"]
        tripdate = request.POST["tripdate"]
        addItems = Products.objects.create(
            name=name,
            category=category,
            price=price,
            color=color,
            qty=qty,
            image=image,
            desc=desc,
            artistId=uid,
            tripday = tripdate,
        )
        addItems.save()
        messages.success(request, "Package Added")
        return redirect("/viewItems")
    return render(request, "ARTIST/addItems.html", {"options": options})


def viewItems(request):
    if "uid" not in request.session:
        messages.error(request, "Please login to continue")
        return redirect("/signin")
    
    uid = request.session["uid"]

    artist = Artist.objects.get(loginid=uid)  

    items = Products.objects.filter(artistId=artist).exclude(status="Cancelled")

    print(items)

    return render(request, "ARTIST/viewItems.html", {"items": items})

def viewReports(request):
    if "uid" not in request.session:
        messages.error(request, "Please login to continue")
        return redirect("/signin")
    uid = request.session["uid"]

    # ALL bookings including cancelled — coordinator should see everything
    all_items = Cart.objects.filter(pid__artistId__loginid=uid)

    # Only paid ones for revenue calculation
    paid_items = all_items.filter(status="Paid")
    total_revenue = paid_items.aggregate(total=Sum("price"))["total"] or 0
    completed = paid_items.filter(completedpay=1).count()
    total_cancelled = all_items.filter(status="Cancelled").count()

    return render(request, "ARTIST/agencyviewreport.html", {
        "items": all_items,
        "total_revenue": total_revenue,
        "completed": completed,
        "total_cancelled": total_cancelled,
    })

def deleteProduct(request):
    id = request.GET["id"]
    deletePdt = Products.objects.get(id=id).delete()
    messages.success(request, "Package Deleted")
    return redirect("/viewItems")


def updateProduct(request):
    id = request.GET["id"]
    options = [
    "Active",
    "Beach & Relaxation",
    "City Breaks",
    "Culture & History",
    "Cycling",
    "Escorted",
    "Expedition Cruising",
    "Family",
    "Food & Wine",
    "Honeymoons",
    "Luxury",
    "Off-the-Beaten Track",
    "Overland",
    "Self-Drive",
    "Skiing",
    "Solo Traveller",
    "Spa Holidays",
    "Tailor-Made",
    "Train & River Journeys",
    "Walking & Trekking",
    "Wildlife & Safaris"
]
    pdtData = Products.objects.get(id=id)
    if request.POST:
        name = request.POST["pdtname"]
        category = request.POST["category"]
        price = request.POST["price"]
        color = request.POST["color"]
        qty = request.POST["qty"]
        image = request.FILES["image"]
        desc = request.POST["desc"]
        tripdate = request.POST["tripdate"]

        updateProduct = Products.objects.get(id=id)
        updateProduct.name = name
        updateProduct.category = category
        updateProduct.price = price
        updateProduct.color = color
        updateProduct.qty = qty
        updateProduct.image = image
        updateProduct.desc = desc
        updateProduct.tripday = tripdate
        updateProduct.save()
        messages.success(request, "Details Updated")
        return redirect("/viewItems")
    return render(request, "ARTIST/updateProduct.html", {"pdtData": pdtData, "category": options})
    
def viewRating(request):
    uid=request.session['uid']
    pdtData = Products.objects.filter(artistId__loginid=uid)
    rating = Feedback.objects.filter(oid__pid__artistId__loginid_id=uid)
    print(rating)
    combined_data = zip(pdtData, rating)
    merged_query = list(combined_data)
    print("MERGED",merged_query)
    return render(request,"ARTIST/viewratings.html",{"data":merged_query})

def coordinatorCancelTrip(request):
    uid = request.session.get("uid")
    package_id = request.GET.get("id")

    if request.method == "GET":
        try:
            artist = Artist.objects.get(loginid=uid)
            package = Products.objects.get(id=package_id, artistId=artist)
            booked_count = Cart.objects.filter(pid=package, status="Paid").count()
            return render(request, "ARTIST/cancelTrip.html", {
                "package": package,
                "booked_count": booked_count
            })
        except Exception as e:
            messages.error(request, f"Package not found: {str(e)}")
            return redirect("/viewItems/")

    if request.method == "POST":
        package_id = request.POST.get("package_id")
        reason = request.POST.get("reason", "No reason provided")
        try:
            artist = Artist.objects.get(loginid=uid)
            package = Products.objects.get(id=package_id, artistId=artist)
            booked_carts = Cart.objects.filter(pid=package, status="Paid")

            for cart in booked_carts:
                package.qty += cart.quantity
                if cart.completedpay == 1:
                    refund_msg = "Full Refund — your full payment will be refunded within 5-7 business days."
                else:
                    refund_msg = "Partial Refund — your partial payment will be refunded within 5-7 business days."
                cart.status = "Cancelled"
                cart.cancellation_reason = reason
                cart.cancelled_by = f"Coordinator ({artist.name})"
                cart.save()
                Notification.objects.create(
                    user=cart.uid,
                    message=f"🚫 Your trip '{package.name}' has been cancelled by the coordinator. Reason: {reason}. {refund_msg}",
                    notif_type="cancellation"
                )

            package.status = "Cancelled"
            package.save()

            Notification.objects.create(
                artist=artist,
                message=f"✅ You cancelled the trip '{package.name}'. Reason: {reason}. {booked_carts.count()} users were notified.",
                notif_type="cancellation"
            )
            messages.success(request, f"Trip '{package.name}' has been cancelled successfully.")
        except Exception as e:
            messages.error(request, f"Could not cancel trip: {str(e)}")
        return redirect("/viewItems/")
    

######################################################--ADMIN--#########################################################


def adminViewArtist(request):
    data = Artist.objects.filter(status="Paid")
    return render(request, "ADMIN/adminViewArtist.html", {"data": data})

def adminViewFeedback(request):
    data = Feedback.objects.all()
    return render(request, "ADMIN/adminViewFeedback.html", {"data": data})


def manageRequest(request):
    id = request.GET["id"]
    status = request.GET["status"]
    updateData = Login.objects.get(id=id)
    if status == "Approved":
        updateData.is_active = 1
        updateData.save()
    elif status == "Rejected":
        updateData.is_active = 0
        updateData.save()
    else:
        updateData = Artist.objects.get(loginid=id).delete()
    messages.success(request, f"Request {status}")
    return redirect("/adminViewArtist")


def adminHome(request):
    return render(request, "ADMIN/adminHome.html")


def adminViewProducts(request):
    productData = Products.objects.exclude(status="Cancelled").order_by('-uploaded')
    return render(request, "ADMIN/adminViewProducts.html", {"productData": productData})


def approveProduct(request):
    id = request.GET["id"]
    approvePdt = Products.objects.filter(id=id).update(status="Approved")
    return redirect("/adminViewProducts")




######################################################--USER--#########################################################
def userHome(request):
    uid = request.session['uid']
    matching_categories = Cart.objects.filter(uid__loginid=uid).values_list('pid__category', flat=True).distinct()
    common_products = Products.objects.filter(status="Approved")
    try:
        user = User.objects.get(loginid=uid)
        unread_count = Notification.objects.filter(user=user, is_read=False).count()
    except:
        unread_count = 0
    return render(request, "USER/userHome.html",{"common_products":common_products, "unread_count": unread_count})

def userProfile(request):
    uid = request.session["uid"]
    user = User.objects.get(loginid=uid)
    return render(request, "USER/userProfile.html", {"user": user})


def updateUserProfilePage(request):
    uid = request.session["uid"]
    user = User.objects.get(loginid=uid)
    return render(request, "USER/updateUserProfile.html", {"user": user})

def updateUserProfile(request):
    uid = request.session["uid"]
    user = User.objects.get(loginid=uid)
    if request.POST:
        name = request.POST["name"]
        email = request.POST["email"]
        phone = request.POST["phone"]
        address = request.POST["address"]
        password = request.POST["password"]

        user.name = name
        user.email = email
        user.phone = phone
        user.address = address
        user.save()

        loginUser = Login.objects.get(id=uid)
        loginUser.username = email
        loginUser.set_password(password)
        loginUser.viewPass = password
        loginUser.save()

        messages.success(request, "Profile updated successfully!")
        return redirect("/userProfile/")
    return redirect("/userProfile/")


def userViewProduct(request):
    uid = request.session["uid"]
    wishListData = Wishlist.objects.filter(uid__loginid=uid).values_list(
        "pid", flat=True
    )
    print(wishListData)
    productData = Products.objects.filter(status="Approved").order_by('-uploaded')
    return render(
        request,
        "USER/viewProducts.html",
        {"productData": productData, "wishListData": wishListData},
    )


def addToCart(request):
    uid = request.session["uid"]
    userid = User.objects.get(loginid=uid)
    if request.POST:
        qty = request.POST["qty"]
        pid = request.POST["pid"]
        price = request.POST["price"]
        total = int(price) * int(qty)
        pdtid = Products.objects.get(id=pid)
        addToCart = Cart.objects.create(
            uid=userid, pid=pdtid, quantity=qty, price=total
        )
        addToCart.save()
        stock = pdtid.qty
        finalstock = int(stock) - int(qty)
        updateStock = Products.objects.filter(id=pid).update(qty=finalstock)
        coordinator = pdtid.artistId
        Notification.objects.create(
            artist=coordinator,
            message=f"🛒 {userid.name} has booked your package: {pdtid.name}!",
            notif_type="booking"
        )
        messages.success(request, "Added To Trips")
    return redirect("/viewCart")


def viewCart(request):
    uid = request.session["uid"]
    cartData = Cart.objects.filter(Q(uid__loginid=uid) & Q(status="InCart"))
    if not cartData.exists():
        messages.error(request, "No Booked Trips")
        return redirect("/userViewProduct")
    cartTota = Cart.objects.filter(
        Q(uid_id__loginid__id=uid) & Q(status="InCart")
    ).aggregate(total=Sum("price"))["total"]
    cartTotal=cartTota
    print(cartTotal)
    count = Cart.objects.filter(Q(uid_id__loginid__id=uid) & Q(status="InCart")).count()
    print(count)
    return render(
        request,
        "USER/viewCart.html",
        {"cartData": cartData, "count": count, "cartTotal": cartTotal},
    )


def removeFromCart(request):
    id = request.GET["id"]
    pid = request.GET["pid"]
    qty = request.GET["qty"]

    updatePdt = Products.objects.get(id=pid)
    stock = updatePdt.qty
    uStock = int(stock) + int(qty)
    updatePdt.qty = uStock
    updatePdt.save()
    updateCart = Cart.objects.get(id=id).delete()
    messages.success(request, "Package Removed")
    return redirect("/viewCart")


def paymentForm(request):
    id = request.GET["id"]
    cartData = Cart.objects.get(id=id)
    cartTotal = (cartData.price)/4
    
    if request.POST:
        updateStatus = Cart.objects.filter(id=id).update(status="Paid")
        messages.success(request, "Payment Success")
        coordinator = cartData.pid.artistId
        Notification.objects.create(
            artist=coordinator,
            message=f"💰 {cartData.uid.name} made a partial payment for {cartData.pid.name}!",
            notif_type="payment"
        )
        return redirect("/viewOrders")
    
    return render(request, "USER/paymentForm.html", {"cartTotal": cartTotal})




def paymentForms(request):
    id = request.GET["id"]
    cartData = Cart.objects.get(id=id)
    cartTotal = (cartData.price)*(0.75)
    
    if request.POST:
        cartData.completedpay=1
        cartData.save()
        user = cartData.uid
        Notification.objects.create(
            user=user,
            message=f"✅ Your payment for {cartData.pid.name} is complete!",
            notif_type="payment"
        )
        coordinator = cartData.pid.artistId
        Notification.objects.create(
            artist=coordinator,
            message=f"✅ {cartData.uid.name} completed full payment for {cartData.pid.name}!",
            notif_type="payment"
        )
        return redirect("/viewOrders")
    
        

    return render(request, "USER/paymentForms.html", {"cartTotal": cartTotal})




def checkOut(request):
    uid = request.session["uid"]
    myCart = Cart.objects.filter(Q(uid_id__loginid__id=uid) & Q(status="InCart"))
    id_list = myCart.values_list("id", flat=True)
    cartTotal = Cart.objects.filter(
        Q(uid_id__loginid__id=uid) & Q(status="InCart")
    ).aggregate(total=Sum("price"))["total"]
    print(id_list)
    for i in id_list:
        print(i)
    if request.POST:
        for i in id_list:
            updateStatus = Cart.objects.filter(id=i).update(status="Paid")
        return redirect("/viewOrders")
    return render(request, "USER/paymentForm.html", {"cartTotal": cartTotal})

def viewOrders(request):
    uid = request.session["uid"]
    orderData = Cart.objects.filter(Q(uid_id__loginid__id=uid) & Q(status="Paid")).order_by("-date")
    cancelledData = Cart.objects.filter(Q(uid_id__loginid__id=uid) & Q(status="Cancelled")).order_by("-date")
    fdbkData = Feedback.objects.filter(uid__loginid=uid)
    id_list = fdbkData.values_list("oid__pid", flat=True)
    return render(request, "USER/viewOrders.html", {"orderData": orderData, "id_list": id_list, "cancelledData": cancelledData}
    )

def addToWishList(request):
    id = request.GET["id"]
    uid = request.session["uid"]
    userid = User.objects.get(loginid=uid)
    pdtid = Products.objects.get(id=id)
    addWishList = Wishlist.objects.create(uid=userid, pid=pdtid)
    addWishList.save()
    messages.success(request, "Added to Saved")
    return redirect("/userViewProduct")


def removeFromWishList(request):
    id = request.GET["id"]
    uid = request.session["uid"]
    deleteWish = Wishlist.objects.filter(Q(pid_id=id) & Q(uid__loginid=uid)).delete()
    messages.success(request, "Removed from Saved")
    return redirect("/userViewProduct")

def wishList(request):
    uid = request.session["uid"]
    wishListData = Wishlist.objects.filter(uid__loginid=uid).exclude(pid__status="Cancelled").order_by("-id")
    return render(request, "USER/wishList.html", {"wishListData": wishListData})


def addFeedback(request):
    uid = request.session["uid"]
    userid = User.objects.get(loginid=uid)
    id = request.GET["id"]
    order_id = Cart.objects.get(id=id)
    if request.POST:
        rating = request.POST["rating"]
        review = request.POST["review"]
        addFdbk = Feedback.objects.create(
            uid=userid, oid=order_id, rating=rating, review=review
        )
        addFdbk.save()
        messages.success(request, "Feedback Added")
        return redirect("/viewOrders")
    return render(request, "USER/addFeedback.html")


def addAddress(request):
    id=request.GET.get("id")
    cart=Cart.objects.filter(id = id)
    if id:
        if request.POST:
            name=request.POST['name']
            email=request.POST['email']
            state=request.POST['state']
            pincode=request.POST['pincode']
            address=request.POST['address']
            images = request.FILES["proof"]
            updateAddress=Cart.objects.filter(id=id).update(name=name,email=email,state=state,pincode=pincode,address=address,proof=images)
            return redirect("/paymentForm?id="+id)
    else:
        uid = request.session["uid"]
        myCart = Cart.objects.filter(Q(uid_id__loginid__id=uid) & Q(status="InCart"))
        id_list = myCart.values_list("id", flat=True)
        if request.POST:
            name=request.POST['name']
            email=request.POST['email']
            state=request.POST['state']
            pincode=request.POST['pincode']
            address=request.POST['address']
            for i in id_list:
                updateStatus = Cart.objects.filter(id=i).update(name=name,email=email,state=state,pincode=pincode,address=address)
            return redirect("/checkOut")
    return render(request,"USER/addAddress.html",{"data":cart})

########################################### Chat Section###########################################

def chat(request):
    uid = request.session["uid"]
    # Artists+
    name=""
    artistData = Artist.objects.all()
    id = request.GET.get("id")
    getChatData = Chat.objects.filter(Q(uid__loginid=uid) & Q(artistid=id))
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M")
    try:
        userid = User.objects.get(loginid__id=uid)
    except User.DoesNotExist:
        messages.error(request, "Chat is only available for Users.")
        return redirect("/artistHome")
    if id:
        artistid = Artist.objects.get(id=id)
        name=artistid.name
    if request.POST:
        message = request.POST["message"]
        sendMsg = Chat.objects.create(uid=userid,message=message,artistid=artistid,time=formatted_time,utype="USER")
        sendMsg.save()
    return render(request,"USER/chat.html",{"artistData": artistData, "getChatData": getChatData,"artistid":name})


def reply(request):
    uid = request.session["uid"]
    print(uid)
    name=""
    userData = User.objects.all()
    id = request.GET.get("id")
    getChatData = Chat.objects.filter(Q(artistid__loginid=uid) & Q(uid=id))
    print(getChatData)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M")
    artistid = Artist.objects.get(loginid__id=uid)
    if id:
        userid = User.objects.get(id=id)
        name=userid.name
    if request.POST:
        message = request.POST["message"]
        sendMsg = Chat.objects.create(uid=userid,message=message,artistid=artistid,time=formatted_time,utype="ARTIST")
        sendMsg.save()
    return render(request,"ARTIST/chat.html",{"userData": userData, "getChatData": getChatData,"userid":name})






########################################### GChat Section###########################################

def gchat(request):
    uid = request.session["uid"]
    print("uid",uid)
    id = request.GET.get("id")
    name=""

    cart = Cart.objects.filter(uid__loginid__id = uid,status = "Paid")
    pak = set()
    for c in cart:
        pak.add(c.pid.id)

    try:
        userid = User.objects.get(loginid = uid)
    except User.DoesNotExist:
        messages.error(request, "Group Chat is only available for Users.")
        return redirect("/artistHome")

    getChatData = GChat.objects.filter(Q(packages=id))
    artistData = Products.objects.filter(id__in=pak).exclude(status="Cancelled")
    if request.POST:
        message = request.POST["message"]
        pack = Products.objects.get(id=id)
        sendMsg = GChat.objects.create(uid=userid,message=message,packages=pack,utype="USER",status="accepted")
        sendMsg.save()
        other_members = GChat.objects.filter(
            packages=pack,
            status="accepted"
        ).exclude(uid=userid).values_list('uid', flat=True).distinct()
        for member_id in other_members:
            try:
                member = User.objects.get(id=member_id)
                Notification.objects.create(
                    user=member,
                    message=f"💬 New message in {pack.name} group!",
                    notif_type="chat"
                )
            except:
                pass
    is_member = GChat.objects.filter(uid=userid, packages=id, status="accepted").exists()
    members = GChat.objects.filter(packages=id, status="accepted", utype="USER", message__isnull=True).values('uid__name', 'uid__id', 'id').distinct()
    return render(request,"USER/gchat.html",{"artistData": artistData, "getChatData": getChatData,"artistid":name,"cart":cart, "is_member": is_member, "id": id, "members": members})
    




def greply(request):
    uid = request.session["uid"]
    print(uid)
    name=""
    userData = Products.objects.filter(artistId__loginid = uid)
    id = request.GET.get("id")
    getChatData = GChat.objects.filter(Q(packages=id))
    print(getChatData)
    current_time = datetime.now().time()
    formatted_time = current_time.strftime("%H:%M")
    artistid = Artist.objects.get(loginid=uid)
    if id:
        userid = Products.objects.get(id=id)
        name=userid.name
    if request.POST:
        message = request.POST["message"]
        sendMsg = GChat.objects.create(packages=userid,status="accepted",message=message,artistid=artistid,time=formatted_time,utype="ARTIST")
        sendMsg.save()
    # Get unique members - one record per user
    seen_uids = []
    unique_members = []
    all_member_records = GChat.objects.filter(packages=id, status="accepted", utype="USER")
    for record in all_member_records:
        if record.uid_id not in seen_uids:
            seen_uids.append(record.uid_id)
            unique_members.append({
                'uid__name': record.uid.name,
                'uid__id': record.uid_id,
                'id': record.id
            })
    return render(request,"ARTIST/gchat.html",{"userData": userData, "getChatData": getChatData,"userid":name, "members": unique_members, "package_id": id})




















def cprofile(request):
    
        id = request.GET["cid"]
        myProfile = Artist.objects.get(id=id)
        data = Products.objects.filter(artistId=id)
        print(myProfile)
        return render(request, "USER/viewcprofile.html", {"myProfile": myProfile,"productData":data})


def addtogroup(request):
    uid = request.session["uid"]
    id = request.GET["id"]
    packages = Products.objects.get(id = id)
    if GChat.objects.filter(uid=uid).exists():
            msg = "User is Already Exists or User is already in the Group"
            return redirect("/viewOrders")
    else:
        var = GChat.objects.create(uid = User.objects.get(loginid = uid),artistid = Artist.objects.get(id = packages.artistId.id),status="requested",utype= "USER",packages=packages)
        var.save()

    return redirect("/viewOrders")


def joingroup(request):
    rid=request.GET["id"]
    req = GChat.objects.get(id=rid)
    req.status = "accepted"
    req.save()
    Notification.objects.create(
        user=req.uid,
        message=f"🎉 You have been accepted into the group for {req.packages.name}!",
        notif_type="group_join"
    )
    return redirect("/profile")

def dontjoingroup(request):
    rid=request.GET["id"]
    req = GChat.objects.get(id=rid)
    req.delete()
    return redirect("/profile")


   ###################new updations

def adminViewUser(request):
    data = User.objects.all()  # Fetch all users
    return render(request, 'ADMIN/adminViewUser.html', {"data": data})

def manageUser(request):
    id = request.GET.get('id')
    status = request.GET.get('status')

    if status == "Delete":
        Login.objects.filter(id=id).delete()

    messages.success(request, "User Deleted Successfully")
    return redirect('/adminViewUser/') 

########################################### Notifications ###########################################

def notifications(request):
    uid = request.session["uid"]
    try:
        user = User.objects.get(loginid=uid)
        notifs = Notification.objects.filter(user=user).order_by('-created_at')
        unread_count = notifs.filter(is_read=False).count()
        # Mark as read AFTER counting
        Notification.objects.filter(user=user, is_read=False).update(is_read=True)
    except User.DoesNotExist:
        notifs = []
        unread_count = 0
    return render(request, "USER/notifications.html", {"notifs": notifs, "unread_count": unread_count})


def clearNotifications(request):
    uid = request.session["uid"]
    try:
        user = User.objects.get(loginid=uid)
        Notification.objects.filter(user=user).delete()
    except:
        pass
    return redirect("/notifications/")


def artistNotifications(request):
    uid = request.session["uid"]
    try:
        artist = Artist.objects.get(loginid=uid)
        notifs = Notification.objects.filter(artist=artist).order_by('-created_at')
        unread_count = notifs.filter(is_read=False).count()
        Notification.objects.filter(artist=artist, is_read=False).update(is_read=True)
    except:
        notifs = []
        unread_count = 0
    return render(request, "ARTIST/artistnotification.html", {"notifs": notifs, "unread_count": unread_count})

def clearArtistNotifications(request):
    uid = request.session["uid"]
    try:
        artist = Artist.objects.get(loginid=uid)
        Notification.objects.filter(artist=artist).delete()
    except:
        pass
    return redirect("/artistNotifications/")

########################################### Admin Reports ###########################################

def adminReports(request):
    # Numbers
    total_users = User.objects.count()
    total_coordinators = Artist.objects.filter(status="Paid").count()
    total_bookings = Cart.objects.filter(status="Paid").count()
    total_revenue = Cart.objects.filter(status="Paid").aggregate(total=Sum("price"))["total"] or 0

    # Most popular trips
    popular_trips = Products.objects.exclude(status="Cancelled").order_by('-uploaded')[:5]

    # All paid bookings (partial payments first, then fully paid, both chronologically ordered)
    all_bookings = Cart.objects.filter(
        status="Paid"
    ).order_by('completedpay', '-date')

  # All feedbacks
    feedbacks = Feedback.objects.all().order_by('-date')[:5]

    # Cancelled bookings
    cancelled_bookings = Cart.objects.filter(status="Cancelled").order_by('-date')

    # Cancelled count for stats card
    total_cancelled = cancelled_bookings.count()

    return render(request, "ADMIN/adminReports.html", {
        "total_users": total_users,
        "total_coordinators": total_coordinators,
        "total_bookings": total_bookings,
        "total_revenue": total_revenue,
        "popular_trips": popular_trips,
        "all_bookings": all_bookings,
        "feedbacks": feedbacks,
        "cancelled_bookings": cancelled_bookings,
        "total_cancelled": total_cancelled,
    })


########################################### Leave & Remove Group ###########################################

def leaveGroup(request):
    uid = request.session["uid"]
    id = request.GET.get("id")  # package id
    try:
        user = User.objects.get(loginid=uid)
        GChat.objects.filter(uid=user, packages=id).delete()
        messages.success(request, "You have left the group.")
    except:
        messages.error(request, "Something went wrong.")
    return redirect("/gchat")


def removeFromGroup(request):
    uid = request.session["uid"]
    user_id = request.GET.get("user_id")
    package_id = request.GET.get("package_id")
    try:
        user_to_remove = User.objects.get(id=user_id)
        GChat.objects.filter(uid=user_to_remove, packages=package_id).delete()
        Notification.objects.create(
            user=user_to_remove,
            message=f"⚠️ You have been removed from the group by the coordinator.",
            notif_type="group_remove"
        )
        messages.success(request, f"{user_to_remove.name} removed from group.")
    except Exception as e:
        messages.error(request, f"Could not remove user: {str(e)}")
    return redirect(f"/greply?id={package_id}")

########################################### Cancel Booking ###########################################

def cancelBooking(request):
    uid = request.session["uid"]
    id = request.GET.get("id")
    
    # Show the cancellation reason form page (GET request)
    if request.method == "GET" and not request.POST:
        try:
            cart = Cart.objects.get(id=id, uid__loginid=uid)
            return render(request, "USER/cancelBooking.html", {"cart": cart})
        except Exception as e:
            messages.error(request, f"Booking not found: {str(e)}")
            return redirect("/viewOrders/")
    
    # Process the cancellation (POST request - form submitted)
    if request.method == "POST":
        id = request.POST.get("id")
        reason = request.POST.get("reason", "No reason provided")
        try:
            cart = Cart.objects.get(id=id, uid__loginid=uid)

            # Restore stock
            product = cart.pid
            product.qty += cart.quantity
            product.save()

            # Determine refund type BEFORE changing status
            if cart.completedpay == 1:
                refund_msg = "Full Refund — your full payment will be refunded within 5-7 business days."
                coord_msg = f"❌ {cart.uid.name} cancelled their booking for {cart.pid.name}. Reason: {reason}. Full refund required."
            elif cart.status == "Paid":
                refund_msg = "Partial Refund — your partial payment will be refunded within 5-7 business days."
                coord_msg = f"❌ {cart.uid.name} cancelled their booking for {cart.pid.name}. Reason: {reason}. Partial refund required."
            else:
                refund_msg = "No payment was made — no refund needed."
                coord_msg = f"❌ {cart.uid.name} cancelled their booking for {cart.pid.name}. Reason: {reason}. No refund needed."

            # Update cart with cancellation info
            cart.status = "Cancelled"
            cart.cancellation_reason = reason
            cart.cancelled_by = "User"
            cart.save()

            # Notify user
            Notification.objects.create(
                user=cart.uid,
                message=f"❌ Your booking for {cart.pid.name} has been cancelled. {refund_msg}",
                notif_type="cancellation"
            )

            # Notify coordinator
            coordinator = cart.pid.artistId
            Notification.objects.create(
                artist=coordinator,
                message=coord_msg,
                notif_type="cancellation"
            )

            messages.success(request, f"Booking cancelled! {refund_msg}")
        except Exception as e:
            messages.error(request, f"Could not cancel booking: {str(e)}")
        return redirect("/viewOrders/")
    

 