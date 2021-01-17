import cherrypy
import os.path
from jinja2 import Environment, PackageLoader, select_autoescape
import requests;
import os;

from client import *


#Lista com todas as informações de todos os clientes
clientDatabase = []
#lista com todas as informações de todos os produtos
productsDatabase = []

shopsDatabase = []
fillShops(shopsDatabase)


fillDataBase(productsDatabase)

# The absolute path to this file's base directory:
baseDir = os.path.dirname(os.path.abspath(__file__))

#Dicionário com a configuração da aplicação
conf = {
  'global': {'tools.sessions.on': True,
            'server.socket_host': '0.0.0.0',
            'server.socket_port': int(os.environ.get('PORT', 5000)), },
  "/":     {'tools.sessions.on': True, 
            "tools.staticdir.root": baseDir },
  "/js":   { "tools.staticdir.on": True,
             "tools.staticdir.dir": "js" },
  "/css":  { "tools.staticdir.on": True,
             "tools.staticdir.dir": "css" },
  "/html": { "tools.staticdir.on": True,
             "tools.staticdir.dir": "html" },
  "/images":{ "tools.staticdir.on": True,
             "tools.staticdir.dir": "images" },
  "/fonts":{ "tools.staticdir.on": True,
             "tools.staticdir.dir": "fonts" },
}

apiDomain = 'https://dry-meadow-84562.herokuapp.com/api'

