from django.forms import ModelForm, TextInput
from django import forms
from .models import Listing, Bid, Comment


class DateInput(forms.DateInput):
    input_type = 'date'


class ListingForm(ModelForm):
    class Meta:
        model = Listing
        fields = ['item_name',
                'item_description',
                'image',
                'start_bid',
                'end_time',
                'category'
                ]
        widgets = {
            'end_time': DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control'


class BidForm(ModelForm):
    class Meta:
        model = Bid
        fields = ['amount']

    def __init__(self, *args, **kwargs):
        super(BidForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form-control m-2'


class CommentForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea, label='')

    class Meta:
        model = Comment
        fields = ['message']
        widgets = {'message': forms.TextInput( attrs={'class' : 'form-control'})}

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.visible_fields()[0].field.widget.attrs['class'] = 'form-control w-75 h-75'
