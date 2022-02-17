from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("watchlist/", views.watchlist, name="watchlist"),
    path("watchlist/<int:id>/edit/", views.watched_listing_item, name="watched_listing_item"),
    path("listing/<int:id>/", views.single_listing, name="single_listing"),
    path("listing/<int:id>/bid/", views.listing_bid, name="listing_bid"),
    path("listing/<int:id>/comment/", views.listing_comment, name="listing_comment"),
    path("listing/create/", views.create_listing, name='create_listing'),
    path("listing/<int:id>/close/", views.close_listing, name="close_listing"),
    path("listing/closed/", views.finished_listings, name="finished_listings"),
    path("categories/", views.categories_page, name="categories"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("register/", views.register, name="register")
]
