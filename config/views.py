from contextlib import redirect_stderr
from email.policy import HTTP
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
import hashlib
from django.core.paginator import Paginator
from article.models import *
def index(request):
  # m = hashlib.sha256()
  # m.update(b"testtest")
  # print( m.hexdigest() )
  # s = '37268335dd6931045bdcdf92623ff819a64244b53d0e746d438797349d4da578'
  # print( len(s) )
  return render(request, 'index.html')

from django.http import HttpResponseRedirect
from article.models import User

def signup(request):
  if request.method == 'POST':
    # 회원정보 저장
    email = request.POST.get('email')
    name = request.POST.get('name')
    pwd = request.POST.get('pwd')
    user = User(email=email, name=name, pwd=pwd)
    user.save()
    return HttpResponseRedirect('/index/')

  return render(request, 'signup.html')

def signin(request):
  if request.method == 'POST':
    # 회원정보 조회
    email = request.POST.get('email')
    pwd = request.POST.get('pwd')
    
    try:
      # select * from user where email=? and pwd=?
      user = User.objects.get(email=email, pwd=pwd)
      request.session['email'] = email
      return render(request, 'signin_success.html')
    except:
      return render(request, 'signin_fail.html')

  return render(request, 'signin.html')

def signout(request):
  del request.session['email']  # 개별 삭제
  request.session.flush()  # 전체 삭제

  return HttpResponseRedirect('/index/')

def download(request):
  id = request.GET.get('id')
  file_attc = FileAttach.objects.get(id = id)
  
  filename = file_attc.save_filename
  with open('c:/django/%s'%filename ,'rb') as f:
    res = HttpResponse(
      f,
      content_type = 'application/octet-stream',
      # content_disposition='attachment; filename = %s' %filename
    )
    res['content-Disposition'] = 'attachment; filename = %s' %filename
  return res

from article.models import Article
import os, time
def upload(request):
  if request.method == 'POST':
    file = request.FILES.getlist('abc')
    if len(file)==0:
      pass
    for f in file:
      name = f.name
      size = f.size
      save_name = name
      # 실제저장소에 이미 같은 이름이 있는지 확인후 처리과정
      if os.path.isfile('c:/django/%s' %save_name):
        ext = save_name[save_name.rfind('.'):]
        n = save_name[:save_name.rfind('.')]
        save_name = '%s_%s%s' %(n, time.time(), ext)
      # 파일 실제 저장소에 저장하는과정
      with open('c:/django/%s' %save_name, 'wb') as u_file:
        for chunk in f.chunks():
          u_file.write(chunk)
      # 데이터베이스에 반영하는 과정
      File(save_filename = save_name, o_filename = name, filesize = size).save()
    # 포스트로 파일 받아서 파일 변수에 담기
    # 파일 명/ 파일 사이즈 변수에 담기
    # 파일 정해둔 경로에 저장하기
    # 데이터베이스에 반영시키기()
    # 데이터베이스에 담고/실제파일을 실제로 저장하는건 업무입장에서는 한번에 일어나는 일이지만
    # 코드입장에서는 두개의 코드로 독립적으로 일어나는것
    # 만약에 코드하나는 잘작동했지만, 하나가 작동이 잘못된다면?
    # 혼선이생기고 일치하지 않는경우가 생길수 있음
    # 그래서 둘중에 하나가 실패하면 같이 실패할수 있게 만든다던가
    # 둘다 성공해야만 반영되게끔 만들게 해줘야한다
    # 트랜잭션이라고 한다.
    # 업무입장에서는 한번에 일어나지만
    # 코드입장에서는 몇개로 분할해서 일어나는 일인지 코드작성 전에 쪼개고 분석해볼 필요가 있다
    return HttpResponse('hi')
  return render(request, 'upload.html')
  
    

def write(request):
  if request.method == 'POST':
    title = request.POST.get('title')
    content = request.POST.get('content')
    files = request.FILES.getlist('file')
    try:
      email = request.session['email']
      # select * from user where email = ?
      user = User.objects.get(email=email)
      # insert into article (title, content, user_id) values (?, ?, ?)
      article = Article(title=title, content=content, user=user)
      article.save()

      if len(files)==0:
        pass
      for f in files:
        name = f.name
        size = f.size
        save_name = name
        # 실제저장소에 이미 같은 이름이 있는지 확인후 처리과정
        if os.path.isfile('c:/django/%s' %save_name):
          ext = save_name[save_name.rfind('.'):]
          n = save_name[:save_name.rfind('.')]
          save_name = '%s_%s%s' %(n, time.time(), ext)
        # 파일 실제 저장소에 저장하는과정
        with open('c:/django/%s' %save_name, 'wb') as u_file:
          for chunk in f.chunks():
            u_file.write(chunk)
        # 데이터베이스에 반영하는 과정
        FileAttach(save_filename = save_name, o_filename = name, filesize = size, article=article).save()
      return redirect('/article/list/')
    except:
      return render(request, 'write_fail.html')

  return render(request, 'write.html')




