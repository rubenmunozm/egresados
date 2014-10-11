# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL('sqlite://storage.sqlite',pool_size=1,check_reserved=['all'])
else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'
#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - old style crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import Auth, Crud, Service, PluginManager, prettydate
auth = Auth(db)
crud, service, plugins = Crud(db), Service(), PluginManager()

auth.settings.extra_fields['auth_user']= [
    Field("correo_trabajo", "string", length=50),
    Field("correo_personal", "string", length=50),
    Field("fecha_nac", "date"),
    Field("telefono", "string", length=20,requires = IS_UPPER()),
    Field("celular", "string", length=20,requires = IS_UPPER()),
    Field("direccion", "string",length=50,requires = IS_UPPER()),
    Field("ciudad", "string",length=30,requires = IS_UPPER()),
    Field("estado", "string", length=30,requires = IS_UPPER()),
    Field("pais", "string", length=30,requires = IS_UPPER())]

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)

## configure email
mail = auth.settings.mailer
mail.settings.server = 'smtp.gmail.com:587'
mail.settings.sender = 'uvmhmoing@gmail.com'
mail.settings.login = 'uvmhmoing@gmail.com:egresados'

## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True
auth.settings.actions_disabled.append('register')


## if you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, write your domain:api_key in private/janrain.key
from gluon.contrib.login_methods.rpx_account import use_janrain
use_janrain(auth, filename='private/janrain.key')

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)

from plugin_jqueryui import DropdownDateWidget, Select2MultiselectWidget, UISliderWidget, Select2Widget,StarRatingWidget
widget_searchmultiselect = Select2MultiselectWidget(maximumSelectionSize=2) 
widget_stars = StarRatingWidget()
widget_searchselect = Select2Widget()
widget_slider = UISliderWidget(min=0, max=100, step=1,
                            orientation='horizontal')

db.auth_user._format = '%(first_name)s'+' '+'%(last_name)s'

db.define_table('carreras',
    Field('nombre_carrera', 'string', notnull=True),
    format='%(nombre_carrera)s')

if db(db.carreras).isempty():
    db.carreras.insert(nombre_carrera='INGENIERIA MECATRONICA')
    db.carreras.insert(nombre_carrera='INGENIERIA INDUSTRIAL')
    db.carreras.insert(nombre_carrera='INGENIERIA EN SISTEMAS COMPUTACIONALES')
    db.carreras.insert(nombre_carrera='LIC. EN INFORMÁTICA ADMINISTRATIVA')
    db.carreras.insert(nombre_carrera='INGENIERÍA EN NEGOCIOS Y TECNOLOGÍAS DE MANUFACTURA')


db.define_table('tiempo_encontrar_empleo',
    Field('tiempos', 'string', notnull=True),
    format='%(tiempos)s')

if db(db.tiempo_encontrar_empleo).isempty():
    db.tiempo_encontrar_empleo.insert(tiempos='AUN NO HE LABORADO EN MI PROFESION')
    db.tiempo_encontrar_empleo.insert(tiempos='YA TRABAJABA AL MOMENTO DE EGRESAR')
    db.tiempo_encontrar_empleo.insert(tiempos='1 MES O MENOS')
    db.tiempo_encontrar_empleo.insert(tiempos='2-3 MESES')
    db.tiempo_encontrar_empleo.insert(tiempos='4-6 MESES')
    db.tiempo_encontrar_empleo.insert(tiempos='6-12 MESES')
    db.tiempo_encontrar_empleo.insert(tiempos='1 AÑO - 1 AÑO Y MEDIO')
    db.tiempo_encontrar_empleo.insert(tiempos='1 AÑO Y MEDIO - 2 AÑOS')
    db.tiempo_encontrar_empleo.insert(tiempos='2-3 AÑOS')
    db.tiempo_encontrar_empleo.insert(tiempos='MAS DE TRES AÑOS')


db.define_table('tipos_titulacion',
    Field('tipos', 'string', notnull=True),
    format='%(tipos)s')

