#pragma once


#include "sthread.h"

typedef void (*handler_t) (void *); 

struct Task {
    handler_t handler;
    void* arg;
};

/*
 * ------------------------------------------------------------------
 * TaskQueue --
 * 
 *      A thread-safe task queue. This queue should be implemented
 *      as a monitor.
 *
 * ------------------------------------------------------------------
 */
class TaskQueue {
    private:
    // TODO: More needed here.

    public:
    TaskQueue();
    ~TaskQueue();

    void enqueue(Task task);
    Task dequeue();

    int size();
    bool empty();
};

