#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include "lib/csv.hpp"

struct TraceReq {
    int timeStamp;
    std::string key;
    int keySize;
    int valSize;
    int client;
    std::string operation;
};

void printTraceReq(TraceReq trace) {
    std::cout << trace.timeStamp << " : " <<
                 trace.key << " : " <<
                 trace.keySize << " : " <<
                 trace.valSize << " : " <<
                 trace.client << " : " <<
                 trace.operation << " : " << std::endl;
}

int main() {
    std::ifstream file("./data/cluster015");

    csv::CSVReader reader(file);

    for (csv::CSVRow& row : reader) {
        if (row[0].is_int() && row[2].is_int() && row[3].is_int() && row[4].is_int()) {
            TraceReq req;
            req.key = row[1].get<std::string>();
            req.operation = row[5].get<std::string>();
                
            req.timeStamp = row[0].get<int>();
            req.keySize = row[2].get<int>();
            req.valSize = row[3].get<int>();
            req.client = row[4].get<int>();

            printTraceReq(req);
        }
    }

    file.close();

    return 0;
}