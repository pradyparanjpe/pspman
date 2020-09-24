prefix=/home/pradyumna
all:
	@cp pspman/gitman $(prefix)/bin
	@mkdir -p /home/pradyumna/.local/share/man/man1
	@cp pspman.1 /home/pradyumna/.local/share/man/man1/
clean:
	rm $(prefix)/bin/gitman
	rm /home/pradyumna/.local/share/man/man1/pspman.1
install:
	@true
