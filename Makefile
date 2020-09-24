prefix=
all:
	@cp pspman/gitman $(prefix)/bin
clean:
	rm $(prefix)/bin/gitman
install:
	@true
