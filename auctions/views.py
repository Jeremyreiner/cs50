from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from datetime import datetime, timedelta
from django.utils import timezone
from django.urls import reverse

from .models import User, Listing, Bid, Comment, Category
from .forms import BidForm, CommentForm, ListingForm

def index(request):
    active_listings = Listing.objects.filter(
        close_listing=False, end_time__gte=datetime.now()).order_by("-start_time")
    
    context = {
        "listings": active_listings, 
        "title" : "Active Listings"
    }

    return render(request, "auctions/index.html", context)


def close_listing(request, id):
    listing = Listing.objects.get(id=id)
    if request.user == listing.user:
        listing.close_listing = True
        listing.end_time = timezone.now()
        listing.save()
    return HttpResponseRedirect(reverse('single_listing',kwargs={'id': id,}))


def finished_listings(request):
    listings = Listing.objects.filter(close_listing=True).order_by("end_time")

    if listings:
        context = {
            'listings': listings,
            'ended': True,
            "title": "Closed Listings"
        }
        return render(request, "auctions/closed_listings.html", context)
    else:
        context = {
            'listings': listings,
            'ended': False,
            "title": "Closed Listings"
        }
        return render(request, "auctions/closed_listings.html", context) 


def watchlist(request):
    context = {
        "listings" : request.user.watchlist.filter(close_listing=False),
        "title" : "Watchlist"
    }
    return render(request, "auctions/index.html", context)
    


def watched_listing_item(request, id):
    if request.method == "POST":
        user = request.user
        listing = Listing.objects.get(id=id)
        watchlist = request.user.watchlist

        if listing in watchlist.all():
            watchlist.remove(listing)
        else:
            watchlist.add(listing)

    return HttpResponseRedirect(reverse('single_listing',kwargs={'id': id,}))


def single_listing(request, id):
    # check that auction exists
    try:
        listing = Listing.objects.get(id=id)
        time_remaining = listing.end_time - timezone.now()
    except:
        return HttpResponse("This listed item does not exist.")

    if listing.is_finshed():
        listing.end_time = datetime.now()
        listing.save()

        context = {
            'listing': listing,
            'time_remaining': time_remaining,
            'ended': True,

        }
        return render(request, "auctions/single_listing.html", context)

    context = {
        'listing': listing,
        'days': time_remaining.days,
        'hours': int(time_remaining.seconds / 3600),
        'bid_form':BidForm(),
        'comment_form': CommentForm(),
    }
    context["minutes"] = int(time_remaining.seconds / 60 - (context["hours"] * 60))

    return render(request, "auctions/single_listing.html", context)


def listing_bid(request, id):
    listing = Listing.objects.get(id=id)
    current_bids = Bid.objects.filter(listing=listing)
    user = request.user
    watchlist = request.user.watchlist

    if request.method == "POST":
        bid_form = BidForm(request.POST)

        if bid_form.is_valid():
            new_bid = bid_form.save(commit=False)
            highest_bid = all(new_bid.amount > bid.amount for bid in current_bids)
            valid_first_bid = new_bid.amount >= listing.start_bid

            if highest_bid and valid_first_bid:
                new_bid.listing = listing
                new_bid.user = user
                new_bid.save()
                watchlist.add(listing)
            else:
                messages.error(request, 'Invalid bid. New Bids must be higher than Current Bid.')
                return HttpResponseRedirect(reverse('single_listing',kwargs={'id': id,}))

        return HttpResponseRedirect(reverse('single_listing', kwargs={'id': id}))
    
    else:
        context = {
            'bid_form': BidForm(),
            'listing': listing,
        }
        return render(request, "auctions/single_listing.html", context)

def listing_comment(request, id):
    comment_form = CommentForm(request.POST)
    user = request.user

    if comment_form.is_valid():
        new_comment = comment_form.save(commit=False)
        new_comment.listing = Listing.objects.get(id=id)
        new_comment.user = user
        new_comment.save()

    return HttpResponseRedirect(reverse('single_listing', kwargs={'id': id}))

def categories_page(request):      
    category = request.GET.get('category')

    if category == None:
        active_listings = None

    else:
        active_listings = Listing.objects.filter(close_listing=False, category__title=category).order_by("-start_time")

    categories = Category.objects.all()

    context = {
        'categories': categories,
        'listings': active_listings,
        "title" : "Categories"
    }
    return render(request, "auctions/categories.html", context)


def create_listing(request):
    form = ListingForm(request.POST, request.FILES)

    if form.is_valid():
        new_listing = form.save(commit=False)
        time_remaining = new_listing.end_time - timezone.now()

        if time_remaining <= timedelta(minutes=0):
            messages.error(request, 'Invalid date. The date must be after the current date/ time.')
            return HttpResponseRedirect(reverse('create_listing'))
        
        new_listing.user = request.user
        new_listing.save()

        return HttpResponseRedirect(reverse('single_listing', kwargs={'id': new_listing.id}))

    else:
        context = {
            'form': form
        }
        return render(request, "auctions/create_listing.html", context)



#----------------LOG IN REQUIREMENTS-----------------
def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
#----------------LOG IN REQUIREMENTS-------------------