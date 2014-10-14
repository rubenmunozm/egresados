# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
## - call exposes all registered services (none by default)
#########################################################################
from gluon.debug import dbg
import csv
#dbg.set_trace() # stop here!
import datetime
from hashlib import md5
import hmac
import math

@auth.requires_membership('admin')
def grid_user():
    db.auth_user.id.readable = False
    grid = SQLFORM.grid(db.auth_user,headers={'auth_user.fecha_nac':'Fecha de nacimiento'},exportclasses=dict(xml=False, html=False, csv_with_hidden_cols=False, tsv_with_hidden_cols=False,tsv=False, json=False))
    return locals()

@auth.requires_membership('admin')
def grid_egresos():
    db.egresos.id.readable = False
    db.egresos.usuario.represent = lambda id,row: db.auth_user(id).first_name +' '+ db.auth_user(id).last_name 
    grid = SQLFORM.grid(db.egresos,headers={'egresos.fecha_egreso':'Fecha de egreso','egresos.fecha_titulacion':'Fecha de titulación','egresos.titulacion':'Esta titulado:'},exportclasses=dict(xml=False, html=False, csv_with_hidden_cols=False,
                             tsv_with_hidden_cols=False,tsv=False, json=False))
    return locals()

@auth.requires_membership('admin')
def grid_empleos():
    db.empleos.id.readable = False
    grid = SQLFORM.grid(db.empleos,headers={'empleos.laboralmente_activo':'Tiene Empleo:','empleos.empleo_relacionado':'Relación Empleo c/ Estudios','empleos.telef_empresa':'Telefono de Empresa'},exportclasses=dict(xml=False, html=False, csv_with_hidden_cols=False,
                             tsv_with_hidden_cols=False,tsv=False, json=False))
    return locals()

@auth.requires_membership('admin')
def grid_empleos_act():
    db.empleos.id.readable = False
    query = (db.empleos.estado_empleo=='ACTUAL')&(db.empleos.laboralmente_activo=='SI')
    grid = SQLFORM.grid(query,headers={'empleos.laboralmente_activo':'Tiene Empleo:','empleos.empleo_relacionado':'Relación Empleo c/ Estudios','empleos.telef_empresa':'Telefono de Empresa'},exportclasses=dict(xml=False, html=False, csv_with_hidden_cols=False,
                             tsv_with_hidden_cols=False,tsv=False, json=False))
    return locals()

@auth.requires_membership('admin')
def adm_web():
    banner = SQLFORM.grid(db.banner,csv=False)
    anuncios = SQLFORM.grid(db.anuncios,csv=False)
    carreras = SQLFORM.grid(db.carreras,exportclasses=dict(xml=False, html=False, csv_with_hidden_cols=False,
                             tsv_with_hidden_cols=False,tsv=False, json=False))
    return locals()

@auth.requires_membership('admin')
def tabla_reportes():
    # index shows the jqgrid table
    #jqueryui enabled in layout.html by removing the comment which stops it from loading.
    response.title=""
    response.subtitle =""
    response.files.append(URL(a='egresados', r=request,c='static/jquery.jqGrid/js/i18n',f='grid.locale-en.js'))
    response.files.append(URL(a='egresados', r=request,c='static/jquery.jqGrid/js/minified',f='jquery.jqGrid.min.js'))
    response.files.append(URL(a='egresados', r=request,c='static/jquery.jqGrid/css',f='ui.jqgrid.css'))

 
    #include a jquery theme downloaded from http://jqueryui.com/download/all/
    response.files.append(URL(a='egresados', r=request,c='static/css/themes/smoothness',f='jquery-ui.css'))
    response.files.append(URL(a='egresados', r=request,c='static/css/themes/smoothness',f='jquery.ui.theme.css'))
    return locals()

@auth.requires_membership('admin')
def correos():
    if request.vars['semando'] == 'bien':
        response.flash = 'Correos enviados!'
    return locals()

@auth.requires_membership('admin')
def recordatorio():
    for row in db().select(db.auth_user.id,db.auth_user.email,db.auth_user.first_name,db.auth_user.username,distinct=True):
        info_registrada = db(db.banderas.usuario==row.id).select(db.banderas.primera_completa).first()
        if info_registrada: ##hay bandera, true or false,pero hay, osea ya hay info egreso y empleo, si true
            if info_registrada['primera_completa'] == True:
                egre=db(db.egresos.usuario == row.id).select(db.egresos.titulacion,db.egresos.posgrado, db.egresos.posgrado_tipo).first()
                emple=db(db.empleos.usuario == row.id)(db.empleos.estado_empleo=='ACTUAL').select(db.empleos.laboralmente_activo,db.empleos.nombre_empresa,orderby=~db.empleos.created_on).first()
                
                context = dict(first_name=row.first_name,matricula=row.username, titulacion=egre.titulacion, posgrado=egre.posgrado,posgrado_tipo=egre.posgrado_tipo.tipos,laboralmente_activo=emple.laboralmente_activo,nombre_empresa=emple.nombre_empresa)
                message = response.render('mail_recordatorio_actualizar.html', context)
                mail.send(to=row.email,
                        subject='Egresados Ingeniería UVM Hermosillo - Actualiza tus Datos',
                        message=message)
            else:
                context = dict(first_name=row.first_name,matricula=row.username)
                message = response.render('mail.html', context)
                mail.send(to=row.email,
                        subject='Egresados Ingeniería UVM Hermosillo',
                        message=message)

        else:
            context = dict(first_name=row.first_name,matricula=row.username)
            message = response.render('mail.html', context)
            mail.send(to=row.email,
                    subject='Egresados Ingeniería UVM Hermosillo',
                    message=message)
    redirect(URL('default','correos',vars={'semando':'bien'}))
    
    return locals()

