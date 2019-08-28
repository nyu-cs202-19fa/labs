TARGET_EXEC ?= ls
SRCS := $(shell find . -name *.c)
OBJS := $(SRCS:%=%.o)
CFLAGS ?= -ansi -pedantic -Wall -std=c11 -g -D_POSIX_C_SOURCE=200112L

%.c.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

$(TARGET_EXEC): $(OBJS)
	$(CC) $(OBJS) -o $@ $(LDFLAGS)

.PHONY: clean format

clean:
	$(RM) $(TARGET_EXEC) $(OBJS)