def list(request):
  # select * from article order by id desc
  article_list = Article.objects.order_by('-id')
  p= Paginator(article_list,10)
  page = request.GET.get('page')

  try:
    article_list = p.page(page)
  except:
    page = 1
    article_list = p.page(page)
  start_page = (int(page)-1)//10*10 +1
  end_page = start_page+9
  if p.num_pages < end_page:
    end_page = p.num_pages
  context = {
    'page_info' : range(start_page, end_page+1), 
    'article_list' : article_list 
  }
  return render(request, 'list.html', context)

def detail(request, id):
  # select * from article where id = ?
  article = Article.objects.get(id=id)
  context = { 
    'article' : article 
  }
  return render(request, 'detail.html', context)

def update(request, id):
  # select * from article where id = ?
  article = Article.objects.get(id=id)

  if request.method == 'POST':
    title = request.POST.get('title')
    content = request.POST.get('content')
    
    try:
      # update article set title = ?, content = ? where id = ?
      article.title = title
      article.content = content
      article.save()
      return render(request, 'update_success.html')
    except:
      return render(request, 'update_fail.html')

  context = { 
    'article' : article 
  }
  return render(request, 'update.html', context)

def delete(request, id):
  try:
    # select * from article where id = ?
    name = request.session['name']
    article = Article.objects.get(id=id)
    if article.user.name ==name:
      article.delete()
    else:
      return HttpResponse('''
      <script>
        alert('작성자만 삭제할 수 있습니다.');
        location = "/article/detail/%s/";
        </script>
      '''%article.id)
    return render(request, 'delete_success.html')
  except:
    return render(request, 'delete_fail.html')

def map(request):
  return render(request, 'map.html')

from django.http import JsonResponse  # JSON 응답
from map.models import Point
from django.forms.models import model_to_dict

def map_data2(request):
  lat = request.GET.get('lat')
  lng = request.GET.get('lng')

  data = Point.objects.raw('''
    SELECT *,
       (6371 * acos(
         cos(radians(%s))
         * cos(radians(lat))
         * cos(radians(lng) - radians(%s))
         + sin(radians(%s))
         * sin(radians(lat)))) AS distance
     FROM map_point
    HAVING distance <= %s
    ORDER BY distance''' % (lat, lng, lat, 10))
  map_list = []
  for d in data:
    d = model_to_dict(d)  # QuerySet -> Dict
    map_list.append(d)
  # dict가 아닌 자료는 항상 safe=False 옵션 사용
  return JsonResponse(map_list, safe=False)

def map_data(request):
  data = Point.objects.all()
  lat = request.GET.get('lat')
  lng = request.GET.get('lng')
  map_list = []
  for d in data:
    d = model_to_dict(d)  # QuerySet -> Dict
    dist = distance(float(lat), float(lng), d['lat'], d['lng'])
    if(dist <= 100):  # 100km 이내의 장소만 응답결과로 저장
      map_list.append(d)
  # dict가 아닌 자료는 항상 safe=False 옵션 사용
  return JsonResponse(map_list, safe=False)

import math
def distance(lat1, lng1, lat2, lng2)  :
  theta = lng1 - lng2
  dist1 = math.sin(deg2rad(lat1)) * math.sin(deg2rad(lat2))

  dist2 = math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) 
  dist2 = dist2* math.cos(deg2rad(theta))

  dist = dist1 + dist2

  dist = math.acos(dist)
  dist = rad2deg(dist) * 60 * 1.1515 * 1.609344

  return dist

def deg2rad(deg):
  return deg * math.pi / 180.0

def rad2deg(rad):
  return rad * 180.0 / math.pi

def contact(request):
  if request.method == 'POST':
    email = request.POST.get('email')
    comment = request.POST.get('comment')
    #         발신자주소, 수신자주소, 메시지
    send_mail('ggoreb.kim@gmail.com', email, comment)
    return render(request, 'contact_success.html')

  return render(request, 'contact.html')

import smtplib
from email.mime.text import MIMEText
 
def send_mail(from_email, to_email, msg):
  # SMTP 설정
  smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  # 인증정보 설정
  smtp.login(from_email, 'hwojjkbwhtxxmxdg')
  msg = MIMEText(msg)
  # 제목
  msg['Subject'] = '[문의사항]' + to_email
  # 수신 이메일
  msg['To'] = from_email
  smtp.sendmail(from_email, from_email, msg.as_string())
  smtp.quit()
