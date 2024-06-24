#include<algorithm>
#include<iostream>

class LamportClock {
private: 
    int time;

public:
    LamportClock() : time(0) {}

    void increment() {
        ++time;
    }

    void update(int receivedTime) {
        time = std::max(time, receivedTime) + 1;
    }

    int getTime() const {
        return time;
    }
};