@auth.requires_membership('admin')
def cargar_archivo():
    form = FORM(INPUT(_type='file', _name='data'), INPUT(_type='submit'))
    if form.process().accepted:
        reader = csv.reader(  form.vars.data.file  )  
        try:  
            for row in reader:    # Leyendo cada ROW

                if db(db.auth_user.username == row[3]).count() == 0:
                    try:
                        
                        password = row[3]
                        
                        hash = CRYPT()(password.encode('utf8'))[0]
                        db.auth_user.insert(first_name=row[0], last_name=row[1], email=row[2], username=row[3],password=str(hash))
                        


                        context = dict(first_name=row[0],matricula=row[3])
                        message = response.render('mail.html', context)
                        mail.send(to=row[2],
                                    subject='Egresados UVM-Hmo',
                                    message=message)
                        
                    except Exception, e:
                        pass
                    
                else:
                    response.flash = 'Algunos registros duplicados no fueron insertados'
        except Exception, e:
                        redirect(URL('default','error_csv'))
    return locals()

def error_correos():
    return locals()
def error_csv():
    return locals()

@auth.requires_membership('admin')
def reportesexp_menu():
    return locals()

@auth.requires_membership('admin')
def reportes_exp():
    query = []
    if request.vars['sintitulo']:
        query = (db.egresos.titulacion == 'NO')
        titulo = 'Egresados sin Título'
        db.egresos.fecha_titulacion.readable = False
        db.egresos.tipo_titulacion.readable = False
        db.egresos.id.readable = False
        db.egresos.tiempo_encontrar_empleo.readable = False
        db.egresos.posgrado.readable = False
        db.egresos.posgrado_tipo.readable = False
        db.egresos.posgrado_institucion.readable = False
        db.egresos.posgrado_areaestudio.readable = False
        db.egresos.posgrado_fechatitulacion.readable = False

    elif request.vars['desempleados']:
        query = (db.empleos.estado_empleo == 'ACTUAL')&(db.empleos.laboralmente_activo == 'NO')
        titulo='Egresados Desempleados'
        db.empleos.id.readable=False
        db.empleos.estado_empleo.readable=False
        db.empleos.nombre_empresa.readable=False
        db.empleos.tipo_empresa.readable=False
        db.empleos.giro_empresa.readable=False
        db.empleos.empleo_relacionado.readable=False
        db.empleos.fecha_inicio.readable=False
        db.empleos.fecha_fin.readable=False
        db.empleos.telef_empresa.readable=False
        
    elif request.vars['noarea']:
        query = (db.empleos.estado_empleo == 'ACTUAL')&(db.empleos.empleo_relacionado == 'NO')&(db.empleos.laboralmente_activo == 'SI')
        titulo = 'Egresados trabajando fuera de su Área de Estudio'
        db.empleos.id.readable=False
        db.empleos.fecha_fin.readable=False

    elif request.vars['posgrado']:
        query = (db.egresos.posgrado == 'SI')
        titulo = 'Egresados con Posgrado'
        db.egresos.fecha_titulacion.readable = False
        db.egresos.tipo_titulacion.readable = False
        db.egresos.id.readable = False
        db.egresos.fecha_egreso.readable = False
        db.egresos.tiempo_encontrar_empleo.readable = False
        db.egresos.titulacion.readable = False

    #resultado_rows= join( query ).select(db.servicios.ALL, distinct=true)
    join = (db.egresos.usuario == db.auth_user.id) & (db.empleos.usuario == db.auth_user.id)&(db.banderas.usuario == db.auth_user.id)
    tabla = SQLFORM.grid(query,headers={'empleos.laboralmente_activo':'Tiene Empleo:','empleos.empleo_relacionado':'Relación Empleo c/ Estudios','egresos.titulacion':'Esta Titulado:','egresos.usuario':'Matrícula','empleos.telef_empresa':'Telefono de Empresa'}, exportclasses=dict(xml=False, html=False, csv_with_hidden_cols=False,
                             tsv_with_hidden_cols=False,tsv=False, json=False))
    return locals()

def index2():
    message = response.render('mail.html')
    mail.send(to='ruben.mu.mo@gmail.com',
                  subject='Egresados UVM-Hmo',
                  message=message, cc='cool_ruben20@hotmail.com')
    response.title=""
    if request.vars.fin:
        response.flash = '¡Muchas Gracias y Mantennos Actualizados!' 
    if request.vars.error:
        response.flash = '¡Oops, ocurrió un error!' 

    return locals()

