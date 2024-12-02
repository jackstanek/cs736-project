#include <cstdint>
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <format>
#include <string> 
#include <memory>
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
        file << std::get<2>(point).get_hit_rate() << std::get<0>(point) << " " << std::get<1>(point) << std::get<2>(point) << std::endl;
    }

    file.close();
}

void initializeNewClientInGhost(int client, std::unordered_map<int, std::unique_ptr<gcache::SampledGhostKvCache<>>>& clientsGhostMap) {
    clientsGhostMap[client] = std::make_unique<gcache::SampledGhostKvCache<5>>(1024*64,1024*64,1024*1024);
}

int main() {
    std::ifstream file("./data/cluster012");
    csv::CSVReader reader(file);

    std::unordered_map<int, std::unique_ptr<gcache::SampledGhostKvCache<>>> clientsGhostMap;

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

            if(clientsGhostMap.find(req.client) == clientsGhostMap.end()) {
                initializeNewClientInGhost(req.client, clientsGhostMap);
            }

            clientsGhostMap[req.client]->access(req.key, req.keySize + req.valSize);
        }
    }

    file.close();

    for (auto& kv : clientsGhostMap) {
        auto curve = kv.second->get_cache_stat_curve();
        saveMRCToFile(curve, std::to_string(kv.first));
    }

    return 0;
}