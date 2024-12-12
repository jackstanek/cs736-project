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

// Time interval for MRC sampling
#define TIME_DELTA 10
// Cache configuration
#define MIN_CACHE (64)
#define MAX_CACHE (1024)
#define CACHE_STEP 64
#define SAMPLE 5

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
        file << std::get<2>(point).get_hit_rate() << " " << std::get<0>(point) << " " << std::get<1>(point) << " " << std::get<2>(point) << std::endl;
    }

    file.close();
}

void initializeNewClientInGhost(int client, std::unordered_map<int, std::unique_ptr<gcache::SampledGhostKvCache<SAMPLE>>>& clientsGhostMap) {
    clientsGhostMap[client] = std::make_unique<gcache::SampledGhostKvCache<SAMPLE>>(CACHE_STEP,MIN_CACHE,MAX_CACHE);
}

int main() {
    std::ifstream file("./data/cluster012");
    csv::CSVReader reader(file);

    std::unordered_map<int, std::unique_ptr<gcache::SampledGhostKvCache<SAMPLE>>> clientsGhostMap;

    int saveTs = 0;

    for (csv::CSVRow& row : reader) {

        if (row[0].is_int() && row[2].is_int() && row[3].is_int() && row[4].is_int()) {

            TraceReq req;
            req.key = row[1].get<std::string>();
            req.operation = row[5].get<std::string>();
            req.timeStamp = row[0].get<int>();
            req.keySize = row[2].get<int>();
            req.valSize = row[3].get<int>();
            req.client = row[4].get<int>() % 32;

            // Save the MRC curves for each client with a certain time interval
            if(req.timeStamp - saveTs > TIME_DELTA) {
                saveTs = (req.timeStamp / TIME_DELTA) * TIME_DELTA;
                std::cout << "TS " << saveTs << std::endl;
                for (auto& kv : clientsGhostMap) {
                    auto curve = kv.second->get_cache_stat_curve();
                    saveMRCToFile(curve, std::format("{}_{}", std::to_string(kv.first), std::to_string(saveTs)));
                }
            }

            // printTraceReq(req);

            if(clientsGhostMap.find(req.client) == clientsGhostMap.end()) {
                initializeNewClientInGhost(req.client, clientsGhostMap);
            }
            clientsGhostMap[req.client]->access(req.key, req.keySize + req.valSize);
        }
    }

    file.close();

    return 0;
}
