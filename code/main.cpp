#include <cstdint>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <format>
#include <csv.hpp>
#include <gcache/ghost_kv_cache.h>

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

void saveMRCToFile(std::vector<std::tuple<uint32_t, uint32_t, gcache::CacheStat>> curve, std::string name) {
    std::ofstream file(std::format("mrc/{}.txt", name));

    for (auto& point : curve) {
        file << std::get<0>(point) << " " << std::get<1>(point) << std::get<2>(point) << std::endl;
    }

    file.close();
}

int main() {
    std::ifstream file("./data/cluster012");

    csv::CSVReader reader(file);

    gcache::SampledGhostKvCache<5> ghost(1024*64, 1024*64, 1024*1024);

    for (csv::CSVRow& row : reader) {
        if (row[0].is_int() && row[2].is_int() && row[3].is_int() && row[4].is_int()) {
            TraceReq req;
            req.key = row[1].get<std::string>();
            req.operation = row[5].get<std::string>();

            req.timeStamp = row[0].get<int>();
            req.keySize = row[2].get<int>();
            req.valSize = row[3].get<int>();
            req.client = row[4].get<int>();

            // printTraceReq(req);

            ghost.access(req.key, req.keySize + req.valSize);
        }
    }

    file.close();

    auto curve = ghost.get_cache_stat_curve();

    saveMRCToFile(curve, "mrc");

    return 0;
}