def index():
    response.title=""
    if request.vars.fin:
        response.flash = '¡Muchas Gracias y Mantennos Actualizados!' 
    if request.vars.error:
        response.flash = '¡Oops, ocurrió un error!' 

    inicio = 'Inicie Sesión'

    if request.args(0) == 'guest':
        response.flash = 'Bienvenido Visitante // Nombre de Usuario: guest // Contraseña: guest'
        inicio = 'Inicie Sesión'

        if db(db.auth_user.username == 'guest').count() == 0:
            password = 'guest'
            hash = CRYPT()(password.encode('utf8'))[0]
            db.auth_user.insert(first_name='Visitante', last_name='Visitante', email='guest@guest.com', username='guest', password=str(hash))
        else:
            db(db.auth_user.username == 'guest').delete()
            password = 'guest'
            hash = CRYPT()(password.encode('utf8'))[0]
            db.auth_user.insert(first_name='Visitante', last_name='Visitante', email='guest@guest.com', username='guest', password=str(hash))

    if request.args(0) == 'guest_en':
        response.flash = 'Welcome Guest// Username: guest // Password: guest'
        inicio = 'Log In'
        if db(db.auth_user.username == 'guest').count() == 0:
            password = 'guest'
            hash = CRYPT()(password.encode('utf8'))[0]
            db.auth_user.insert(first_name='Visitante', last_name='Visitante', email='guest@guest.com', username='guest', password=str(hash))
        else:
            db(db.auth_user.username == 'guest').delete()
            password = 'guest'
            hash = CRYPT()(password.encode('utf8'))[0]
            db.auth_user.insert(first_name='Visitante', last_name='Visitante', email='guest@guest.com', username='guest', password=str(hash))

    if request.args(0) == 'guest_de':
        response.flash = 'Willkommen Besucher // Benutzername: guest // Passwort: guest'
        inicio = 'Anmelden'
        if db(db.auth_user.username == 'guest').count() == 0:
            password = 'guest'
            hash = CRYPT()(password.encode('utf8'))[0]
            db.auth_user.insert(first_name='Visitante', last_name='Visitante', email='guest@guest.com', username='guest', password=str(hash))
        else:
            db(db.auth_user.username == 'guest').delete()
            password = 'guest'
            hash = CRYPT()(password.encode('utf8'))[0]
            db.auth_user.insert(first_name='Visitante', last_name='Visitante', email='guest@guest.com', username='guest', password=str(hash))

    return locals()

@auth.requires_login()
def preinicio():
    try:
        row = db(db.banderas.usuario==auth.user.id).select(db.banderas.primera_completa).first()
        titulado = db(db.egresos.usuario==auth.user.id).select(db.egresos.titulacion).first()
        posgraduado = db(db.egresos.usuario==auth.user.id).select(db.egresos.posgrado, db.egresos.posgrado_tipo).first()
        empleado = db(db.empleos.usuario==auth.user.id)(db.empleos.estado_empleo=='ACTUAL').select(db.empleos.laboralmente_activo,db.empleos.nombre_empresa, orderby=~db.empleos.created_on).first()    
        if request.vars.error:
            response.flash = '¡Oops, ocurrió un error!' 
    except Exception, e:
        redirect(URL('default','index', vars={'error':'error'}))
    


    return locals()

@auth.requires_signature()
def inicio():
    anuncios = {}
    try:
        if not db(db.anuncios).isempty():
            anuncios = db(db.anuncios.pagina==1).select(db.anuncios.titulo_anuncio, db.anuncios.imagen, db.anuncios.anuncio).first()
            
    except Exception, e:
        pass
                 
    auth.settings.table_user.username.default = auth.user.username
    auth.settings.table_user.username.writable = False
    auth.settings.table_user.first_name.default = auth.user.first_name
    auth.settings.table_user.first_name.writable = False
    auth.settings.table_user.last_name.default = auth.user.last_name
    auth.settings.table_user.last_name.writable = False
    auth.settings.table_user.email.default = auth.user.email

    auth.settings.table_user.id.writable=False
    auth.settings.table_user.id.readable=False
    auth.settings.table_user.password.writable = False   
    auth.settings.table_user.password.readable = False
    auth.settings.table_user.fecha_nac.requires = IS_DATE()


    auth.settings.table_user.ciudad.requires = [IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]
    auth.settings.table_user.estado.requires = [IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]
    auth.settings.table_user.pais.requires = [IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]

    form = SQLFORM(auth.settings.table_user, record=auth.user.id, submit_button='Siguiente',labels={'email':'E-mail para contactarlo','correo_trabajo':'E-mail Laboral','correo_personal':'E-mail Personal','fecha_nac': 'Fecha de Nacimiento', 'telefono':'Telefono Fijo'})
    if form.accepts(request.vars, session):
       redirect(URL('egreso', args=[auth.user.id],user_signature=True))
    elif form.errors:
       response.flash = 'Favor de corregir el formulario'
    else:
       response.flash= 'Favor de ingresar los datos'
    return locals()
    
#dbg.set_trace() # stop here
@auth.requires_signature()
def egreso(): 
    yacompleto_egreso = db(db.egresos.usuario == auth.user.id).select().first()
    if yacompleto_egreso:
        redirect(URL('default','empleo_actual',user_signature=True))
    else:
        anuncios = {}
        try:
            if not db(db.anuncios).isempty():
                anuncios = db(db.anuncios.pagina==2).select(db.anuncios.titulo_anuncio, db.anuncios.imagen, db.anuncios.anuncio).first()
                
        except Exception, e:
            pass
        
        db.egresos.usuario.default = auth.user.id
        db.egresos.usuario.readable = False
        db.egresos.usuario.writable = False

        form = SQLFORM(db.egresos, submit_button='Siguiente',labels={'tiempo_encontrar_empleo':'Seleccione un lapso de tiempo','carrera': 'Carrera Cursada', 'fecha_egreso':'Año de Egreso','titulacion': 'Realizó Titulación','fecha_titulacion': 'Año en que se tituló','tipo_titulacion': 'Forma en que se tituló','posgrado_tipo':'Nivel de Posgrado','posgrado_institucion':'Institución (posgrado)','posgrado_areaestudio':'Area de Estudio (posgrado)','posgrado_fechatitulacion':'Año de titulación (posgrado)'})

        if form.accepts(request.vars, session):
           redirect(URL('empleo_actual',user_signature=True))
        elif form.errors:
           response.flash = 'Favor de corregir el formulario'
        else:
            response.flash= 'Favor de ingresar los datos'

    
    return locals()

