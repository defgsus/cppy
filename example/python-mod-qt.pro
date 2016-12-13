#-------------------------------------------------
#
# Project created by QtCreator 2016-12-10T09:31:40
#
#-------------------------------------------------

QT       += core

QT       -= gui

TARGET = python-mod
CONFIG   += console c++11
CONFIG   -= app_bundle

TEMPLATE = app

LIBS += -lpython3.4m

HEADERS += \
    py_utils.h \
    example.h \

SOURCES += \
    py_utils.cpp \
    example.cpp \
    main.cpp