if db(db.tipos_titulacion).isempty():
    db.tipos_titulacion.insert(tipos='-')
    db.tipos_titulacion.insert(tipos='CENEVAL')
    db.tipos_titulacion.insert(tipos='TESIS')
    db.tipos_titulacion.insert(tipos='PROMEDIO')
    db.tipos_titulacion.insert(tipos='CURSOS DE MAESTRIA')
    db.tipos_titulacion.insert(tipos='DIPLOMADO DE TITULACION')
    db.tipos_titulacion.insert(tipos='EXPERIENCIA LABORAL')
    db.tipos_titulacion.insert(tipos='OTRO')


db.define_table('tipos_posgrado',
    Field('tipos', 'string', notnull=True),
    format='%(tipos)s')

if db(db.tipos_posgrado).isempty():
    db.tipos_posgrado.insert(tipos='-')
    db.tipos_posgrado.insert(tipos='ESPECIALIDAD')
    db.tipos_posgrado.insert(tipos='MAESTRIA')
    db.tipos_posgrado.insert(tipos='DOCTORADO')
    db.tipos_posgrado.insert(tipos='OTRO')


db.define_table('banderas',
    Field('usuario', db.auth_user),
    Field('primera_completa', 'boolean', default=False))

db.define_table("egresos", 
    Field("usuario", db.auth_user, unique=True), 
    Field("tiempo_encontrar_empleo", "reference tiempo_encontrar_empleo",widget = widget_searchselect.widget),
    Field("carrera", 'reference carreras',widget = widget_searchselect.widget),
    Field("fecha_egreso", "string",widget = widget_searchselect.widget, requires=IS_IN_SET(['1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015'])),
    Field("titulacion", "string",default='NO',widget = SQLFORM.widgets.radio.widget, requires=IS_IN_SET(['SI','NO'],)),
    Field("fecha_titulacion", "string",default='-',widget = widget_searchselect.widget, requires=IS_IN_SET(['-','1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015'])),
    Field("tipo_titulacion", "reference tipos_titulacion", widget = widget_searchselect.widget),
    Field("posgrado", "string",default='NO',widget = SQLFORM.widgets.radio.widget, requires=IS_IN_SET(['SI','NO'])),
    Field("posgrado_tipo", "reference tipos_posgrado", default='-', widget = widget_searchselect.widget),
    Field("posgrado_institucion", "string", length=50,requires = IS_UPPER()),
    Field("posgrado_areaestudio", "string", length=50,requires = IS_UPPER()),
    Field("posgrado_fechatitulacion", "string",default='-',widget = widget_searchselect.widget, requires=IS_IN_SET(['-','1990','1991','1992','1993','1994','1995','1996','1997','1998','1999','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015'])),
    )

if db(db.tipos_titulacion.tipos=='-').count() == 0:
    db.tipos_titulacion.insert(tipos='-')
    db.egresos.tipo_titulacion.default = db(db.tipos_titulacion.tipos=='-').select(db.tipos_titulacion.id).first().id
else:
    db.egresos.tipo_titulacion.default = db(db.tipos_titulacion.tipos=='-').select(db.tipos_titulacion.id).first().id

if db(db.tipos_posgrado.tipos=='-').count() == 0:
    db.tipos_posgrado.insert(tipos='-')
    db.egresos.posgrado_tipo.default = db(db.tipos_posgrado.tipos=='-').select(db.tipos_posgrado.id).first().id
else:
    db.egresos.posgrado_tipo.default = db(db.tipos_posgrado.tipos=='-').select(db.tipos_posgrado.id).first().id

db.define_table('tipos_empresa',
    Field('tipos', 'string', notnull=True),
    format='%(tipos)s')

if db(db.tipos_empresa).isempty():
    db.tipos_empresa.insert(tipos='-')
    db.tipos_empresa.insert(tipos='PUBLICA')
    db.tipos_empresa.insert(tipos='PRIVADA')
    db.tipos_empresa.insert(tipos='PROPIA')
    db.tipos_empresa.insert(tipos='NO LUCRATIVA - NO GUBERNAMENTAL')
    db.tipos_empresa.insert(tipos='OTRO')