@auth.requires_signature()
def empleo_actual():
    yacompleto_empleoactual = db(db.banderas.usuario==auth.user.id).select(db.banderas.primera_completa).first()
    if yacompleto_empleoactual:
        if yacompleto_empleoactual['primera_completa'] == True:
            redirect(URL('default','decision',user_signature=True))
        else:
            anuncios = {}
            try:
                if not db(db.anuncios).isempty():
                    anuncios = db(db.anuncios.pagina==3).select(db.anuncios.titulo_anuncio, db.anuncios.imagen, db.anuncios.anuncio).first()
                    
            except Exception, e:
                pass
            
            db.empleos.usuario.default = auth.user.id
            db.empleos.estado_empleo.default='ACTUAL'
            db.empleos.estado_empleo.readable=False
            db.empleos.estado_empleo.writable=False

            

            db.empleos.usuario.readable = False
            db.empleos.usuario.writable = False
            db.empleos.fecha_fin.readable = False
            db.empleos.fecha_fin.writable = False

            
            form = SQLFORM(db.empleos, submit_button='Siguiente',labels={'laboralmente_activo': 'Cuenta actualmente con un Empleo', 'nombre_empresa':'Nombre de la Empresa','tipo_empresa': 'Tipo de Empresa','giro_empresa': 'Giro de la Empresa','fecha_inicio': 'Fecha en la que comenzó a trabajar','telef_empresa': 'Telefono de la Empresa','empleo_relacionado':'Tiene relación tu empleo con tus estudios?'})
            if form.accepts(request.vars, session):
               db.banderas.insert(usuario=auth.user.id, primera_completa=True)
               redirect(URL('decision', args=[form.vars.laboralmente_activo],user_signature=True))
            elif form.errors:
               response.flash = 'Favor de corregir el formulario'
            else:
               response.flash='Favor de ingresar los datos'

    else:
        anuncios = {}
        try:
            if not db(db.anuncios).isempty():
                anuncios = db(db.anuncios.pagina==3).select(db.anuncios.titulo_anuncio, db.anuncios.imagen, db.anuncios.anuncio).first()
                
        except Exception, e:
            pass
        
        db.empleos.usuario.default = auth.user.id
        db.empleos.estado_empleo.default='ACTUAL'
        db.empleos.estado_empleo.readable=False
        db.empleos.estado_empleo.writable=False
        

        db.empleos.usuario.readable = False
        db.empleos.usuario.writable = False
        db.empleos.fecha_fin.readable = False
        db.empleos.fecha_fin.writable = False

        
        form = SQLFORM(db.empleos, submit_button='Siguiente',labels={'laboralmente_activo': 'Cuenta actualmente con un Empleo', 'nombre_empresa':'Nombre de la Empresa','tipo_empresa': 'Tipo de Empresa','giro_empresa': 'Giro de la Empresa','fecha_inicio': 'Fecha en la que comenzó a trabajar','telef_empresa': 'Telefono de la Empresa','empleo_relacionado':'Tiene relación tu empleo con tus estudios?'})
        if form.accepts(request.vars, session):
           db.banderas.insert(usuario=auth.user.id, primera_completa=True)
           redirect(URL('decision', args=[form.vars.laboralmente_activo],user_signature=True))
        elif form.errors:
           response.flash = 'Favor de corregir el formulario'
        else:
           response.flash='Favor de ingresar los datos'
    return locals()

@auth.requires_signature()
def decision():
    return locals() 

def fechas_correctas(form):
    #dbg.set_trace() # stop here!

    #fecha_ini=datetime.datetime.strptime(form.vars.fecha_inicio,'%d/%m/%Y').date()
    #fecha_fin=datetime.datetime.strptime(form.vars.fecha_fin,'%d/%m/%Y').date()
    fecha_fin = form.vars.fecha_fin
    fecha_ini = form.vars.fecha_inicio
    now = datetime.date.today()
    if fecha_fin < fecha_ini or fecha_fin > now:
       form.errors.fecha_fin= 'Debe ser posterior a Fecha de Inicio y no mayor a la fecha de hoy'
    else:
       form.vars.fecha_fin=form.vars.fecha_fin


@auth.requires_signature()
def masempleos():    
    db.empleos.usuario.default = auth.user.id 
    db.empleos.usuario.readable = False
    db.empleos.usuario.writable = False


    empleado = db(db.empleos.usuario==auth.user.id)(db.empleos.estado_empleo=='ACTUAL').select(db.empleos.laboralmente_activo,orderby=~db.empleos.created_on).first()

    db.empleos.laboralmente_activo.default = 'SI'
    db.empleos.laboralmente_activo.readable = False
    db.empleos.laboralmente_activo.writable = False

    db.empleos.estado_empleo.default='ANTERIOR'
    db.empleos.estado_empleo.readable=False
    db.empleos.estado_empleo.writable=False
    db.empleos.fecha_inicio.requires=IS_DATE()
    db.empleos.fecha_fin.requires=IS_DATE()
    db.empleos.nombre_empresa.requires = [IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]
    

    form = SQLFORM(db.empleos, submit_button='Siguiente',labels={'laboralmente_activo': 'Cuenta actualmente con un Empleo', 'nombre_empresa':'Nombre de la Empresa','tipo_empresa': 'Tipo de Empresa','giro_empresa': 'Giro de la Empresa','fecha_inicio': 'Fecha en la que comenzó a trabajar','telef_empresa': 'Telefono de la Empresa','fecha_fin': 'Fecha de Término','empleo_relacionado':'Tiene relación tu empleo con tus estudios?'})
    if form.process(onvalidation=fechas_correctas).accepted:
       redirect(URL('decision',vars={'otro_empleo':'otro_empleo'},user_signature=True))
    else:
        response.flash= 'Favor de ingresar los datos'

       
    
    return locals()
    
