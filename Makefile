CC=gcc
CFLAGS=-Wall -O3 -I/usr/local/opt/openssl@3/include
LDFLAGS=-L/usr/local/opt/openssl@3/lib -lcrypto -lpthread

all: key_search

key_search: key_search.c
	$(CC) $(CFLAGS) -o $@ $< $(LDFLAGS)

clean:
	rm -f key_search 