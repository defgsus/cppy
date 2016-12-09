CXX=g++
CPPFLAGS=-g -pthread -std=c++11 -O2 -Wall
LDFLAGS=-g
LDLIBS=-lpython3.4m

.PHONY: test clean

python-mod: example.cpp main.o py_utils.o example.o
	$(CXX) $(LDFLAGS) -o python-mod main.o py_utils.o example.o $(LDLIBS)

main.o: main.cpp
	$(CXX) $(CPPFLAGS) -c main.cpp

py_utils.o: py_utils.cpp py_utils.h
	$(CXX) $(CPPFLAGS) -c py_utils.cpp

example.o: example.cpp example.h
	$(CXX) $(CPPFLAGS) -c example.cpp

example.cpp: example.py
	python3 ../cppy.py -i example.py

test:
	./python-mod tests.py

clean:
	rm -f python-mod
	rm -f *.o
	rm -f example.cpp
	rm -f example.h
	rm -fr __pycache__