@auth.requires_signature()
def actualizar():
    auth.settings.table_user.username.default = auth.user.username
    auth.settings.table_user.username.writable = False
    auth.settings.table_user.first_name.default = auth.user.first_name
    auth.settings.table_user.first_name.writable = False
    auth.settings.table_user.last_name.default = auth.user.last_name
    auth.settings.table_user.last_name.writable = False
    auth.settings.table_user.email.default = auth.user.email

    auth.settings.table_user.id.writable=False
    auth.settings.table_user.id.readable=False
    auth.settings.table_user.password.writable = False   
    auth.settings.table_user.password.readable = False    

    form = SQLFORM(auth.settings.table_user, record=auth.user.id, submit_button='Guardar Cambios (Datos Personales)',labels={'email':'E-mail para contactarlo','correo_trabajo':'E-mail Laboral','correo_personal':'E-mail Personal','fecha_nac': 'Fecha de Nacimiento', 'telefono':'Telefono Fijo'})
    if form.accepts(request.vars, session):
       response.flash='Los cambios se han guardado (Datos Personales)'
    elif form.errors:
       response.flash = 'Favor de corregir el formulario'
    

    
    #db.egresos.usuario.default = auth.user.username
    db.egresos.usuario.readable = False
    db.egresos.usuario.writable = False
    db.egresos.id.readable = False
    db.egresos.id.writable = False

    tesis = db(db.tipos_titulacion.tipos=='TESIS').select(db.tipos_empresa.id).first().id

    record = db.egresos(db.egresos.usuario== auth.user.id)
    #record=db()
    form2 = SQLFORM(db.egresos, record=record.id, submit_button='Guardar Cambios (Datos Egreso)',labels={'tiempo_encontrar_empleo':'Seleccione un lapso de tiempo','carrera': 'Carrera Cursada', 'fecha_egreso':'Año de Egreso','titulacion': 'Realizó Titulación','fecha_titulacion': 'Año en que se tituló','tipo_titulacion': 'Forma en que se tituló','posgrado_tipo':'Nivel de Posgrado','posgrado_institucion':'Institución (posgrado)','posgrado_areaestudio':'Area de Estudio (posgrado)','posgrado_fechatitulacion':'Año de titulación (posgrado)'})
    if form2.accepts(request.vars, session):
       response.flash='Los cambios se han guardado (Datos Egreso)'
    elif form2.errors:
       response.flash = 'Favor de corregir el formulario'
    
    return locals()





@auth.requires_signature()
def actualizar_empleo():
    empleado = db(db.empleos.usuario==auth.user.id)(db.empleos.estado_empleo=='ACTUAL').select(db.empleos.id,db.empleos.laboralmente_activo,db.empleos.nombre_empresa,orderby=~db.empleos.created_on).first()
    
    if empleado: ## haber si existe, 98% pq no hay registro 'ACTUAL'
        if empleado['laboralmente_activo'] == 'SI': #ya estabas empleado, dar finalizacion a ese empleo y se actualizarta con ANTERIOR para posteriormente crear uno nuevo ACTUAL
            
            db.empleos.usuario.readable = False
            db.empleos.usuario.writable = False
            db.empleos.id.readable = False
            db.empleos.id.writable = False
            db.empleos.laboralmente_activo.default='SI'
            db.empleos.laboralmente_activo.readable = False
            db.empleos.laboralmente_activo.writable = False

            #db.empleos.estado_empleo.default='ANTERIOR'
            db.empleos.estado_empleo.readable = True
            db.empleos.estado_empleo.writable = False
            db.empleos.nombre_empresa.writable = False
            db.empleos.tipo_empresa.writable = False
            db.empleos.giro_empresa.writable = False
            db.empleos.fecha_inicio.writable = False
            db.empleos.telef_empresa.writable = False
            db.empleos.empleo_relacionado.writable = False
            db.empleos.empleo_relacionado.readable = True

            now = datetime.date.today()
            empleoaconcluir =db(db.empleos.usuario== auth.user.id)(db.empleos.estado_empleo=='ACTUAL').select(db.empleos.fecha_inicio,orderby=~db.empleos.created_on).first()

            db.empleos.fecha_fin.requires=IS_DATE_IN_RANGE(format=T('%Y-%m-%d'),
                   minimum=empleoaconcluir.fecha_inicio,
                   maximum=now,
                   error_message='Debe ser posterior a la Fecha de Inicio y no mayor a la fecha de hoy')
            
            
            empleadoid = db(db.empleos.usuario==auth.user.id)(db.empleos.estado_empleo=='ACTUAL').select(db.empleos.id,orderby=~db.empleos.created_on).first()
            eid=empleadoid.id
            
            form = SQLFORM(db.empleos, record=eid, submit_button='Guardar Cambios / Ir a Nuevo Empleo',labels={'laboralmente_activo': 'Cuenta actualmente con un Empleo', 'nombre_empresa':'Nombre de la Empresa','tipo_empresa': 'Tipo de Empresa','giro_empresa': 'Giro de la Empresa','fecha_inicio': 'Fecha en la que comenzó a trabajar','telef_empresa': 'Telefono de la Empresa','fecha_fin': 'Fecha de Término','empleo_relacionado':'Tiene relación tu empleo con tus estudios?'})
            if form.accepts(request.vars, session):
                db(db.empleos.id==eid).update(estado_empleo='ANTERIOR')
                redirect(URL('nuevo_registro_menu',user_signature=True))
            elif form.errors:
               response.flash = 'Favor de corregir el formulario'
        

        else:##estaba desempleado, se hara un update en laboralmenteactivo(de F a T), se llenan los datos del empleo y se mantiene el edo. ACTUAl
        ## si solo tiene un registro- actual desempleado - y para validar la fecha de inicio (va y busca su ultimo trabajo orderby fechafin,) pero no hay datos en fecha fin .. en min marcaria error
            
            db.empleos.usuario.readable = False
            db.empleos.usuario.writable = False
            db.empleos.id.readable = False
            db.empleos.id.writable = False
            #db.empleos.laboralmente_activo.default=True
            db.empleos.laboralmente_activo.readable = False
            db.empleos.laboralmente_activo.writable = False

            #db.empleos.estado_empleo.default='ACTUAL'
            db.empleos.estado_empleo.readable = False
            db.empleos.estado_empleo.writable = False

            db.empleos.fecha_fin.readable = False
            db.empleos.fecha_fin.writable = False
            now = datetime.date.today()
            

            ultimoempleo =db(db.empleos.usuario== auth.user.id)(db.empleos.estado_empleo=='ANTERIOR').select(orderby=~db.empleos.fecha_fin).first()
            
            if ultimoempleo is None: ##quiere decir que es su primer empleo(no hay anterior)
                db.empleos.nombre_empresa.requires=[IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]
                db.empleos.fecha_inicio.requires=IS_DATE_IN_RANGE(format=T('%Y-%m-%d'),
                       minimum=datetime.date(1914,1,1),
                       maximum=now,
                       error_message='No debe ser posterior a la fecha de hoy')
            else:#ya tenia empleo antes de estar desempleada, fecha min de inicio de este empleo debe ser mayor o igual a cuando termino su empleo anterior
                db.empleos.nombre_empresa.requires=[IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]
                db.empleos.fecha_inicio.requires=IS_DATE_IN_RANGE(format=T('%Y-%m-%d'),
                       minimum=ultimoempleo.fecha_fin,
                       maximum=now,
                       error_message='Debe ser posterior a la finalización de su empleo anterior ('+str(ultimoempleo.fecha_fin)+') y no mayor a la fecha de hoy')

            empleadoid = db(db.empleos.usuario==auth.user.id)(db.empleos.estado_empleo=='ACTUAL').select(db.empleos.id,orderby=~db.empleos.created_on).first()
            eid=empleadoid.id
            
            form2 = SQLFORM(db.empleos, record=eid, submit_button='Guardar Cambios',labels={'laboralmente_activo': 'Cuenta actualmente con un Empleo', 'nombre_empresa':'Nombre de la Empresa','tipo_empresa': 'Tipo de Empresa','giro_empresa': 'Giro de la Empresa','fecha_inicio': 'Fecha en la que comenzó a trabajar','telef_empresa': 'Telefono de la Empresa','empleo_relacionado':'Tiene relación tu empleo con tus estudios?'})
            if form2.accepts(request.vars, session):
                db(db.empleos.id==eid).update(laboralmente_activo='SI')
                redirect(URL('preinicio',user_signature=True))
            elif form2.errors:
               response.flash = 'Favor de corregir el formulario'
    else:#entonces creamos uno actual
        redirect(URL('default','nuevo_registro_menu', user_signature=True))           
    

    return locals()