class HelloWorld(object):
    def __init__(self):
      self.env = Environment(
          loader=PackageLoader('app', 'html'),
          autoescape=select_autoescape(['html', 'xml'])
      )
    
    def render(self, tpg, tps):
      template = self.env.get_template(tpg)
      return template.render(tps)
    
    @cherrypy.expose
    def index(self):
      cherrypy.session['auth'] = False
      tparams = {
        'errors': False
      }
      return self.render('login.html', tparams)
    
    @cherrypy.expose
    def login(self):
      cherrypy.session['auth'] = True
      cherrypy.session['role'] = 'vendor'
      cherrypy.session['productsCar'] = []
      raise cherrypy.HTTPRedirect("/product")

    @cherrypy.expose
    def doLogin(self, email, password):

      authReq = requests.post(apiDomain+'/auth/login', json={'email':email, 'password':password})
      data = authReq.json()

      cherrypy.session['auth'] = True
      cherrypy.session['token'] = data['authToken']
      cherrypy.session['role'] = data['user']['role']
      cherrypy.session['productsCar'] = []
      raise cherrypy.HTTPRedirect("/product")

    @cherrypy.expose
    def logout(self):
      cherrypy.session['auth'] = False
      cherrypy.session['productsCar'].clear()
      raise cherrypy.HTTPRedirect("/index")

    @cherrypy.expose
    def doRegister(self, name, email, password, isVendor='no'):

      role = 'user'
      if isVendor and isVendor == 'on':
        role = 'vendor'
      authReq = requests.post(apiDomain+'/auth/signup', json={'name': name, 'email':email, 'password':password, 'role':role})
      data = authReq.json()

      raise cherrypy.HTTPRedirect("/product")

    @cherrypy.expose
    def main(self):
      tparams = {
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('index.html', tparams)
    
    @cherrypy.expose
    def product(self):
      if 'auth' not in cherrypy.session:
       cherrypy.session['auth'] = False
    
      res = requests.get('https://dry-meadow-84562.herokuapp.com/api/product/suggestions')
      #print(res.json()['parts']) # arrray de produtos

      tparams = {
        'products': res.json()['parts'],
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('product.html', tparams)
    
    @cherrypy.expose
    def search(self, query):
      if 'auth' not in cherrypy.session:
       cherrypy.session['auth'] = False
       

      res = requests.post('https://dry-meadow-84562.herokuapp.com/api/product/search', json={'query':query})

      print(res.json())

      tparams = {
        'products': res.json()['results'],
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('product.html', tparams)
      
    @cherrypy.expose
    def services(self):
      tparams = {
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('services.html', tparams)
    
    @cherrypy.expose
    def about(self):
      tparams = {
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('about.html', tparams)
    
    @cherrypy.expose
    def contact(self):
      tparams = {
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('contact.html', tparams)
    
    @cherrypy.expose
    def register(self):
      cherrypy.session['auth'] = False
      tparams = {
        'errors': False
      }
      return self.render('register.html', tparams)
    
    @cherrypy.expose
    def oficina(self, fname=None, lname=None, email=None, subject=None, message=None):
      errors = False
      if fname == "" or lname == "" or email == "" or subject == "" or message == "":
        errors = True

      tparams = {
        'errors': errors,
        'shops': shopsDatabase,
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('oficina.html', tparams)
  
    @cherrypy.expose
    def testlogin(self, email=None, password=None):
      for client in clientDatabase:
        if client.email == email and client.password == password:
          cherrypy.session['auth'] = True
          cherrypy.session['user'] = {'username': client.username, 'email': client.email, 'role': "client"}
          raise cherrypy.HTTPRedirect("/main")

      tparams = {
        'errors': True
      }
      return self.render('login.html', tparams)

    @cherrypy.expose
    def testregister(self, name=None, password=None, email=None,  address=None):
      c = Client(name, address, email, password)
      
      if c in clientDatabase:
        tparams = {
          'errors': True
        }
        return self.render('register.html', tparams)
      else:
        cherrypy.session['auth'] = True
        cherrypy.session['productsCar'] = []
        cherrypy.session['user'] = {'username': name, 'email': email, 'role': "client"}
        clientDatabase.append(c)
        raise cherrypy.HTTPRedirect("/main")

    @cherrypy.expose
    def payment(self):
      return open('html/payment.html', 'r')

    
    @cherrypy.expose
    def single(self, pid):
      if 'auth' not in cherrypy.session:
       cherrypy.session['auth'] = False
      
      pReq = requests.post(apiDomain+'/product/part', json={'id':pid})
      p = pReq.json()['part']

      cReq = requests.post(apiDomain+'/product/comments', json={'id':pid})
      c = cReq.json()['comments']
      
      tparams = {
        'pid':pid,
        'productname': p['name'],
        'price': p['price'],
        'productinfo': p['description'],
        'country': p['country'],
        'marca': p['brand'],
        'modelo': p['model'],
        #'peso': p['weight'],
        'unidades':int(p['quantity']),
        'cond': p['condition'],
        'imgsrc': p['imgUrl'],
        #'comments': c,
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      
      return self.render('single.html', tparams)


    @cherrypy.expose
    def singleShop(self, sn=None):
      if not cherrypy.session['auth']:
        raise cherrypy.HTTPRedirect("/oficina")
      for p in shopsDatabase:
        if sn == p.name:
          tparams = {
            'name': p.name,
            'open': p.open,
            'close': p.close,
            'location': p.location,
            'days': p.days,
            'email': p.email,
            'imgsrc': p.img,
            'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
            'auth': True if cherrypy.session['auth'] else False,
            'login': "Log Out" if cherrypy.session['auth'] else "Log In"
          }
          return self.render('singleShop.html', tparams)
      return None




    @cherrypy.expose
    def subNotification(self, pid):
      if 'auth' not in cherrypy.session:
       cherrypy.session['auth'] = False
      
      #redirects to login page
      if not cherrypy.session['auth']:
        raise cherrypy.HTTPRedirect('/')
      
      #needs auth
      #sReq= requests.put(apiDomain+'/subscription', json={'partId':pid}, headers={"Authorization":cherrypy.session['token']})
      
      raise cherrypy.HTTPRedirect('/single?pid='+pid)   

    @cherrypy.expose
    def additem(self, pid=None):
      if not cherrypy.session['auth']:
        raise cherrypy.HTTPRedirect("/product")

      cherrypy.session['productsCar'].append(pid)
      raise cherrypy.HTTPRedirect("/product")

    @cherrypy.expose
    def cart(self):
      if not cherrypy.session['auth']:
        raise cherrypy.HTTPRedirect("/main")

      total = 0
      product = []
      for pid in cherrypy.session['productsCar']:
        res = requests.post('https://dry-meadow-84562.herokuapp.com/api/product/part', json=({'id':pid}))
        p = res.json()['part']
        print(p)
        total+=int(p['price'])
        product.append(p)
      tparams = {
        'carproducts': product,
        'total': total,
        'num': len(cherrypy.session['productsCar']),
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('cart.html', tparams)

    @cherrypy.expose
    def empty(self):
      cherrypy.session['productsCar'].clear()
      raise cherrypy.HTTPRedirect("/cart")
    
    @cherrypy.expose
    def payment_done(self, firstname=None, email=None, address=None, city=None, state=None, zip=None, cardname=None, cardnumber=None, expmonth=None, expyear=None, cvv=None, sameadr=None):
      cherrypy.session['productsCar'].clear()
      tparams = {
        'num': len(cherrypy.session['productsCar']),
        'login': "Log Out" if cherrypy.session['auth'] else "Log In",
        'auth': True if cherrypy.session['auth'] else False
      }
      return self.render('done.html', tparams)
    
    @cherrypy.expose
    def user(self):
      if not cherrypy.session['auth']:
        raise cherrypy.HTTPRedirect("/main")
      
      for c in clientDatabase:
        if c.username == cherrypy.session['user']['username']:      
          tparams = {
            'num': len(cherrypy.session['productsCar']),
            'login': "Log Out" if cherrypy.session['auth'] else "Log In",
            'auth': True if cherrypy.session['auth'] else False,
            'username': c.username,
            'email': c.email,
            'address': c.address
          }
          return self.render('user.html', tparams)
    
    @cherrypy.expose
    def vendor(self):
      if 'auth' not in cherrypy.session or not cherrypy.session['auth']:
        raise cherrypy.HTTPRedirect("/main")

      if cherrypy.session['role'] != 'vendor':
        raise cherrypy.HTTPRedirect("/main")
      
      partsReq= requests.get(apiDomain+'/product/vendorProducts',headers={"Authorization":cherrypy.session['token']})
      ps = partsReq.json()['parts']

      return self.render('vendor.html', {'products':ps})

    @cherrypy.expose
    def edit(self, pid):
      pReq = requests.post(apiDomain+'/product/part', json={'id':pid})
      p = pReq.json()['part']
      
      tparams = {
        'pid':pid,
        'productname': p['name'],
        'price': p['price'],
        'description': p['description'],
        'country': p['country'],
        'marca': p['brand'],
        'modelo': p['model'],
        #'peso': p['weight'],
        'unidades':int(p['quantity']),
        'cond': p['condition'],
        'imgsrc': p['imgUrl'],
        'makerId': p['makerId'],
        'ean': p['ean'],
        'num': len(cherrypy.session['productsCar']) if cherrypy.session['auth'] else 0,
        'auth': True if cherrypy.session['auth'] else False,
        'login': "Log Out" if cherrypy.session['auth'] else "Log In"
      }
      return self.render('edit.html', tparams)

    @cherrypy.expose
    def addVendorPart(self, name, description, country, brand, model, condition, price, quantity, makerId, ean):
      newPart = {
        'name':name,
        'description':description,
        'country':country,
        'brand':brand,
        'model':model,
        'condition':condition,
        'price':price,
        'quantity':quantity,
        'makerId':makerId,
        'ean':ean
      }

      addReq= requests.post(apiDomain+'/product/vendorProducts',headers={"Authorization":cherrypy.session['token']}, json=newPart ) 
      raise cherrypy.HTTPRedirect("/vendor")
    
    @cherrypy.expose
    def updateVendorPart(self, pid, name, description, country, brand, model, condition, price, quantity, makerId, ean): 
      part = {
        'id':int (pid),
        'name':name,
        'description':description,
        'country':country,
        'brand':brand,
        'model':model,
        'condition':condition,
        'price':price,
        'quantity':quantity,
        'makerId':makerId,
        'ean':ean
      }
      updateReq= requests.put(apiDomain+'/product/vendorProducts',headers={"Authorization":cherrypy.session['token']}, json=part )
      raise cherrypy.HTTPRedirect("/vendor")
    
    @cherrypy.expose
    def delVendorPart(self, pid):
      delReq= requests.post(apiDomain+'/product/deleteVendorProducts', json={'id':pid}, headers={"Authorization":cherrypy.session['token']}) 
      raise cherrypy.HTTPRedirect("/vendor")

if __name__ == '__main__':
    cherrypy.config.update({'server.socket_host': '127.0.0.1'})
    cherrypy.quickstart(HelloWorld(), "/", conf)