"""
Django settings for ProjectShow project.

Generated by 'django-admin startproject' using Django 2.0.7.

For more information on this file, see
https://docs.djangoproject.com/en/2.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.0/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '&#p0#emjyh)pcyyk$bf3cl_-2#a8*z7brn^un(y_o(lj0q7)uo'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
LANGUAGE_CODE = 'zh-hans'
ALLOWED_HOSTS = ["39.108.183.209", "www.strivexj.com", "strivexj.com", "127.0.0.1", "*", ]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'bootstrap3',


    'blog',
    'contact',
    'home',
    'project',
    'account',
    'article',
    'timetable',
    'rest_framework'
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ProjectShow.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        # 'DIRS': [os.path.join(BASE_DIR, 'templates'), ],
        'DIRS': [os.path.join(BASE_DIR, "templates").replace('\\', '/')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
            ],
        },
    },
]

WSGI_APPLICATION = 'ProjectShow.wsgi.application'

# Database
# https://docs.djangoproject.com/en/2.0/ref/settings/#databases

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',  # 加载驱动
#         'NAME': 'ProjectShow',  # 数据库名
#         'USER': 'root',  # mysql的用户名
#         'PASSWORD': 'pwh19990228',  # mysql的密码
#         'HOST': 'localhost',  # 连接地址（本地的话使用localhost或者127.0.0.1）
#         'PORT': 3306  # 数据库服务的端口号
#     }
# }
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',  # 数据库引擎
        'NAME': 'ProjectShow',  # 数据库名，先前创建的
        'USER': 'root',  # 用户名，可以自己创建用户
        'PASSWORD': 'pwh19990228',  # 密码
        'HOST': 'localhost',  # mysql服务所在的主机ip
        'PORT': '3306',  # mysql服务端口
    }
}

# Password validation
# https://docs.djangoproject.com/en/2.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/2.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.0/howto/static-files/

STATIC_URL = '/static/'
HERE = os.path.dirname(os.path.abspath(__file__))
HERE = os.path.join(HERE, '../')

LOGIN_URL = '/account/login/'
BOOTSTRAP3 = {
    'include_jquery': True,
}

# email setting
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'strivexj@gmail.com'
EMAIL_HOST_PASSWORD = 'keepstriving'
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

# EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
# EMAIL_HOST = 'smtp.qq.com'
# EMAIL_PORT = 25
# EMAIL_HOST_USER = '1003214597@qq.com'
# EMAIL_HOST_PASSWORD = 'wtutawjxewghbgaf'
# EMAIL_USE_TLS = True  # 这里必须是 True，否则发送不成功
# EMAIL_FROM = "1003214597@qq.com"
# DEFAULT_FROM_EMAIL = "1003214597@qq.com"

SITE_ID = 1

REDIS_HOST = 'localhost'
REDIS_PORT = 6379
REDIS_DB = 0

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(HERE, 'static/'),
    os.path.join(BASE_DIR, 'media/'),
)

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')  # 设置静态文件路径为主目录下的media文件夹
MEDIA_URL = 'ProjectShow/media/'