@auth.requires_signature()
def nuevo_registro_menu():
    empleado = db(db.empleos.usuario==auth.user.id)(db.empleos.estado_empleo=='ACTUAL').select(db.empleos.laboralmente_activo,db.empleos.nombre_empresa,orderby=~db.empleos.created_on).first()

    if empleado: ###  ya existe un registro ACTUAL, t deveuelve a preinicio, pa q sobre el actual q ya existe, actualices
        redirect(URL('preinicio',user_signature=True))
    
    return locals()

@auth.requires_signature()
def post_nr_menu_actualdesempleado():
    db.empleos.insert(usuario=auth.user.id,laboralmente_activo='NO',estado_empleo='ACTUAL')
    redirect(URL('default','preinicio'))
    return locals()



@auth.requires_signature()
def nuevo_empleo():
    ultimoempleo =db(db.empleos.usuario== auth.user.id)(db.empleos.estado_empleo=='ANTERIOR').select(orderby=~db.empleos.fecha_fin).first()

    db.empleos.usuario.default = auth.user.id
    db.empleos.estado_empleo.default='ACTUAL'
    db.empleos.estado_empleo.readable=False
    db.empleos.estado_empleo.writable=False

    db.empleos.laboralmente_activo.default='SI'
    db.empleos.laboralmente_activo.readable=False
    db.empleos.laboralmente_activo.writable=False
    db.empleos.nombre_empresa.requires=[IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]

    db.empleos.usuario.readable = False
    db.empleos.usuario.writable = False
    db.empleos.fecha_fin.readable = False
    db.empleos.fecha_fin.writable = False

    now = datetime.date.today()
    if ultimoempleo is None: ##quiere decir que es su primer empleo(no hay anterior)
        db.empleos.nombre_empresa.requires=[IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]
        db.empleos.fecha_inicio.requires=IS_DATE_IN_RANGE(format=T('%Y-%m-%d'),
               minimum=datetime.date(1914,1,1),
               maximum=now,
               error_message='No debe ser posterior a la fecha de hoy')
    else:#ya tenia empleo, fecha min de inicio de este empleo debe ser mayor o igual a cuando termino su empleo anterior
        db.empleos.nombre_empresa.requires=[IS_NOT_EMPTY(error_message='No puede quedar vacío'),IS_UPPER()]
        db.empleos.fecha_inicio.requires=IS_DATE_IN_RANGE(format=T('%Y-%m-%d'),
               minimum=ultimoempleo.fecha_fin,
               maximum=now,
               error_message='Debe ser posterior a la finalización de su empleo anterior ('+str(ultimoempleo.fecha_fin)+') y no mayor a la fecha de hoy')

    form = SQLFORM(db.empleos, submit_button='Siguiente',labels={'laboralmente_activo': 'Cuenta actualmente con un Empleo', 'nombre_empresa':'Nombre de la Empresa','tipo_empresa': 'Tipo de Empresa','giro_empresa': 'Giro de la Empresa','fecha_inicio': 'Fecha en la que comenzó a trabajar','telef_empresa': 'Telefono de la Empresa'})
    if form.accepts(request.vars, session):
       redirect(URL('preinicio',user_signature=True))
    elif form.errors:
       response.flash = 'Favor de corregir el formulario'
    
    return locals()

