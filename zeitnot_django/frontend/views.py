from django.shortcuts import render
from django.views import View
from django.http import HttpResponse
from django.contrib.staticfiles.views import serve

# Create your views here.
class Index(View):
    def get(self, request):
        context = {
        }
        resp = render(request,"index.html", context=context)
        

        return resp
    
class StockfishJS(View):
    def get(self, request):
        with open("frontend/static/js/stockfish/stockfish-nnue-16.js") as f:
            response = HttpResponse(f.read())

            response["Cross-Origin-Opener-Policy"] = "same-origin"
            response["Cross-Origin-Embedder-Policy"] = "require-corp"
            response["Cross-Origin-Resource-Policy"] = "same-site"
            response["Content-Type"] = "application/x-javascript"

            return response
        
class StockfishWasm(View):
    def get(self, request):
        with open("frontend/static/js/stockfish/stockfish-nnue-16.wasm", "rb") as f:
            response = HttpResponse(f.read())

            response["Cross-Origin-Opener-Policy"] = "same-origin"
            response["Cross-Origin-Embedder-Policy"] = "require-corp"
            response["Cross-Origin-Resource-Policy"] = "same-site"
            response["Content-Type"] = "application/wasm"

            return response