from django.shortcuts import render
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import redirect

def index(request):
  context = RequestContext(request)
  return render_to_response('main/index.html', context)