@service.json
def tabla_ajax():
    
    """ this gets passed a few URL arguments: page number, and rows per page, and sort column, and sort desc or asc
    """
    #db.licencias.sistema_libranza.represent = lambda v: v.name
    #try:
        
    fields = ['first_name','last_name','email','username','fecha_nac','telefono','celular','direccion','ciudad','estado','pais','carrera','fecha_egreso','titulacion','fecha_titulacion','tipo_titulacion','posgrado','posgrado_tipo','posgrado_institucion','posgrado_areaestudio','posgrado_fechatitulacion','tiempo_encontrar_empleo','laboralmente_activo','nombre_empresa','tipo_empresa','giro_empresa','fecha_inicio','telef_empresa']
    rows = []
    page = int(request.vars.page)  #the page number
    pagesize = int(request.vars.rows)        

    
    limitby = (page*pagesize - pagesize,page*pagesize)
    orderby = db.auth_user[request.vars.sidx]
    if request.vars.sord == 'desc':
        orderby = ~orderby
    
    #variables = request.vars
    # variables=[]
    # variables_low=[]
    # for var in request.vars:
    #     variables_low.append(var)
    #     variables.append(request.vars[var])

    #variables_low.append(var.values())
    queries = []
    #queries_puntas = []
    lista_egresados = ['fecha_egreso','titulacion','fecha_titulacion','tipo_titulacion','posgrado','posgrado_tipo','posgrado_institucion','posgrado_areaestudio','posgrado_fechatitulacion','tiempo_encontrar_empleo']
    lista_empleados = ['laboralmente_activo','nombre_empresa','tipo_empresa','giro_empresa','fecha_inicio','telef_empresa']
    #dbg.set_trace() # stop here
    if request.vars["_search"] == "true":
        filtros_str = request.vars['filters']
        filtro = eval( filtros_str )
        
        for dato in filtro['rules']:
            
            if dato['op'] == 'eq':
                if dato['field'] in lista_egresados:
                    queries.append(  db.egresos[dato['field']] == dato['data'] ) 
                elif dato['field'] in lista_empleados:
                    queries.append(  db.empleos[dato['field']] == dato['data'] ) 
                elif dato['field'] == 'carrera': 
                    queries.append(  db.carreras['nombre_carrera'] == dato['data'] )              
                else:
                    queries.append( db.auth_user[dato['field']] == dato['data'] )

            elif dato['op'] == 'ne': 
                if dato['field'] in lista_empleados:
                    queries.append(  db.empleos[dato['field']] != dato['data'] )
                elif dato['field'] in lista_egresados:
                    queries.append( db.egresos[dato['field']] != dato['data'] )
                else:
                    queries.append( db.auth_user[dato['field']] != dato['data'] )

            elif dato['op'] == 'ge':
                if dato['field'] in lista_egresados:
                    queries.append(  db.egresos[dato['field']] >= dato['data'] ) 
                elif dato['field'] in lista_empleados:
                    queries.append(  db.empleos[dato['field']] >= dato['data'] )               
                else:
                    queries.append( db.auth_user[dato['field']] >= dato['data'] )

            elif dato['op'] == 'le':
                if dato['field'] in lista_egresados:
                    queries.append(  db.egresos[dato['field']] <= dato['data'] ) 
                elif dato['field'] in lista_empleados:
                    queries.append(  db.empleos[dato['field']] <= dato['data'] )               
                else:
                    queries.append( db.auth_user[dato['field']] <= dato['data'] )

            elif dato['op'] == 'gt':
                if dato['field'] in lista_egresados:
                    queries.append(  db.egresos[dato['field']] > dato['data'] ) 
                elif dato['field'] in lista_empleados:
                    queries.append(  db.empleos[dato['field']] > dato['data'] )               
                else:
                    queries.append( db.auth_user[dato['field']] > dato['data'] )

            elif dato['op'] == 'lt':
                if dato['field'] in lista_egresados:
                    queries.append(  db.egresos[dato['field']] < dato['data'] ) 
                elif dato['field'] in lista_empleados:
                    queries.append(  db.empleos[dato['field']] < dato['data'] )               
                else:
                    queries.append( db.auth_user[dato['field']] < dato['data'] )

            elif dato['op'] == 'cn': #op de string
                 if dato['field'] in lista_egresados:
                    if dato['field'] == "tipo_titulacion":
                        queries.append( db.tipos_titulacion['tipos'].contains(dato['data']) )
                    elif dato['field'] == "posgrado_tipo":
                        queries.append( db.tipos_posgrado['tipos'].contains(dato['data']) )
                    else:
                        queries.append(  db.egresos[dato['field']].contains(dato['data']) )
                 elif dato['field'] in lista_empleados:
                    if dato['field'] == "tipo_empresa":
                        queries.append( db.tipos_empresa['tipos'].contains(dato['data']) )
                    elif dato['field'] == "giro_empresa":
                        queries.append( db.giros_empresa['giros'].contains(dato['data']) )
                    else:
                        queries.append(  db.empleos[dato['field']].contains(dato['data']) )
                 elif dato['field'] == 'carrera': 
                    queries.append(  db.carreras['nombre_carrera'].contains(dato['data']) )
                 else:
                     queries.append(db.auth_user[ dato['field'] ].contains( dato['data'] ))

            elif dato['op'] == 'nc': #op de string
                if dato['field'] in lista_egresados:
                    if dato['field'] == "tipo_titulacion":
                        queries.append( ~db.tipos_titulacion['tipos'].contains(dato['data']) )
                    elif dato['field'] == "posgrado_tipo":
                        queries.append( ~db.tipos_posgrado['tipos'].contains(dato['data']) )
                    else:
                        queries.append(  ~db.egresos[dato['field']].contains(dato['data']) )
                elif dato['field'] in lista_empleados:
                    if dato['field'] == "tipo_empresa":
                        queries.append( ~db.tipos_empresa['tipos'].contains(dato['data']) )
                    elif dato['field'] == "giro_empresa":
                        queries.append( ~db.giros_empresa['giros'].contains(dato['data']) )
                    else:
                        queries.append(  ~db.empleos[dato['field']].contains(dato['data']) )
                elif dato['field'] == 'carrera': 
                    queries.append(  ~db.carreras['nombre_carrera'].contains(dato['data']) )
                else:
                     queries.append(~db.auth_user[ dato['field'] ].contains( dato['data'] ))
            
        # try:
        #     query_puntas = reduce(lambda a,b:(a|b),queries_puntas)
        # except Exception, e:
        #     query_puntas = (db.presupuestos.id == db.presupuestos.id)
        try:
            query = reduce(lambda a,b:(a&b),queries)
        except Exception, e:
            query = (db.auth_user.id == db.auth_user.id)
    else:
        query = (db.auth_user.id == db.auth_user.id)
        #query_puntas = query
    
    join = (db.egresos.usuario == db.auth_user.id) & (db.empleos.usuario == db.auth_user.id)&(db.banderas.usuario == db.auth_user.id)&(db.egresos.carrera == db.carreras.id)&(db.egresos.tipo_titulacion == db.tipos_titulacion.id)&(db.egresos.posgrado_tipo == db.tipos_posgrado.id)&(db.empleos.tipo_empresa == db.tipos_empresa.id)&(db.empleos.giro_empresa == db.giros_empresa.id)
    #for r in db(query_puntas)(query)(join).select(db.auth_user.ALL, limitby=limitby,orderby=orderby, distinct=True):
    for r in db(join)(query)(db.banderas.primera_completa==True)(db.empleos.estado_empleo=='ACTUAL').select(db.auth_user.ALL, limitby=limitby,orderby=orderby, distinct=True):
        vals = []
        #ident = r['id']

        #lleno_info=db(db.banderas.usuario==r.id).select().first()
        egre=db(db.egresos.usuario == r.id).select().first()
        emple=db(db.empleos.usuario == r.id)(db.empleos.estado_empleo=='ACTUAL').select(orderby=~db.empleos.created_on).first()
        
        for f in fields:
            if f in lista_egresados:
                if f == 'tipo_titulacion':
                    vals.append(egre.tipo_titulacion.tipos)
                elif f == 'tiempo_encontrar_empleo':
                    vals.append(egre.tiempo_encontrar_empleo.tiempos)
                elif f == 'posgrado_tipo':
                    vals.append(egre.posgrado_tipo.tipos)
                else:
                    vals.append(egre[f])
            elif f in lista_empleados:
                if f == 'tipo_empresa':
                    vals.append(emple.tipo_empresa.tipos)
                elif f == 'giro_empresa':
                    vals.append(emple.giro_empresa.giros)
                else:
                    vals.append(emple[f])
            elif f == 'carrera':
                vals.append(egre.carrera.nombre_carrera)
            #elif f == 'editar':
             #   vals.append( A(SPAN(_class='icon icon-file'),T("Historial"), _href=URL('plugin_servicios','presupuestos_adjuntos', args=[ident],user_signature=True), _class='btn btn-mini btn-primary', _target="_blank") +A(SPAN(_class="icon-edit"),T("Edicion"), _href=URL('plugin_servicios','presupuesto_editar', args=[ident], user_signature=True),_TARGET="blank", _class='btn btn-mini btn-warning', _style='margin-top: 0em') )
            else:
                vals.append(r[f])
        rows.append(dict(id=r.id,cell=vals))
    
    total = db(db.auth_user.id>0).count()
    pages = math.ceil(1.0*total/pagesize)
    data = dict(total=pages,page=page,rows=rows)
    # dbg.set_trace()
    return data
    ##except Exception, e:
      ##  redirect(URL('default','error'))

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    if request.args(0) == 'profile':
        db.auth_user.first_name.writable = False
        db.auth_user.last_name.writable = False
        db.auth_user.username.writable = False
    return dict(form=auth())

@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()


@auth.requires_signature()
def data():
    """
    http://..../[app]/default/data/tables
    http://..../[app]/default/data/create/[table]
    http://..../[app]/default/data/read/[table]/[id]
    http://..../[app]/default/data/update/[table]/[id]
    http://..../[app]/default/data/delete/[table]/[id]
    http://..../[app]/default/data/select/[table]
    http://..../[app]/default/data/search/[table]
    but URLs must be signed, i.e. linked with
      A('table',_href=URL('data/tables',user_signature=True))
    or with the signed load operator
      LOAD('default','data.load',args='tables',ajax=True,user_signature=True)
    """
    return dict(form=crud())
