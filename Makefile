morse/coreaudio.so: morse/coreaudio.pyx morse/setup.py
	cd morse; \
	CFLAGS="-framework CoreAudio" python setup.py build_ext --inplace; \
	rm -rf build

clean:
	rm -f morse/*.c morse/*.pyc morse/*.so *.pyc