db.define_table('giros_empresa',
    Field('giros', 'string', notnull=True),
    format='%(giros)s')

if db(db.giros_empresa).isempty():
    db.giros_empresa.insert(giros='-')
    db.giros_empresa.insert(giros='INDUSTRIAL')
    db.giros_empresa.insert(giros='INDUSTRIAL EXTRACTIVA')
    db.giros_empresa.insert(giros='INDUSTRIAL MANUFACTURERA')
    db.giros_empresa.insert(giros='INDUSTRIAL AGROPECUARIA')
    db.giros_empresa.insert(giros='COMERCIAL')
    db.giros_empresa.insert(giros='COMERCIAL MAYORISTA')
    db.giros_empresa.insert(giros='COMERCIAL MENUDEO')
    db.giros_empresa.insert(giros='SERVICIOS')
    db.giros_empresa.insert(giros='SERVICIOS PUBLICOS')
    db.giros_empresa.insert(giros='SERVICIOS PRIVADOS')
    db.giros_empresa.insert(giros='SERVICIOS TRANSPORTE')
    db.giros_empresa.insert(giros='SERVICIOS TURISMO')
    db.giros_empresa.insert(giros='SERVICIOS INSTITUCIONES FINANCIERAS')
    db.giros_empresa.insert(giros='SERVICIOS EDUCACION')
    db.giros_empresa.insert(giros='SERVICIOS SALUD')
    db.giros_empresa.insert(giros='SERVICIOS FINANZAS Y SEGUROS')
    db.giros_empresa.insert(giros='SERVICIOS TECNOLOGIAS DE INFORMACION')
    db.giros_empresa.insert(giros='OTRO')   



db.define_table("empleos", 
    Field("usuario", db.auth_user),
    Field('laboralmente_activo',"string",default='NO',widget = SQLFORM.widgets.radio.widget, requires=IS_IN_SET(['SI','NO'],)),
    Field("estado_empleo", "string",widget = widget_searchselect.widget, requires=IS_IN_SET(['ACTUAL','ANTERIOR'])),
    Field("nombre_empresa", "string", length=50,requires = IS_UPPER()),
    Field("tipo_empresa", "reference tipos_empresa",widget = widget_searchselect.widget ),
    Field("giro_empresa", "reference giros_empresa",widget = widget_searchselect.widget ),
    Field("empleo_relacionado","string",default='NO',widget = SQLFORM.widgets.radio.widget, requires=IS_IN_SET(['SI','NO'],)),
    Field("fecha_inicio", "date"),
    Field("fecha_fin", "date"),
    Field("telef_empresa", "string", length=30,requires = IS_UPPER()),
    auth.signature,)

if db(db.tipos_empresa.tipos=='-').count() == 0:
    db.tipos_empresa.insert(tipos='-')
    db.empleos.tipo_empresa.default = db(db.tipos_empresa.tipos=='-').select(db.tipos_empresa.id).first().id
else:
    db.empleos.tipo_empresa.default = db(db.tipos_empresa.tipos=='-').select(db.tipos_empresa.id).first().id

if db(db.giros_empresa.giros=='-').count() == 0:
    db.giros_empresa.insert(giros='-')
    db.empleos.giro_empresa.default = db(db.giros_empresa.giros=='-').select(db.giros_empresa.id).first().id
else:
    db.empleos.giro_empresa.default = db(db.giros_empresa.giros=='-').select(db.giros_empresa.id).first().id

db.define_table("banner",
    Field("imagen", "upload"))

db.define_table('anuncios',
    Field('pagina','integer',unique=True,requires=IS_IN_SET(['1','2','3'])),
    Field('titulo_anuncio','string', notnull=True),
    Field('imagen','upload',notnull=True),
    Field('anuncio','text',notnull=True))


