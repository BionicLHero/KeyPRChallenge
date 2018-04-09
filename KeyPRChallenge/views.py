from django.shortcuts import render
import requests

def index(request):
    return NotImplementedError
    # response = requests.get('http://freegeoip.net/json/')
    # responsejson = response.json()
    # return render(request, 'core/home.html', {
    #     'ip': responsejson['ip'],
    #     'country': responsejson['country_name']
    # })
