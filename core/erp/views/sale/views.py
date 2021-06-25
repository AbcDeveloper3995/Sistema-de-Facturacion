import json
import os

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.loader import get_template
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import CreateView, ListView, UpdateView, DeleteView
from django.views.generic.base import View
from xhtml2pdf import pisa

from config import settings
from core.erp.forms import saleForm
from core.erp.mixins import ValidatePermissionRequiredMixin
from core.erp.models import Sale, Product, DetSale

class DetSaleListView(LoginRequiredMixin, ValidatePermissionRequiredMixin, ListView):
    model = DetSale
    template_name = 'sale/list.html'
    permission_required = 'erp.view_client'

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'searchdata':
                data = []
                for i in Sale.objects.all():
                    data.append(i.toJSON())
            elif action == 'search_details_pro':
                data = []
                print(request.POST)
                for i in DetSale.objects.filter(sale_id=request.POST['id']):
                    data.append(i.toJSON())
            else:
                data['error'] = 'Ha ocurrido un error'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Listado de Ventas'
        context['create_url'] = reverse_lazy('erp:sale_create')
        context['list_url'] = reverse_lazy('erp:sale_list')
        context['entity'] = 'Ventas'
        return context

class saleCreateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, CreateView):
    model = Sale
    form_class = saleForm
    template_name = 'sale/create.html'
    success_url = reverse_lazy('erp:client_list')
    permission_required = 'erp.add_client'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data =[]
                prods = Product.objects.filter(name__icontains=request.POST['term'])
                if prods:
                    for i in prods:
                        item =i.toJSON()
                        item['text'] = i.name
                        data.append(item)
                else:
                    sms = 'No se encontraron productos con esa descripcion'
                    data.append(sms)
            elif action =='add':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    sale = Sale(
                        date_joined=vents['date_joined'],
                        cli_id=int(vents['cli']),
                        subtotal=float(vents['subtotal']),
                        iva=float(vents['iva']),
                        total=float(vents['total']),
                    )
                    sale.save()
                    for i in vents['products']:
                        det = DetSale(
                            sale_id=sale.id,
                            prod_id=i['id'],
                            cant=int(i['cant']),
                            price=float(i['pvp']),
                            subtotal=float(i['subtotal'])
                        )
                        det.save()
            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Creación de una venta'
        context['entity'] = 'Clientes'
        context['list_url'] = self.success_url
        context['action'] = 'add'
        context['det'] = []
        return context


class saleUpdateView(LoginRequiredMixin, ValidatePermissionRequiredMixin, UpdateView):
    model = Sale
    form_class = saleForm
    template_name = 'sale/create.html'
    success_url = reverse_lazy('erp:client_list')
    permission_required = 'erp.change_client'
    url_redirect = success_url

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            action = request.POST['action']
            if action == 'search_products':
                data =[]
                prods = Product.objects.filter(name__icontains=request.POST['term'])
                if prods:
                    for i in prods:
                        item =i.toJSON()
                        item['value'] = i.name
                        data.append(item)
                else:
                    sms = 'No se encontraron productos con esa descripcion'
                    data.append(sms)
            elif action =='edit':
                with transaction.atomic():
                    vents = json.loads(request.POST['vents'])
                    sale = self.get_object()
                    sale.date_joined = vents['date_joined']
                    sale.cli_id = vents['cli']
                    sale.subtotal = float(vents['subtotal'])
                    sale.iva = float(vents['iva'])
                    sale.total = float(vents['total'])
                    sale.save()
                    sale.detsale_set.all().delete()
                    for i in vents['products']:
                        det = DetSale(
                            sale_id=sale.id,
                            prod_id=i['id'],
                            cant=int(i['cant']),
                            price=float(i['pvp']),
                            subtotal=float(i['subtotal'])
                        )
                        det.save()

            else:
                data['error'] = 'No ha ingresado a ninguna opción'
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data, safe=False)

    def getDetailsProducts(self):
        data = []
        try:
            for i in DetSale.objects.filter(sale_id=self.get_object().id):
                item = i.prod.toJSON()
                item['cant'] = i.cant
                data.append(item)
        except:
            pass
        return data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edicion de una venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        context['action'] = 'edit'
        context['det'] = json.dumps(self.getDetailsProducts())
        return context

class saleDeleteView(LoginRequiredMixin, ValidatePermissionRequiredMixin, DeleteView):
    model = Sale
    template_name = 'sale/delete.html'
    success_url = reverse_lazy('erp:sale_list')
    permission_required = 'erp.delete_sale'
    url_redirect = success_url

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        data = {}
        try:
            self.object.delete()
        except Exception as e:
            data['error'] = str(e)
        return JsonResponse(data)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Eliminación de una Venta'
        context['entity'] = 'Ventas'
        context['list_url'] = self.success_url
        return context

class saleInvoicePDF(View):

    def link_callback(self, uri, rel):

        sUrl = settings.STATIC_URL
        sRoot = settings.STATIC_ROOT
        mUrl = settings.MEDIA_URL
        mRoot = settings.MEDIA_ROOT

        if uri.startswith(mUrl):
            path = os.path.join(mRoot, uri.replace(mUrl, ""))
        elif uri.startswith(sUrl):
            path = os.path.join(sRoot, uri.replace(sUrl, ""))
        else:
            return uri

        if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
        return path


    def get(self, request, *args, **kwargs):
        try:
            template = get_template('sale/invoice.html')
            context = {
                'sale':Sale.objects.get(pk=self.kwargs['pk']),
                'comp':{'name':'Algorisoft','ruc':'999','address':'Cuba'},
                'icon':'{}{}'.format(settings.MEDIA_URL,'logo.png')
            }
            html = template.render(context)
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = 'attachment; filename="reporte.pdf"'
            pisaStatus = pisa.CreatePDF(html, dest=response, link_callback=self.link_callback)
            return response
        except:
            return HttpResponseRedirect(reverse_lazy('erp:sale_list'))





